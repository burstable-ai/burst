import sys
print ("test_script running, args:", sys.argv[1:])
f = open("foo")
s = f.read()
s += str(len(s))
f.close()
f = open("foo")
f.write(s)
f.close()
