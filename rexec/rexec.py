#!/usr/bin/env python3
import os, sys, argparse

DEfAULT_IMAGE = "rexec_image"

print ("rexec -- remote execution using docker containers")

cmd = "docker build . -t {0}".format(DEfAULT_IMAGE)
print (cmd)

args = " ".join(sys.argv[1:])
print ("ARGS:", args)
cmd = "docker run --rm -it {0} {1}".format(DEfAULT_IMAGE, args)
print (cmd)