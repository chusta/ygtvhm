#!/usr/bin/env python3
import argparse
from bs4 import BeautifulSoup
import datetime
import json
import os
import requests
import re
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
ROOMS = {"cybex": 9, "cardio": 12, "free": 12}

if not os.path.exists(DATA):
    os.mkdir(DATA)

with open("config.json", "r") as fp:
    CFG = json.load(fp)


def fetch(dt_a, dt_z):
    uri = CFG["target"]
    data = CFG["params"].copy()
    data["start"] = dt_a
    data["end"] = dt_z

    resp = requests.get(uri, data)
    if resp.ok:
        data = resp.content.strip(b"()")
        j = json.loads(data)
        return j.get("aaData", [])


def daterange(dt_a, dt_z):
    def check(dt):
        if isinstance(dt, str):
            dt = datetime.datetime.strptime(dt, "%Y%m%d")
        elif isinstance(dt, float):
            dt = datetime.datetime.fromtimestamp(dt)
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            raise Exception(f"Invalid input range: {dt}")
        return dt

    start_week = lambda x: x - datetime.timedelta(days=x.weekday())
    fmt = lambda x: datetime.datetime.strftime(x, "%s")

    dt_a = check(dt_a)
    dt_z = check(dt_z)
    a = start_week(dt_a)
    z = start_week(dt_z)
    while a <= z:
        dtrange = (fmt(a), fmt(a + datetime.timedelta(days=6)))
        if f"{'-'.join(dtrange)}.json" not in os.listdir(DATA):
            yield dtrange
        a += datetime.timedelta(days=7)


def transform(entry, r_weekday, r_weekend):
    def parse_spots(html):
        soup = BeautifulSoup(html, "html.parser")
        if spot := soup.find("a", {"class": "signUpGXP"}):
            rx = re.match(r"\d+", spot["textmsg"])
            return rx.group() if rx else "0"

    room = entry[4].lower().split()[0]
    if room not in ROOMS.keys():
        return

    day, date = entry[0].split(", ", 1)
    date = datetime.datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
    used = ROOMS[room] - int(parse_spots(entry[9]))
    slot = entry[1]

    data = {
        "date": date,
        "slot": slot,
        "used": used,
        "room": room,
    }
    if day in WEEKDAYS:
        r_weekday.append(data)
    else:
        r_weekend.append(data)


def dedup(items):
    def is_same(a, b):
        return (
            a["date"] == b["date"] and
            a["slot"] == b["slot"] and
            a["room"] == b["room"]
        )

    weight, cardio, cybex = [], [], []
    for i in items:
        if i["room"] == "free":
            weight.append(i)
        elif i["room"] == "cardio":
            cardio.append(i)
        elif i["room"] == "cybex":
            cybex.append(i)

    for room in [weight, cardio, cybex]:
        last = room[-1]
        for i in range(len(room) - 2, 0, -1):
            this = room[i]
            if is_same(last, this):
                last["used"] += this["used"]
                room.pop(i)
                this = room[i]
            last = this
    return weight + cardio + cybex


def write(name, data):
    with open(os.path.join(DATA, name), "w") as fp:
        json.dump(dedup(data), fp)
    print(f"[+] {name} ({len(data)})")


def main(args):
    for a, b in daterange(args.a, args.b):
        r_weekday = list()
        r_weekend = list()
        for item in fetch(a, b):
            transform(item, r_weekday, r_weekend)

        write(f"{a}-{b}.json", r_weekday)
        write(f"{a}-{b}s.json", r_weekend)
        time.sleep(args.sleep)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", default="20201005")
    ap.add_argument("-b", default=time.time())
    ap.add_argument("-s", "--sleep", default=1, type=int)
    main(ap.parse_args())
