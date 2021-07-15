#!/usr/bin/env python3
import os, sys, json, time, subprocess, datetime, argparse, traceback, requests
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

def check_jupyter(port = 8888):
    now = datetime.datetime.utcnow().replace(tzinfo=dutz.tzutc())  # bah humbug
    # print("NOW:", now)
    recent = datetime.datetime(2021, 1, 6, tzinfo=dutz.tzutc())

    r = requests.get(f"http://127.0.0.1:{port}/api/kernels")
    if r.status_code == 200:
        j = json.loads(r.content)
        # pprint(j)
        for k in j:
            if k['execution_state'] == 'busy':
                recent = now
                break
            last = duparse(k['last_activity'])
            # print("LAST:", last)
            if last > recent:
                recent = last
        seconds = (now - recent).total_seconds()
        # print(f"last activity {seconds} seconds ago")
        return seconds
    else:
        print("Error:", r.status_code, r.content)
        return False

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--ip",         required=True)
parser.add_argument("--provider",   required=True)
parser.add_argument("--access",     required=True)
parser.add_argument("--secret",     required=True)
parser.add_argument("--region",     required=True)
parser.add_argument("--project",    default="")
parser.add_argument("--jupyter_port", type=int)
args = parser.parse_args()

delay = 3600        # if not specified by burst
print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~SESSION~~~~~~~~~~~~~~~~~~~~~~~~~~")   #if you have to ask
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
        juport = None
        for out in lines:
            out = out.decode().strip()[1:-1] #seems a docker bug; returning single-quoted json blob
            # print ("OUT:", out)
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
                    elif key == 'ai.burstable.jupyter':
                        juport = val
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
                    # print("CMD:", cmd, "CHK:", cmd.split()[0].lower().split('/')[-1])
                    if cmd.split()[0].lower().split('/')[-1] not in ["command", "ps", "bash", "fish", "sh", "tsh",
                          "zsh"] and 'jupyter-lab' not in cmd and 'ipykernel_launcher' not in cmd and "<defunct>" not in cmd:
                        really_busy = True
                        print ("active process: %s" % cmd)
                        break
                if really_busy:
                    break

                # check for tty activity
                proc = subprocess.Popen([f"docker", "exec", "-ti", ID, "ls", "/dev/pts"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                pts = proc.stdout.read().decode('utf8').strip().split()
                pts = [x for x in pts if x[0].isdigit()]
                # print ("PTS:", pts)
                for pty in pts[:-1]:    #last tty is ours
                    # print ("PTY:", pty)
                    proc = subprocess.Popen(["docker", "exec", "-ti", ID, "stat", f"/dev/pts/{pty}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    lines = proc.stdout.read().strip().split(b"\n")
                    for out in lines:
                        out = out.decode()
                        columns = out.split()
                        # print ("COLS:", columns)
                        if len(columns) == 4 and columns[0] in ["Access:", "Modify:", "Change:"]:
                            t = duparse(f"{columns[1]} {columns[2]} {columns[3]}")
                            # print ("STAT:", t, recent)
                            if t > recent:
                                print(f"tty activity {(now-t).total_seconds()} seconds ago")
                                really_busy = True
                                break
                    if really_busy:
                        break
                if really_busy:
                    break

                # check for jupyter activity
                if juport:
                    sec = check_jupyter(juport)
                    if sec != False and sec < 15:
                        print (f"jupyter activity {sec} seconds ago")
                        really_busy = True

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
