#!/usr/bin/env python

from datetime import datetime, timedelta
import json
import subprocess
from sys import argv, stdin
import requests
from pathlib import Path

from forms import forms, groups, _P, _C


base = Path(__file__).resolve().parent

# load posts.json which stores the posts already uploaded


def load_posts():
    try:
        with open("posts.json", "r") as file:
            posts = json.load(file)
    except FileNotFoundError:
        posts = {}
    return posts


def save_posts(posts):
    with open("posts.json.tmp", "w") as file:
        json.dump(posts, file, indent=2)
    Path("posts.json.tmp").replace("posts.json")


posts = load_posts()


def run_resize():
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


def get_data(label_or_group, count):
    label = None

    # normal recurring event
    if label_or_group in forms:
        form = forms[label_or_group]

        # count date forward to "today + count"
        dates = form["date"]
        date = next(dates)
        for i in range(int(count)):
            date = next(dates)
        label = label_or_group

    # group of events
    elif label_or_group in groups:
        dates = {k: forms[k]["date"] for k in groups[label_or_group]}
        dates_next = {k: next(dates[k]) for k in dates}
        date = None
        for i in range(int(count) + 1):
            k_next = min(dates_next, key=dates_next.get)
            date = dates_next[k_next]
            try:
                dates_next[k_next] = next(dates[k_next])
            except StopIteration:
                # this label has no more dates, remove it
                del dates_next[k_next]
            form = forms[k_next]
            label = k_next

    data = {
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
    return (data, label)


def run_post(label_or_group, count):
    (data, label) = get_data(label_or_group, count)
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
    print("\n\nPlease press enter to post...")
    stdin.readline()

    # post with cookie, my posts didn't arrive on the page previously
    s = requests.Session()
    # allow sending request to debug server
    # s.verify = base.joinpath("debug_cert.pem")
    s.get(endpoint).raise_for_status()
    # browser client sends data as content-disposition
    # response = s.post(endpoint, headers=headers, files={**data, **files})
    response = s.post(endpoint, headers=headers, data=data, files=files)
    response.raise_for_status()
    print(response.headers)
    with open("log.html", "w") as f:
        f.write(response.text)


def run_inject(label_or_group, count):
    (data, _) = get_data(label_or_group, count)

    script = ""
    for k, v in data.items():
        script += """document.querySelector('[name="{:}"]').value = `{:}`;
""".format(
            k, v
        )

    subprocess.run(["wl-copy", script])


def run_debugserve():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from time import time
    from threading import Thread
    import os
    import ssl

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
        # openssl req -x509 -newkey rsa:4096 -keyout debug_key.pem -out debug_cert.pem -nodes \
        #   -days 1 -subj "/C=DE/CN=www.hueckelhoven.de/O=adabru" -addext "subjectAltName = DNS:www.hueckelhoven.de"
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            base.joinpath("debug_cert.pem"),
            keyfile=base.joinpath("debug_key.pem"),
        )
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
elif len(argv) == 4 and argv[1] == "post" and argv[2] in {**forms, **groups}:
    label = argv[2]
    count = argv[3]
    run_post(label, count)
elif len(argv) == 4 and argv[1] == "inject" and argv[2] in {**forms, **groups}:
    label = argv[2]
    count = argv[3]
    run_inject(label, count)
elif len(argv) == 2 and argv[1] == "debugserve":
    try:
        run_debugserve()
    except subprocess.CalledProcessError:
        pass
else:
    print(
        "usage:\n\n  fill_form.py (inject | post ) (event | group) <0-9>\n\n  fill_form.py resize\n  fill_form.py debugserve\n\ngroups: {:}\nevents: {:}\n\n".format(
            ", ".join(groups.keys()), ", ".join(forms.keys())
        )
    )


# update sudo credential cache
# subprocess.run("sudo -v".split(" "), check=True)
# forward traffic from 80 to 8080
# pSocat = subprocess.Popen(
#     "sudo -n socat TCP4-LISTEN:80,fork,su=nobody TCP4:{:}:8080".format(ip).split(
#         " "
#     ),
#     stdin=subprocess.PIPE,
#     stdout=subprocess.PIPE,
# )
# point endpoint to localhost
# subprocess.run(
#     "sudo sed -i -E s/#(.*www.hueckelhoven.de)/\1/ /etc/hosts".split(" "),
#     check=True,
# )
