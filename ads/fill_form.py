#!/usr/bin/env python

from datetime import datetime, timedelta
import subprocess
from sys import argv, stdin
import requests
from pathlib import Path

#  JSON.stringify( [...$0.options].reduce((a, x) => {a[x.innerText]=x.value; return a}, {}) )
_C = {
    "Messe": "2077",
    "Sitzungen": "89",
    "Tag der offenen Tür": "653",
    "verkaufsoffene Sonntage": "260",
    "Bildung": "78",
    "Kindergarten": "657",
    "Veranstaltungen der Gleichstellungsbeauftragten": "261",
    "Kino": "565",
    "Jam Session": "650",
    "Lesung": "1924",
    "Termin": "90",
    "Offenes Singen": "254",
    "Feiern": "74",
    "Sport": "76",
    "Comedy/Kabarett": "258",
    "Kultur": "77",
    "Traditionelle Veranstaltungen": "259",
    "Theater": "257",
    "Ausstellungen": "256",
    "Events": "75",
    "Märkte": "73",
    "Sonstiges": "255",
    "Konzert": "253",
    "Highlight": "138",
}
_P = {
    "Altmyhl": "190",
    "Schaufenberg": "200",
    "Kleingladbach": "196",
    "Doveren": "193",
    "Millich": "197",
    "Rurich": "199",
    "Brachelen": "192",
    "Baal": "191",
    "Hilfarth": "194",
    "Ratheim": "198",
    "Hückelhoven": "195",
}

forms = {
    "silke": {
        "title": "Offener Nähtreff",
        "date": datetime.fromisoformat("2023-08-28T14:30:00"),
        "duration": timedelta(hours=3),
        "category": _C["Kultur"],
        "place": _P["Hückelhoven"],
        "address": "Friedrichplatz 7",
        "description": """Interkultureller Nähtreff mit Kinderbetreuung. Im Vordergrund steht die gemeinsame Freude am Nähen und das offene Gespräch miteinander. NähanfängerInnen sind genauso willkommen wie Fortgeschrittene. Die Kinder werden während der Kurszeit betreut.

Jeden Montag von 14:30 Uhr bis 17:30 Uhr im Begegnungszentrum.
Leitung Silke Löwenkamp, famkrack{:} .""".format(
            "@googlemail.com"
        ),
    },
    "ela": {
        "title": "Offener Näh- und Handarbeitstreff",
        "date": datetime.fromisoformat("2023-08-29T10:00:00"),
        "duration": timedelta(hours=3),
        "category": _C["Kultur"],
        "place": _P["Hückelhoven"],
        "address": "Rheinstraße 103",
        "description": """Offener Näh- und Handarbeitstreff für Jung und Alt. Im Vordergrund steht die gemeinsame Freude am Nähen, Häkeln und Stricken. Anfänger/innen sind genauso willkommen wie Fortgeschrittene. Es wird für den guten Zweck oder an privaten Projekten gearbeitet. Schau gerne mal vorbei!

Jeden Dienstag von 10 Uhr bis 13 Uhr im DRK Hückelhoven.

Kontakt: Manuela Backes, 0176 {:}.""".format(
            "81416805"
        ),
    },
}


base = Path(__file__).resolve().parent


def run_resize():
    # prepare images and exit
    for dir in base.iterdir():
        if dir.is_dir():
            for i in range(1, 6):
                image = dir.joinpath("{:}.jpg".format(i))
                if image.is_file():
                    print(image)
                    dir.joinpath("small").mkdir(exist_ok=True)
                    subprocess.run(
                        "convert {:} -resize 1500x1500> -quality 75 {:}".format(
                            image, dir.joinpath("small", image.name)
                        ).split(" ")
                    )


def get_data(label, count):
    form = forms[label]

    # count date forward to "today + count"
    date = form["date"]
    while date < datetime.now():
        date += timedelta(weeks=1)
    for i in range(int(count)):
        date += timedelta(weeks=1)

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
    return data


def run_post(label, count):
    data = get_data(label, count)
    data["submit-customer-event"] = "1"

    headers = {
        "Content-Type": "multipart/form-data",
    }

    files = {}
    for i in range(1, 6):
        image = base.joinpath(label, "small/{:}.jpg".format(i))
        if image.is_file():
            files["customer_event_image{:}".format(i)] = open(image, "rb")

    endpoint = "https://www.hueckelhoven.de/termineingabe/"

    print(
        "{:}-{:}-{:}   {:}-{:}".format(
            data["customer_event_date_year"],
            data["customer_event_date_month"],
            data["customer_event_date_day"],
            data["customer_event_date_time"],
            data["customer_event_date_time_2"],
        )
    )
    print(data["customer_event_description"])
    print("\n\nPlease press enter to post...")
    stdin.readline()
    response = requests.post(endpoint, headers=headers, data=data, files=files)
    print(response)


def run_inject(label, count):
    data = get_data(label, count)

    script = ""
    for k, v in data.items():
        script += """document.querySelector('[name="{:}"]').value = `{:}`;
""".format(
            k, v
        )

    subprocess.run(["wl-copy", script])


if len(argv) == 2 and argv[1] == "resize":
    run_resize()
elif len(argv) == 4 and argv[1] == "post" and argv[2] in forms:
    label = argv[2]
    count = argv[3]
    run_post(label, count)
elif len(argv) == 4 and argv[1] == "inject" and argv[2] in forms:
    label = argv[2]
    count = argv[3]
    run_inject(label, count)
else:
    print(
        "usage:\n\n  fill_form.py (inject | post) ({:}) <0-9>\n\n  fill_form.py resize\n".format(
            " | ".join(forms.keys())
        )
    )
