import sys
print ("test_script running, args:", sys.argv[1:])
f = open("foo", 'w')
f.write("bar")
f.close()
