#!/usr/bin/env python3
import os, sys, json, time, subprocess, datetime, argparse, traceback

#for absolute imports to work in script mode, we need to import from the root folder
opath = os.path.abspath(".")
abspath = os.path.abspath(__file__)
abspath = abspath[:abspath.rfind('/') + 1]
os.chdir(abspath)
abspath = os.path.abspath("../..")
sys.path.insert(0, abspath)

from burst.lcloud import *

os.chdir(opath)
print ("monitor.py pwd:", opath)

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

delay = 900  # if not specified by burst
shuttime = datetime.datetime.utcnow() + datetime.timedelta(seconds = delay) #default if no process running
while True:
    busy = False

    #check if rsync active
    proc = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = proc.stdout.read().strip().split(b"\n")
    for out in lines:
        out = out.decode().strip()[1:-1] #seems a docker bug; returning single-quoted json blob
        if not out:
            continue
        columns = out.split()
        if len(columns) > 4 and "rsync" in columns[4]:
            busy = True

    #check for running burst processes
    proc = subprocess.Popen(["docker", "ps", "--format='{{json .}}'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = proc.stdout.read().strip().split(b"\n")
    max_val = -1
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
                    busy = True
                    val = int(val)
                    if val == 0:
                        val = 10000000000
                    max_val = max(val, max_val)
                elif key == 'ai.burstable.monitor':
                    pass
                else:
                    print ("ERROR -- unknown docker label %s=%s" % (key, val))
                    sys.stdout.flush()
    if max_val >= 0:
        delay = max_val

    now = datetime.datetime.utcnow()
    if busy:
        shuttime = now + datetime.timedelta(seconds=delay)

    remain = (shuttime-now).total_seconds()
    print ("time now:", now, "shutoff time:", shuttime, "remaining:", remain)
    sys.stdout.flush()
    if remain < 0:
        print ("Proceeding to shutdown {0}".format(args.ip))
        sys.stdout.flush()
        try:
            stop_instance_by_url(args.ip, vars(args))
        except:
            print ("SHUTDOWN FAIL")
            os.system("pwd")
            os.system("ls")
            traceback.print_exc()
            sys.stdout.flush()
            time.sleep(999999)
        break

    time.sleep(5)
