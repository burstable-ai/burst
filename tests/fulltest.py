import os, sys

out1 = """Welcome burstables! You're running a virtual machine with"""

out2 = "----------------------END-------------------------"

os.system("rm fulltest.log")
os.system("burst --verbosity 127 --cloudmap s3:s3_data 'python3 fulltest_command.py' 2>&1 | tee fulltest.log")

f = open("fulltest.log")
s = f.read()
f.close()

print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TEST COMPLETED~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
if out1 in s and out2 in s:
    print ("PASSED")
else:
    print ("FAILED")

