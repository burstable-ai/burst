#!/usr/bin/env python3
import os, sys, json, time, subprocess, datetime, argparse
from burst.lcloud import *
from pprint import pprint

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
        # pprint(j)
        # print ("RUNNING:", j['Image'], j['Labels'])
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

    #check for rsync process
    rsync_busy = True
    if os.path.exists(".burst-sentinel.txt"):
        f = open(".burst-sentinel.txt")
        t = float(f.readline())
        s = f.read()
        f.close()
        if 'rsync' in s:
            last_rsync = t
        else:
            age = time.time() - last_rsync
            print("rsync sentinel age: %f" % age)
            if age > 45:
                rsync_busy = False

    print ("rsync busy:", rsync_busy)
    if rsync_busy:
        shuttime = now + datetime.timedelta(seconds=tot_delay)

    remain = (shuttime-now).total_seconds()
    print ("time now:", now, "shutoff time:", shuttime, "remaining:", remain)
    sys.stdout.flush()
    if remain < 0:
        print ("Proceeding to shutdown {0}".format(args.ip))
        sys.stdout.flush()
        stop_instance_by_url(args.ip, vars(args))
        break

    time.sleep(5)
