import sys, time, os
t0 = time.time()
print ("HOME2\nPublic ip:", end=' ')
sys.stdout.flush()
os.system("curl https://ipv4.wtfismyip.com/text")
print ("This is a long-running process (of sorts)")
print (os.path.abspath('.'))
f = open("./data/test.log", 'w')
for i in range(10):
    t = time.time()-t0
    print (i, "TIME:", t)
    print (i, "TIME:", t, file=f)
    time.sleep(1)
f.close()

print ("OK, done with that. I should be going to sleep now...")
sys.stdout.flush()
