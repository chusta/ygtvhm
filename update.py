#!/usr/bin/env python3
import os
import re
import subprocess
import shlex


BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
JS = "ygtvhm.js"


def run(cmd):
    p = subprocess.Popen(shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    return out.decode()


def patch(data, date_type):
    with open(JS, "r") as fp:
        lines = fp.readlines()
    pos = lines.index(f"/* {date_type} */\n")
    line = f'd3.json("{data}"),\n'
    if line not in lines:
        lines.insert(pos, line)
    with open(JS, "w") as fp:
        fp.write("".join(lines))

    run(f"git add {data} {JS}")
    run(f"git commit -m 'add {data}'")


def main():
    out = run("git ls-files")
    git_data = sorted([x for x in out.split("\n") if x.startswith("data/")])
    sys_data = sorted([f"data/{x}" for x in os.listdir(DATA)])

    rx = re.compile("data/[0-9]{10}-[0-9]{10}.json")
    weekday = list()
    weekend = list()

    for day in sys_data:
        if rx.match(day):
            weekday.append(day)
        else:
            weekend.append(day)

    for day, end in zip(weekday, weekend):
        if day not in git_data:
            patch(day, "WEEKDAY")
        if end not in git_data:
            patch(end, "WEEKEND")


if __name__ == "__main__":
    main()
