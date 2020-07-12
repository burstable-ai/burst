#!/usr/bin/env python3
import os, sys, argparse

DEfAULT_IMAGE = "rexec_image"
DOCKER_REMOTE = "localhost:2376"

print ("rexec -- remote execution using docker containers")

def rexec(url, args):
    print ("REXEC", url)

    if url:
        remote = "-H " + DOCKER_REMOTE
        user, host = url.split('@')
        locpath = os.path.abspath('.')[len(os.path.expanduser('~')):]
        path = "/home/{0}{1}".format(user, locpath)
    else:
        remote = ""
        path = os.path.abspath('.')
    print ("PATH:", path)

    cmd = "docker {1} build . -t {0}".format(DEfAULT_IMAGE, remote)
    print (cmd)
    os.system(cmd)

    args = " ".join(args)
    print ("PATH:", path)
    cmd = "docker {3} run --rm -it -v {2}:/home/rexec {0} {1}".format(DEfAULT_IMAGE, args, path, remote)
    print (cmd)
    os.system(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    args, unknown = parser.parse_known_args()
    rexec(args.url, unknown)