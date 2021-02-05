import os, sys

out1 = """Build phase 1 success"""

out2 = """Build phase 2 success"""

os.system("rm buildtest.log")
os.system("burst --verbosity 127 --build 2>&1 | tee buildtest.log")

f = open("buildtest.log")
s = f.read()
f.close()

print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TEST COMPLETED~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
if out1 in s and out2 in s:
    print ("PASSED")
else:
    print ("FAILED")
