from datetime import datetime, timedelta


_W = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def get_time() -> datetime:
    date = datetime.now()
    date = date.replace(minute=0, second=0, microsecond=0)
    return date


def monthly(weekday: str, time: str):
    h, m = time.split(":")
    date = get_time()
    while date.minute != int(m):
        date = date + timedelta(minutes=1)
    while date.hour != int(h):
        date = date + timedelta(hours=1)
    while True:
        while date.day > 7 or date.weekday() != _W[weekday]:
            date = date + timedelta(days=1)
        yield date
        date = date + timedelta(days=1)


def weekly(weekday: str, time: str):
    h, m = time.split(":")
    date = get_time()
    while date.minute != int(m):
        date = date + timedelta(minutes=1)
    while date.hour != int(h):
        date = date + timedelta(hours=1)
    while date.weekday() != _W[weekday]:
        date = date + timedelta(days=1)
    while True:
        yield date
        date += timedelta(weeks=1)


def fixed(*dates: str):
    for date in dates:
        _date = datetime.fromisoformat(date)
        if _date < datetime.now():
            continue
        yield _date


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
        "date": weekly("monday", "14:30"),
        "duration": timedelta(hours=3),
        "category": _C["Kultur"],
        "place": _P["Hückelhoven"],
        "address": "Friedrichplatz 7",
        "description": """Interkultureller Nähtreff mit Kinderbetreuung. Im Vordergrund steht die gemeinsame Freude am Nähen und das offene Gespräch miteinander. NähanfängerInnen sind genauso willkommen wie Fortgeschrittene. Die Kinder werden während der Kurszeit betreut.

Jeden Montag von 14:30 Uhr bis 17:30 Uhr im Begegnungszentrum.
Leitung Silke Löwenkamp, famkrack_XXX_@googlemail.com .""",
    },
    "ela": {
        "title": "Offener Näh- und Handarbeitstreff",
        "date": weekly("tuesday", "10:00"),
        "duration": timedelta(hours=3),
        "category": _C["Kultur"],
        "place": _P["Hückelhoven"],
        "address": "Rheinstraße 103",
        "description": """Offener Näh- und Handarbeitstreff für Jung und Alt. Im Vordergrund steht die gemeinsame Freude am Nähen, Häkeln und Stricken. Anfänger/innen sind genauso willkommen wie Fortgeschrittene. Es wird für den guten Zweck oder an privaten Projekten gearbeitet. Schau gerne mal vorbei!

Jeden Dienstag von 10 Uhr bis 13 Uhr im DRK Hückelhoven.

Kontakt: Manuela Backes, 0176 _XXX_81416805""",
    },
    "heike": {
        "title": "Offener Näh- und Handarbeitstreff",
        "date": weekly("thursday", "17:30"),
        "duration": timedelta(hours=2),
        "category": _C["Kultur"],
        "place": _P["Hückelhoven"],
        "address": "Dr. Ruben-Straße 10",
        "description": """Offener Näh- und Handarbeitstreff in Kathis Pedalotreff. Schau gerne mal vorbei! Jeden Donnerstag von 1730 Uhr bis 1930 Uhr.""",
    },
    "messe_efg": {
        "title": "Gottesdienst",
        "date": weekly("sunday", "10:00"),
        "duration": timedelta(hours=1.5),
        "category": _C["Messe"],
        "place": _P["Baal"],
        "address": "Fringstraße 8",
        "description": """Wir sind eine aktive christliche Gemeinde, deren Türen für jeden offen stehen. Mit unterschiedlichen Aktivitäten sind alle Altersgruppen angesprochen und in das Gemeindeleben eingebunden.

Gerne begrüßen wir Sie in unserem nächsten Gottesdienst am kommenden Sonntag oder bei einer der Gruppenveranstaltungen. Der Gottesdienst ist familienfreundlich mit Mutter-Kind-Raum und Kinderprogramm.

E-Mail: kontakt_XXX_@efg-hueckelhoven.de
Tel.: 02435 _XXX_2078
https://www.efg-hueckelhoven.de
https://www.instagram.com/efg_baal
https://www.youtube.com/channel/UCENZN_mYZurANrfSxNjZRjw
""",
    },
    "nori_schacht4": {
        "duration": timedelta(hours=7),
        "category": _C["Märkte"],
        "title": "Trödelmarkt Schacht 4",
        "date": fixed(
            "2024-03-31T11:00:00",
            "2024-04-01T11:00:00",
            "2024-04-21T11:00:00",
            "2024-05-19T11:00:00",
            "2024-06-23T11:00:00",
            "2024-07-21T11:00:00",
            "2024-08-18T11:00:00",
            "2024-09-22T11:00:00",
            "2024-10-20T11:00:00",
            "2024-11-17T11:00:00",
            "2024-12-15T11:00:00",
        ),
        "place": _P["Ratheim"],
        "address": "Myhler Straße 81",
        "description": """Trödelmarkt, auch Neuwaren. Für Standanmeldung oder Kontakt: https://www.marktcom.de/veranstaltung/schacht-iv-41836-hueckelhoven""",
    },
    "nori_centershop": {
        "duration": timedelta(hours=7),
        "category": _C["Märkte"],
        "title": "Trödelmarkt Center Shop",
        "date": fixed(
            "2024-05-05T11:00:00",
            "2024-05-30T11:00:00",
            "2024-06-30T11:00:00",
            "2024-08-25T11:00:00",
            "2024-09-29T11:00:00",
            "2024-10-27T11:00:00",
            "2024-12-08T11:00:00",
        ),
        "place": _P["Hückelhoven"],
        "address": "Rheinstr. 17",
        "description": """Trödelmarkt, auch Neuwaren. Für Standanmeldung oder Kontakt: https://www.marktcom.de/veranstaltung/center-shop-41836-hueckelhoven?term_id=1066516""",
    },
    "wochenmarkt": {
        "category": _C["Märkte"],
        "title": "Wochenmarkt",
        "date": weekly("friday", "8:00"),
        "duration": timedelta(hours=4.5),
        "place": _P["Hückelhoven"],
        "address": "Rathausplatz",
        "description": """Großer Wochenmarkt rund ums Hückelhovener Rathaus. Freitags 08.00 Uhr bis 12.30 Uhr.""",
    },
    # https://www.vianobis-eingliederungshilfe.de/termine
    "repair": {
        "duration": timedelta(hours=3),
        "category": _C["Kultur"],
        "title": "Repair Cafe",
        "date": monthly("saturday", "15:00"),
        "place": _P["Hückelhoven"],
        "address": "Dr. Ruben-Straße 10",
        "description": """Mit kompetenter Hilfestellung reparieren wir gemeinsam defekte Gegenstände. Bei Kaffee und Kuchen finden interessante Gespräche und Begegnungen statt.

Jeden 1. Samstag im Monat, 15 bis 18 Uhr. Für Rückfragen, montags bis donnerstags, von 10 bis 14 Uhr unter Telefon 02433 30541220.""",
    },
}
for _, form in forms.items():
    form["description"] = form["description"].replace("_XXX_", "")

groups = {
    "nori": ["nori_schacht4", "nori_centershop"],
    "markt": ["nori_schacht4", "nori_centershop", "wochenmarkt"],
    "kai": ["ela"],
    "katho": ["silke"],
    "pedalo": ["maike"],
    "all": [
        "nori_schacht4",
        "nori_centershop",
        "wochenmarkt",
        "repair",
        "silke",
        "ela",
        # "ekir_messe",
    ],
}

# efg_frauen
# vikz
# ditib
# kai_garten
# hilfarth_garten
