#!/usr/bin/env python3
import os, sys, argparse

DEfAULT_IMAGE = "rexec_image"

print ("rexec -- remote execution using docker containers")

cmd = "docker build . -t {0}".format(DEfAULT_IMAGE)
print (cmd)
os.system(cmd)

args = " ".join(sys.argv[1:])
path = os.path.abspath('.')
cmd = "docker run --rm -it -v {2}:/home/rexec {0} {1}".format(DEfAULT_IMAGE, args, path)
print (cmd)
os.system(cmd)
