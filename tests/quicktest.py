import os, sys

out1 = """---------------------OUTPUT-----------------------
Welcome burstables! You're running a virtual machine with"""

out2 = "----------------------END-------------------------"

os.system("rm quicktest.log")
os.system("burst --verbosity 1 'python3 hello_burst.py' 2>&1 | tee quicktest.log")

f = open("quicktest.log")
s = f.read()
f.close()

print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TEST COMPLETED~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
if out1 in s and out2 in s:
    print ("PASSED")
else:
    print ("FAILED")
