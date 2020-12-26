#!/usr/bin/env python3
import argparse
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
    return out


def patch(data, date_type):
    with open(JS, "r") as fp:
        lines = fp.readlines()
    pos = lines.index(f"/* {date_type} */\n")
    line = f'd3.json("{data}"),\n'
    if line not in lines:
        lines.insert(pos, line)
    with open(JS, "w") as fp:
        fp.write("".join(lines))


def main():
    out = run("git ls-files").decode()
    git_data = sorted([x for x in out.split("\n") if x.startswith("data/")])
    sys_data = sorted([f"data/{x}" for x in os.listdir(DATA)])

    rx = re.compile("data/[0-9]{10}-[0-9]{10}.json")
    weekend, weekday = [], []
    for x in sys_data:
        if rx.match(x):
            weekday.append(x)
        else:
            weekend.append(x)

    for data in weekday:
        if data not in git_data:
            patch(data, "WEEKDAY")
            run(f"git add {data} {JS}")
            run(f"git commit -m 'add {data}'")

    for data in weekend:
        if data not in git_data:
            patch(data, "WEEKEND")


if __name__ == "__main__":
    main()
