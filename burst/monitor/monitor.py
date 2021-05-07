#!/usr/bin/env python3
import os, sys, json, time, subprocess, datetime, argparse, traceback
from dateutil.parser import parse as duparse
import dateutil.tz as dutz

#for absolute imports to work in script mode, we need to import from the root folder
opath = os.path.abspath(".")
abspath = os.path.abspath(__file__)
abspath = abspath[:abspath.rfind('/') + 1]
os.chdir(abspath)
abspath = os.path.abspath("../..")
sys.path.insert(0, abspath)

from burst.lcloud import *
from burst.verbos import set_verbosity
set_verbosity(127)

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

delay = 3600        # if not specified by burst
print ("\n" * 40)   #if you have to ask
shuttime = datetime.datetime.utcnow() + datetime.timedelta(seconds = delay) #default if no process running
while True:
    now = datetime.datetime.now(dutz.tzutc())
    recent = now - datetime.timedelta(seconds=15)
    really_busy = None
    #check if rsync active
    rsync_busy = False
    proc = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = proc.stdout.read().strip().split(b"\n")
    for out in lines:
        out = out.decode().strip()[1:-1] #seems a docker bug; returning single-quoted json blob
        if not out:
            continue
        columns = out.split()
        if len(columns) > 4 and "rsync" in columns[4]:
            rsync_busy = True
            print ("rsync in progress")

    if not rsync_busy:
        #check for running burst processes
        docker_busy = False
        proc = subprocess.Popen(["docker", "ps", "--format='{{json .}}'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = proc.stdout.read().strip().split(b"\n")
        max_val = -1
        ids = []
        for out in lines:
            out = out.decode().strip()[1:-1] #seems a docker bug; returning single-quoted json blob
            # print("OUT:", out)
            if not out:
                continue
            j = json.loads(out)
            ids.append(j['ID'])
            # print ("ID:", j['ID'])
            for x in j['Labels'].split(','):
                if 'burstable' in x:
                    key, val = x.split('=')
                    # print ("LABEL: %s = %s" % (key, val))
                    if key == 'ai.burstable.shutdown':
                        docker_busy = True
                        # print ("docker container running")
                        val = int(val)
                        if val == 0:
                            val = 10000000000
                        max_val = max(val, max_val)
                    elif key == 'ai.burstable.monitor':
                        pass
                    else:
                        print ("ERROR -- unknown docker label %s=%s" % (key, val))
                        sys.stdout.flush()

        if docker_busy:
            really_busy = False
            for ID in ids:
                # check for root processes spawned inside container -- if none, busy=False
                # print ("docker instance: %s PIDs:" % ID)
                proc = subprocess.Popen([f"docker", "exec", "-ti", ID, "ps", "ax"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                lines = proc.stdout.read().strip().split(b"\n")
                for out in lines:
                    cmd = out.split()[4:]
                    cmd = b" ".join(cmd)
                    cmd = cmd.decode()
                    # print (cmd)
                    if cmd not in ["COMMAND", "ps ax", "bash"]:
                        really_busy = True
                        print ("active process")
                        break
                if really_busy:
                    break

                # check for tty activity
                proc = subprocess.Popen([f"docker", "exec", "-ti", ID, "stat", "/dev/pts/0"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                lines = proc.stdout.read().strip().split(b"\n")
                for out in lines:
                    out = out.decode()
                    columns = out.split()
                    # print ("COLS:", columns)
                    if len(columns) == 4 and columns[0] in ["Access:", "Modify:", "Change:"]:
                        t = duparse(f"{columns[1]} {columns[2]} {columns[3]}")
                        # print ("STAT:", t, recent)
                        if t > recent:
                            print("tty activity")
                            really_busy = True
                            break
                if really_busy:
                    break

    if really_busy == None:
        busy = rsync_busy
    else:
        busy = really_busy

    # print ("BUSY:", busy)

    if max_val >= 0:
        delay = max_val

    now = datetime.datetime.utcnow()
    if busy:
        shuttime = now + datetime.timedelta(seconds=delay)

    remain = (shuttime-now).total_seconds()
    print ("Time:", now.strftime("%Y/%m/%d %H:%M:%S utc"), "Stop:", shuttime.strftime("%Y/%m/%d %H:%M:%S utc"), "in %d sec" % remain)
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
