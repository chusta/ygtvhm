#!/usr/bin/env python3
import argparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import requests
import re
from subprocess import Popen, PIPE
import shlex
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
JS = "ygtvhm.js"

if not os.path.exists(JS):
    raise Exception(f"! Cannot find file: {JS}")

if not os.path.exists(DATA):
    os.mkdir(DATA)

with open("config.json", "r") as fp:
    CFG = json.load(fp)


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
WEEKENDS = ["Saturday", "Sunday"]
ROOMS = {"cybex": 9, "cardio": 12, "free": 12}


def run(cmd):
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    out, _ = p.communicate()
    return out.decode()


def write(name, data):
    with open(os.path.join(DATA, name), "w") as fp:
        json.dump(data, fp)
    print(f"+ {name}")


def patch(data, date_type):
    with open(JS, "r+") as fp:
        lines = fp.readlines()
        pos = lines.index(f"/* {date_type} */\n")
        line = f'd3.json("{data}"),\n'
        if line not in lines:
            lines.insert(pos, line)
        fp.seek(0)
        fp.write("".join(lines))
        fp.truncate()
    run(f"git add {data} {JS}")
    run(f"git commit -m 'add {data}'")


def fetch(dt_a, dt_z):
    uri = CFG["target"]
    data = CFG["params"]
    data["start"] = dt_a
    data["end"] = dt_z

    resp = requests.get(uri, data)
    if resp.ok:
        data = resp.content.strip(b"()")
        j = json.loads(data)
        return j.get("aaData", [])


def date_range(dt_a, dt_z):
    start_week = lambda x: x - timedelta(days=x.weekday())
    fmt = lambda x: datetime.strftime(x, "%s")
    a = start_week(dt_a)
    z = start_week(dt_z)
    while a <= z:
        dt_range = (fmt(a), fmt(a + timedelta(days=6)))
        if f"{'-'.join(dt_range)}.json" not in os.listdir(DATA):
            yield dt_range
        a += timedelta(days=7)


def parse_spots(html):
    result = 0
    soup = BeautifulSoup(html, "html.parser")
    if spot := soup.find("a", {"class": "signUpGXP"}):
        if rx := re.match("[0-9]+", spot["textmsg"]):
            result = int(rx.group())
    return result


def transform(entry, weekday, weekend):
    room = entry[4].lower().split()[0]
    if room not in ROOMS.keys():
        return

    day, date = entry[0].split(", ", 1)
    date = datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
    used = ROOMS[room] - parse_spots(entry[9])
    slot = entry[1]

    data = {
        "date": date,
        "slot": slot,
        "used": used,
        "room": room,
    }
    if day in WEEKDAYS:
        weekday.append(data)
    elif day in WEEKENDS:
        weekend.append(data)


def dedup(this, room):
    try:
        last = room[-1]
    except IndexError:
        room.append(this)
        return

    is_same = (
        this["date"] == last["date"] and
        this["slot"] == last["slot"] and
        this["room"] == last["room"]
    )
    if is_same:
        last["used"] += this["used"]
    else:
        room.append(this)


def include(items):
    weight, cardio, cybex = [], [], []
    for item in items:
        if item["room"] == "cybex":
            dedup(item, cybex)
        elif item["room"] == "free":
            dedup(item, weight)
        elif item["room"] == "cardio":
            dedup(item, cardio)
    return weight + cardio + cybex


def scrape(dt_a, dt_b):
    for a, b in date_range(dt_a, dt_b):
        weekday, weekend = [], []
        for item in fetch(a, b):
            transform(item, weekday, weekend)
        write(f"{a}-{b}.json", include(weekday))
        write(f"{a}-{b}s.json", include(weekend))
        time.sleep(1)


def update():
    files = run("git ls-files").split("\n")
    git_data = sorted([x for x in files if x.startswith("data/")])
    sys_data = sorted([f"data/{x}" for x in os.listdir(DATA)])

    rx = re.compile("data/[0-9]{10}-[0-9]{10}.json")
    for day in sys_data:
        if day not in git_data:
            patch(day, "WEEKDAY" if rx.match(day) else "WEEKEND")


def main(args):
    if args.cmd is None or args.cmd == "scrape":
        scrape(args.a, args.b)
    if args.cmd is None or args.cmd == "update":
        update()


def dt_type(s):
    try:
        dt = datetime.strptime(s, "%Y%m%d")
    except ValueError:
        dt = datetime.now()
        dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return dt


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", type=dt_type, default="20201005")
    ap.add_argument("-b", type=dt_type, default="")
    sp = ap.add_subparsers(dest="cmd")
    scrape_sp = sp.add_parser("scrape")
    update_sp = sp.add_parser("update")
    main(ap.parse_args())
