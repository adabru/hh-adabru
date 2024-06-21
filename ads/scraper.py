from pathlib import Path
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from urllib.parse import urljoin, urlparse
import json
import re
import requests
from typing import List

from db import load_db, save_db
from forms import _C, _P

# mkdir scrapes/images
base = Path(__file__).resolve().parent
image_cache_dir = base.joinpath("scrapes/images")
image_cache_dir.mkdir(exist_ok=True, parents=True)

scrapes = load_db("scrapes")


def run_scrape():
    scrape_ekir()


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def escape_image_url(url: str) -> str:
    return url.replace("/", "_").replace(":", "_")


def download_image(url: str) -> str:
    filename = escape_image_url(url)
    filepath = image_cache_dir.joinpath(filename)
    if not filepath.exists():
        print(f"Downloading image from {url}")
        response = requests.get(url)
        with open(filepath, "wb") as file:
            file.write(response.content)


def download_and_rename_images(images: List[str]) -> None:
    for i, url in enumerate(images):
        download_image(url)
        images[i] = escape_image_url(url)


def scrape_ekir():
    if "ekir_messe" not in scrapes:
        scrapes["ekir_messe"] = {}
    base_url = "https://termine.ekir.de"

    def remap(key: str) -> str:
        return {
            "Gottesdienste": "Messe",
            "Hückelhoven-Hilfarth": "Hilfarth",
        }.get(key, key)

    url = urljoin(base_url, "/veranstaltungen?vid=206")
    soup = get_soup(url)
    events = soup.find_all("div", class_="et_content_row")
    for i, event in enumerate(events, start=1):
        try:
            print(f"Scraping event {i}/{len(events)}")
            sleep(0.2)
            # Find the link to the event detail page
            link = event.find("a")
            if link and link.get("href"):
                # Join the base URL with the relative URL of the event detail page
                event_url = urljoin(base_url, link.get("href"))
                scrape_key = urlparse(event_url).path
                if scrape_key in scrapes["ekir_messe"]:
                    print(f"Event already scraped: {scrape_key}")
                    continue

                event_soup = get_soup(event_url)
                script = event_soup.find("script", type="application/ld+json")
                data = json.loads(script.string)
                title = data["name"]
                date = datetime.fromisoformat(data["startDate"])
                category = (
                    event_soup.find(
                        "div",
                        class_="et_content_detaillabel",
                        text="Art der Veranstaltung",
                    )
                    .find_next_sibling("div", class_="et_content_detailvalue")
                    .get_text(strip=True)
                )

                place = data["location"]["address"]["addressLocality"]
                address = data["location"]["address"]["streetAddress"]
                description = title
                images = [
                    urljoin(base_url, img["src"])
                    for img in event_soup.find_all("img")
                    if "/Upload/" in img["src"] and img["src"].endswith(".png")
                ]
                if place == "Erkelenz" or place == "Heinsberg":
                    print(f"skipping event {title} in {place}")
                    continue
                download_and_rename_images(images)
                event_scrape = {
                    "title": title,
                    "date": date.isoformat(),
                    "duration": None,
                    "category": _C[remap(category)],
                    "place": _P[remap(place)],
                    "address": address,
                    "description": description,
                    "images": images,
                    "url": event_url,
                }
                scrapes["ekir_messe"][scrape_key] = event_scrape
        except KeyError as e:
            traceback.print_exc()
            print(f"Data: {data}")
            print(f"Event URL: {event_url}")
            print(f"Event scrape: {event_scrape}")
            # stop scraping if an error occurs for me to inspect the error
            break
    print("Scraping done")
    save_db("scrapes", scrapes)
