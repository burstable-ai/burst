import sys, time, os
t0 = time.time()
print ("Public ip:", end=' ')
sys.stdout.flush()
os.system("curl https://ipv4.wtfismyip.com/text")
print ("This is a long-running process (of sorts)")
print (os.path.abspath('.'))
f = open("./data/test.log", 'w')
for i in range(int(sys.argv[1])):
    t = time.time()-t0
    print (i, "TIME:", t)
    sys.stdout.flush()
    print (i, "TIME:", t, file=f)
    f.flush()
    time.sleep(5)
f.close()

print ("OK, done with that. I should be going to sleep now...")
sys.stdout.flush()
