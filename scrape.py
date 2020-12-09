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

with open("config.json", "r") as fp:
    CFG = json.load(fp)


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
ROOMS = {"cybex": 9, "cardio": 12, "free": 12}


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


def parse_spots(html):
    soup = BeautifulSoup(html, "html.parser")
    spot = soup.find("a", {"class": "signUpGXP"})
    if spot:
        rx = re.match(r"\d+", spot["textmsg"])
        return rx.group() if rx else "0"


def transform(entry):
    day, date = entry["date"].split(", ", 1)
    date = datetime.datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
    if day not in WEEKDAYS:
        return

    room = entry["room"].lower().split()[0]
    if room not in ROOMS.keys():
        return

    slot = entry["slot"]
    free = int(entry["free"])
    used = ROOMS[room] - free

    return {
        "date": date,
        "slot": slot,
        "used": used,
        "room": room,
    }


def dedup(items):
    def is_same(a, b):
        return (
            a["date"] == b["date"] and
            a["slot"] == b["slot"] and
            a["room"] == b["room"]
        )

    weight = list()
    cardio = list()
    cybex = list()
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


def main(args):
    for a, b in daterange(args.a, args.b):
        results = list()
        for item in fetch(a, b):
            if (free := parse_spots(item[9])):
                x = {
                    "free": free,
                    "date": item[0],
                    "slot": item[1],
                    "room": item[4],
                }
                if (data := transform(x)):
                    results.append(data)
        fpath = f"{a}-{b}.json"
        with open(os.path.join(DATA, fpath), "w") as fp:
            json.dump(dedup(results), fp)
        print(f"[+] {fpath} ({len(results)})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", default="20201005")
    ap.add_argument("-b", default=time.time())
    main(ap.parse_args())
