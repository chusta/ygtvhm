#!/usr/bin/env python3
import argparse
import os
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


def patch(data):
    with open(JS, "r") as fp:
        lines = fp.readlines()
    pos = lines.index("/* DATA */\n")
    lines.insert(pos, f'd3.json("{data}"),\n')
    with open(JS, "w") as fp:
        fp.write("".join(lines))


def main(args):
    out = run("git ls-files").decode()
    git_data = [x for x in out.split("\n") if x.startswith("data/")]
    sys_data = [f"data/{x}" for x in os.listdir(DATA)]

    for data in sys_data:
        if data not in git_data:
            print(f"+ {data}")
            patch(data)
            if not args.skip:
                run(f"git add {data} {JS}")
                run(f"git commit -m 'add {data}'")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--skip", action="store_true")
    main(ap.parse_args())
