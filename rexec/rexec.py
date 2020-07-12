#!/usr/bin/env python3
import os, sys, argparse

DEfAULT_IMAGE = "rexec_image"

print ("rexec -- remote execution using docker containers")

def rexec(url, args):
    print ("REXEC", url)

    remote = ""
    if url:
        remote = "-H " + url
    cmd = "docker {1} build . -t {0}".format(DEfAULT_IMAGE, remote)
    print (cmd)
    os.system(cmd)

    args = " ".join(args)
    path = os.path.abspath('.')
    cmd = "docker {3} run --rm -it -v {2}:/home/rexec {0} {1}".format(DEfAULT_IMAGE, args, path, remote)
    print (cmd)
    os.system(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    args, unknown = parser.parse_known_args()
    rexec(args.url, unknown)