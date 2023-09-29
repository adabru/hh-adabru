#!/usr/bin/env python

from datetime import datetime, timedelta
import subprocess
from sys import argv


forms = {
    "silke": {
        "title": "Offener Nähtreff",
        "date": datetime.fromisoformat("2023-08-28T14:30:00"),
        "duration": timedelta(hours=3),
        "category": "Kultur",
        "place": "Hückelhoven",
        "address": "Friedrichplatz 7",
        "description": """Interkultureller Nähtreff mit Kinderbetreuung. Im Vordergrund steht die gemeinsame Freude am Nähen und das offene Gespräch miteinander. NähanfängerInnen sind genauso willkommen wie Fortgeschrittene. Die Kinder werden während der Kurszeit betreut.

Jeden Montag von 14:30 Uhr bis 17:30 Uhr im Begegnungszentrum, Leitung Silke Löwenkamp.""",
    },
    "ela": {
        "title": "Offener Näh- und Handarbeitstreff",
        "date": datetime.fromisoformat("2023-08-29T10:00:00"),
        "duration": timedelta(hours=3),
        "category": "Kultur",
        "place": "Hückelhoven",
        "address": "Rheinstraße 103",
        "description": """Offener Näh- und Handarbeitstreff für Jung und Alt. Im Vordergrund steht die gemeinsame Freude am Nähen, Häkeln und Stricken. Anfänger/innen sind genauso willkommen wie Fortgeschrittene. Es wird für den guten Zweck oder an privaten Projekten gearbeitet. Schau gerne mal vorbei!

Jeden Dienstag von 10 Uhr bis 13 Uhr im DRK Hückelhoven.""",
    },
}

if not (len(argv) == 2 and argv[1] == "resize" or len(argv) == 3 and argv[1] in forms):
    print(
        "usage:\n\n  fill_form.py ({:}) <0-9>\n\n  fill_form.py resize\n".format(
            " | ".join(forms.keys())
        )
    )
    exit()
if argv[1] == "resize":
    # prepare images and exit
    from pathlib import Path

    base = Path("~/repo/hh-adabru/ads").expanduser()
    for dir in base.iterdir():
        if dir.is_dir():
            for image in dir.iterdir():
                if image.is_file():
                    print(image)
                    dir.joinpath("300kb").mkdir(exist_ok=True)
                    subprocess.run(
                        "convert {:} -define jpeg:extent=300kb {:}".format(
                            image, dir.joinpath("300kb", image.name)
                        ).split(" ")
                    )
    exit()

label = argv[1]
form = forms[label]
count = argv[2]


# count date forward to "today + count"
date = form["date"]
while date < datetime.now():
    date += timedelta(weeks=1)
for i in range(int(count)):
    date += timedelta(weeks=1)

script = """
document.querySelector('[name="customer_event_title"]').value = `{:}`
document.querySelector('[name="customer_event_date_day"]').value = `{:}`
document.querySelector('[name="customer_event_date_month"]').value = `{:}`
document.querySelector('[name="customer_event_date_year"]').value = `{:}`
document.querySelector('[name="customer_event_date_time"]').value = `{:}`
document.querySelector('[name="customer_event_date_day_2"]').value = `{:}`
document.querySelector('[name="customer_event_date_month_2"]').value = `{:}`
document.querySelector('[name="customer_event_date_year_2"]').value = `{:}`
document.querySelector('[name="customer_event_date_time_2"]').value = `{:}`
Array.from(document.querySelector('[name="customer_event_category"]').options).find(el => el.text == `{:}`).selected = true
Array.from(document.querySelector('[name="customer_event_place"]').options).find(el => el.text == `{:}`).selected = true
document.querySelector('[name="customer_event_place_2"]').value = `{:}`
document.querySelector('[name="customer_event_description"]').value = `{:}`
document.querySelector('[name="customer_name"]').value = `{:}`
document.querySelector('[name="customer_email"]').value = `{:}`
document.querySelector('[name="customer_adress"]').value = `{:}`
document.querySelector('[name="customer_datenschutz"]').checked = true
document.querySelector('[name="customer_datenschutz2"]').checked = true
""".format(
    form["title"],
    date.day,
    date.month,
    date.year,
    date.strftime("%H:%M"),
    (date + form["duration"]).day,
    (date + form["duration"]).month,
    (date + form["duration"]).year,
    (date + form["duration"]).strftime("%H:%M"),
    form["category"],
    form["place"],
    form["address"],
    form["description"],
    "Adam Brunnmeier",
    "adam.brunnmeier@gmail.com",
    "017645737586\nRheinstraße 42\n41836 Hückelhoven",
)

subprocess.run(["wl-copy", script])

# print("Filling in in 3 seconds...")
# subprocess.run(["wtype", "\t".join(forms[label])])
