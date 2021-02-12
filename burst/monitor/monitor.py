#!/usr/bin/env python3
import os, sys, json, time, subprocess, datetime
from pprint import pprint

shuttime = None

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
        for x in j['Labels'].split(','):
            if 'burstable' in x:
                key, val = x.split('=')
                print ("LABEL: %s = %s" % (key, val))
                if key == 'ai.burstable.shutdown':
                    delay = int(val)
                    t = datetime.datetime.utcnow() + datetime.timedelta(seconds = delay)
                    if shuttime == None or shuttime < t:
                        shuttime = t
                else:
                    print ("ERROR -- unknown docker label %s=%s" % (key, val))
            count += 1
    if count==0:
        print ("No burstable containers are running")

    now = datetime.datetime.utcnow()
    remain = (shuttime-now) if shuttime else None
    print ("time now:", now, "shutoff time:", shuttime, "remaining:", remain.total_seconds() if remain else None )
    if remain != None and remain < datetime.timedelta(seconds=0):
        print ("Proceeding to shutdown")

    time.sleep(5)