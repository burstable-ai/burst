import os, sys

out1 = """---------------------OUTPUT-----------------------
Build phase 1 success
----------------------END-------------------------"""

out2 = """Build phase 2 success"""

os.system("rm buildtest.log")
os.system("burst --build 2>&1 | tee buildtest.log")

f = open("buildtest.log")
s = f.read()
f.close()

print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TEST COMPLETED~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
if out1 in s and out2 in s:
    print ("PASSED")
else:
    print ("FAILED")

#burst --verbosity 1 python3 hello_burst.py
