#!/usr/bin/env python3
import os, sys, json, time, subprocess
from pprint import pprint

while True:
    proc = subprocess.Popen(["docker", "ps", "--format='{{json .}}'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    count  = 0
    lines = proc.stdout.read().strip().split(b"\n")
    for out in lines:
        out = out.decode().strip()[1:-1] #seems a docker bug; returning single-quoted json blob
        # print("OUT:", out)
        if not out:
            continue
        j = json.loads(out)
        # pprint(j)
        print ("RUNNING:", j['Image'], j['Labels'])
        count += 1
        # if j[]
    if count==0:
        print ("NADA")
    time.sleep(5)