import os, sys, time

print ("fulltest_ports")
sys.stdout.flush()

for i in range(20):
    os.system("curl -s localhost:6789 > fulltest.ports")
    if os.path.getsize("fulltest.ports") > 0:
        break
    time.sleep(5)

if os.path.getsize("fulltest.ports") == 0:
    print("fulltest_ports: failed")
else:
    print("fulltest_ports: received data")

sys.stdout.flush()
