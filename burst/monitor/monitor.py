#!/usr/bin/env python3
import os, sys, json, time, subprocess, datetime, argparse
from pprint import pprint

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--ip", required=True)
args = parser.parse_args()

shuttime = None

while True:
    proc = subprocess.Popen(["docker", "ps", "--format='{{json .}}'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    count  = 0
    now = datetime.datetime.utcnow()
    lines = proc.stdout.read().strip().split(b"\n")
    for out in lines:
        out = out.decode().strip()[1:-1] #seems a docker bug; returning single-quoted json blob
        # print("OUT:", out)
        if not out:
            continue
        j = json.loads(out)
        # pprint(j)
        # print ("RUNNING:", j['Image'], j['Labels'])
        for x in j['Labels'].split(','):
            if 'burstable' in x:
                key, val = x.split('=')
                # print ("LABEL: %s = %s" % (key, val))
                if key == 'ai.burstable.shutdown':
                    delay = int(val)
                    t = now + datetime.timedelta(seconds = delay)
                    if shuttime == None or shuttime < t:
                        shuttime = t
                else:
                    print ("ERROR -- unknown docker label %s=%s" % (key, val))
            count += 1
    # if count==0:
    #     print ("No burstable containers are running")

    remain = (shuttime-now) if shuttime else None
    print ("time now:", now, "shutoff time:", shuttime, "remaining:", remain.total_seconds() if remain != None else "infinite")
    if remain != None and remain < datetime.timedelta(seconds=0):
        print ("Proceeding to shutdown {0}".format(args.ip))
        os.system("burst --verbosity 1 --stop_instance_by_url {0}".format(args.ip))
        break

    time.sleep(5)