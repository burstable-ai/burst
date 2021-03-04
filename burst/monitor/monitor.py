#!/usr/bin/env python3
import os, sys, json, time, subprocess, datetime, argparse

#for absolute imports to work in script mode, we need to import from the root folder
opath = os.path.abspath(".")
abspath = os.path.abspath(__file__)
abspath = abspath[:abspath.rfind('/') + 1]
os.chdir(abspath)
abspath = os.path.abspath("../..")
sys.path.insert(0, abspath)

from burst.lcloud import *

def stop_instance_by_url(url, conf):
    print ("STOP instance with public IP", url)
    # print ("DEBUG", os.path.abspath('.'), conf.secret)
    node = get_server(url=url, conf=conf)
    if not node:
        print ("No active instance found for IP", url)
    else:
        print ("shutting down node %s" % node)
        stop_server(node)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--ip",         required=True)
parser.add_argument("--provider",   required=True)
parser.add_argument("--access",     required=True)
parser.add_argument("--secret",     required=True)
parser.add_argument("--region",     required=True)
parser.add_argument("--project",    default="")
args = parser.parse_args()

shuttime = datetime.datetime.utcnow() + datetime.timedelta(seconds = 1800) #default if no process running
last_rsync = 0 #1970 aka the beginning of time
tot_delay = 60
while True:

    #check if rsync active
    busy = False
    proc = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = proc.stdout.read().strip().split(b"\n")
    for out in lines:
        out = out.decode().strip()[1:-1] #seems a docker bug; returning single-quoted json blob
        if not out:
            continue
        columns = out.split()
        if len(columns) > 4 and "rsync" in columns[4]:
            # print("OUT:", columns[4])
            busy = True
    if busy:
        print ("rsync active, pausing countdown")
        time.sleep(7.5) #because... the world is round
        continue

    #check for running burst processes
    proc = subprocess.Popen(["docker", "ps", "--format='{{json .}}'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    now = datetime.datetime.utcnow()
    lines = proc.stdout.read().strip().split(b"\n")
    cnt = 0
    for out in lines:
        out = out.decode().strip()[1:-1] #seems a docker bug; returning single-quoted json blob
        # print("OUT:", out)
        if not out:
            continue
        j = json.loads(out)
        for x in j['Labels'].split(','):
            if 'burstable' in x:
                key, val = x.split('=')
                # print ("LABEL: %s = %s" % (key, val))
                if key == 'ai.burstable.shutdown':
                    delay = int(val)
                    tot_delay = max(delay, tot_delay)
                    if delay < 0:
                        shuttime = datetime.datetime(3001, 1, 1)    #Yr 3K problem
                        break
                    elif delay == 0:
                        shuttime = now
                    else:
                        t = now + datetime.timedelta(seconds = delay)
                        if cnt == 0 or shuttime < t:
                            shuttime = t
                    cnt += 1
                elif key == 'ai.burstable.monitor':
                    pass
                else:
                    print ("ERROR -- unknown docker label %s=%s" % (key, val))
                    sys.stdout.flush()

    remain = (shuttime-now).total_seconds()
    print ("time now:", now, "shutoff time:", shuttime, "remaining:", remain)
    sys.stdout.flush()
    if remain < 0:
        print ("Proceeding to shutdown {0}".format(args.ip))
        sys.stdout.flush()
        stop_instance_by_url(args.ip, vars(args))
        break

    time.sleep(5)
