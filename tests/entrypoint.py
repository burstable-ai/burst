import sys, os, time, platform

print ("Public ip:", end=' ')
sys.stdout.flush()

os.system("curl https://ipv4.wtfismyip.com/text")
sys.stdout.flush()

print ("Linux version:", platform.platform())
sys.stdout.flush()
time.sleep(5)

print ("OK, done")
sys.stdout.flush()
