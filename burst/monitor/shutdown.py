import os, sys, json, time, subprocess
from pprint import pprint

while True:
    proc = subprocess.Popen(["docker",  "ps", "--format='{{json .}}'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.read()
    if out:
        out = eval("""r%s""" % out.decode())
        print(out)
        j = json.loads(out)
        pprint(j)
    else:
        print ("NADA")
    time.sleep(7)