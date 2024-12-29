#!/usr/bin/env python

import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from sys import argv, stdin

import requests
from db import load_db, save_db
from forms import _C, _P, forms, groups

base = Path(__file__).resolve().parent

# load posts.json which stores the posts already uploaded


posts = load_db("posts")


def run_resize() -> None:
    # prepare images and exit
    for dir in base.joinpath("images").iterdir():
        if dir.is_dir():
            for i in range(1, 6):
                image = dir.joinpath("{:}.jpg".format(i))
                target = dir.joinpath("small", image.name)
                if image.is_file() and (
                    not target.is_file()
                    or image.stat().st_mtime > target.stat().st_mtime
                ):
                    print(image)
                    dir.joinpath("small").mkdir(exist_ok=True)
                    subprocess.run(
                        "convert {:} -resize 1500x1500> -quality 75 {:}".format(
                            image, target
                        ).split(" ")
                    )


class AlreadyPostedException(Exception):
    """Thrown if the next event for the specified label was already posted."""

    pass


def get_next_event(label_or_group: str) -> tuple[dict, str, datetime]:
    """
    Get next event to schedule. Already posted events are skipped (posts.json).

    Args:
        label_or_group: For events, the label of the event. For groups, the label of the group. The next event of the group is returned.
    """

    def get_next_unpublished_date(label, publishing_offset=3) -> datetime:
        """
        Get next unpublished date for event "label". Raises AlreadyPostedException if event was already posted.
        The publishing_offset is used to skip events that are too close to the current date.
        """
        # add new dictionary if event is new
        if label not in posts:
            posts[label] = {}

        dates = forms[label]["date"]
        now = datetime.now()
        # skip events that are too close to the current date, also making following events earlier visible
        date = next(dates)
        while date < now + timedelta(days=publishing_offset):
            date = next(dates)
        if date.isoformat() in posts[label]:
            raise AlreadyPostedException("Event on {:} already posted.".format(date))
        return date

    # normal recurring event
    if label_or_group in forms:
        label = label_or_group
        date = get_next_unpublished_date(label)

    # group of events
    elif label_or_group in groups:
        group = label_or_group
        # get next event for every label in the group
        dates = {}
        error_message = ""
        for k in groups[group]:
            try:
                dates[k] = get_next_unpublished_date(k)
            except AlreadyPostedException as e:
                error_message += str(e) + "\n"
            except StopIteration:
                pass
        if not dates:
            raise AlreadyPostedException(
                "All events in group {:} already posted or none left.\n{:}".format(
                    group, error_message
                )
            )
        # get next event
        label = min(dates, key=dates.get)
        date = dates[label]

    form = forms[label]

    event = {
        "customer_event_title": form["title"],
        "customer_event_date_day": date.day,
        "customer_event_date_month": date.month,
        "customer_event_date_year": date.year,
        "customer_event_date_time": date.strftime("%H:%M"),
        "customer_event_date_day_2": (date + form["duration"]).day,
        "customer_event_date_month_2": (date + form["duration"]).month,
        "customer_event_date_year_2": (date + form["duration"]).year,
        "customer_event_date_time_2": (date + form["duration"]).strftime("%H:%M"),
        "customer_event_category": form["category"],
        "customer_event_place": form["place"],
        "customer_event_place_2": form["address"],
        "customer_event_description": form["description"],
        "customer_name": "Adam Brunnmeier",
        "customer_email": "adam.brunnmeier@gmail.com",
        "customer_adress": "017645737586\nRheinstraße 42\n41836 Hückelhoven",
        "customer_datenschutz": "1",
        "customer_datenschutz2": "1",
    }
    return (event, label, date)


def run_post(label_or_group: str) -> None:
    try:
        (data, label, date) = get_next_event(label_or_group)
    except AlreadyPostedException as e:
        print(e)
        return

    data["submit-customer-event"] = "1"

    # add some headers, just to be safe
    headers = {
        "Origin": "https://www.hueckelhoven.de",
        "Referer": "https://www.hueckelhoven.de/termineingabe/",
    }

    files = {}
    for i in range(1, 6):
        image = base.joinpath("images", label, "small/{:}.jpg".format(i))
        name = "customer_event_image{:}".format(i)
        if image.is_file():
            files[name] = (image.name, open(image, "rb"), "image/jpeg")
        else:
            files[name] = ("", "", "application/octet-stream")
    files["customer_event_file"] = ("", "", "application/octet-stream")

    endpoint = "https://www.hueckelhoven.de/termineingabe/"

    def reverse_lookup(dict: dict, what):
        return next(key for key, value in dict.items() if value == what)

    print(
        "{:}-{:}-{:}   {:}-{:}".format(
            data["customer_event_date_year"],
            data["customer_event_date_month"],
            data["customer_event_date_day"],
            data["customer_event_date_time"],
            data["customer_event_date_time_2"],
        )
    )
    print(
        "({:}) Hückelhoven-{:}, {:}".format(
            reverse_lookup(_C, data["customer_event_category"]),
            reverse_lookup(_P, data["customer_event_place"]),
            data["customer_event_place_2"],
        )
    )
    print("\033[1m{:}\033[22m".format(data["customer_event_title"]))
    print(data["customer_event_description"])
    print()
    print(files["customer_event_image1"])
    print(files["customer_event_image2"])
    print(files["customer_event_image3"])
    print(files["customer_event_image4"])
    print(files["customer_event_image5"])
    print(
        "\n\nPlease type a message to skip this event or leave empty to upload it.\nYour message: ",
        end="",
    )
    try:
        message = stdin.readline().strip()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return

    # add post to posts.json
    if message == "":
        posts[label][date.isoformat()] = "posted on " + datetime.now().isoformat()
        save_db("posts", posts)
    else:
        posts[label][date.isoformat()] = "skipped: " + message
        save_db("posts", posts)
        print("skipped")
        return

    # post with cookie, my posts didn't arrive on the page previously
    s = requests.Session()

    # allow sending request to debug server
    # s.verify = base.joinpath("debug_cert.pem")

    s.get(endpoint).raise_for_status()

    # browser client sends data as content-disposition
    response = s.post(endpoint, headers=headers, data=data, files=files)
    response.raise_for_status()
    print(response.headers)
    with open("log.html", "w") as f:
        f.write(response.text)


def run_inject(label_or_group, count):
    (data, _) = get_next_event(label_or_group, count)

    script = ""
    for k, v in data.items():
        script += """document.querySelector('[name="{:}"]').value = `{:}`;
""".format(
            k, v
        )

    subprocess.run(["wl-copy", script])


def run_debugserve():
    import os
    import ssl
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from threading import Thread
    from time import time

    if os.geteuid() != 0:
        print("Run as root (serve on port 80, edit /etc/hosts). Exiting.")
        exit()

    class LogServer(BaseHTTPRequestHandler):
        def do_GET(self):
            # feed cookie
            self.send_response(200)
            self.send_header("Set-Cookie", "DEBUG")
            self.end_headers()

        def do_POST(self):
            head = "{:}\n{:}".format(
                self.requestline,
                self.headers,
            )
            length = int(self.headers["Content-Length"])
            body = self.rfile.read(length)
            base.joinpath("log").mkdir(exist_ok=True)
            with open(base.joinpath("log", str(time())), "wb") as f:
                f.write(head.encode())
                f.write(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write("Request received.".encode())

    ip = "127.0.0.45"
    with open("/etc/hosts") as f:
        hosts = f.read()
    # redirect www.hueckelhoven.de to localhost
    hosts = hosts.replace("#" + ip, ip)
    with open("/etc/hosts", "w") as f:
        f.write(hosts)

    with HTTPServer((ip, 443), LogServer) as httpd:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            context.load_cert_chain(
                base.joinpath("debug_cert.pem"),
                keyfile=base.joinpath("debug_key.pem"),
            )
        except FileNotFoundError:
            print("No debug certificate found. Run command\n")
            print(
                'openssl req -x509 -newkey rsa:4096 -keyout debug_key.pem -out debug_cert.pem -nodes -days 1 -subj "/C=DE/CN=www.hueckelhoven.de/O=adabru" -addext "subjectAltName = DNS:www.hueckelhoven.de"'
            )
            print("\nExiting.")
            exit()
        httpd.socket = context.wrap_socket(
            httpd.socket,
            server_side=True,
        )
        print("serving at {:}".format(ip))
        t = Thread(target=httpd.serve_forever)
        t.start()
        print("press enter to exit...")
        input()
        httpd.shutdown()
        with open("/etc/hosts", "w") as f:
            # remove redirection
            hosts = hosts.replace(ip, "#" + ip)
            f.write(hosts)


if len(argv) == 2 and argv[1] == "resize":
    run_resize()
elif len(argv) == 3 and argv[1] == "post" and argv[2] in {**forms, **groups}:
    label = argv[2]
    run_post(label)
elif len(argv) == 3 and argv[1] == "inject" and argv[2] in {**forms, **groups}:
    label = argv[2]
    run_inject(label)
elif len(argv) == 2 and argv[1] == "scrape":
    from scraper import run_scrape

    run_scrape()
elif len(argv) == 2 and argv[1] == "debugserve":
    try:
        run_debugserve()
    except subprocess.CalledProcessError:
        pass
else:
    print(
        "usage:\n\n  fill_form.py (inject | post ) (event | group)\n\n  fill_form.py resize\n  fill_form.py debugserve\n\ngroups: {:}\nevents: {:}\n\n".format(
            ", ".join(groups.keys()), ", ".join(forms.keys())
        )
    )
