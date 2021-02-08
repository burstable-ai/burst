import os, sys, argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--cloudmap", required=True, help="must specify cloudmap; a test file will be written here")
parser.add_argument("--storage-config")
parser.add_argument("--compute-config")
parser.add_argument("--verbosity", type=int, default=1)
args = parser.parse_args()

out1 = """Welcome burstables! You're running a virtual machine with"""

out2 = "----------------------END-------------------------"

os.system("rm fulltest.log")
opts = "--cloudmap={0} --verbosity={1}".format(args.cloudmap, args.verbosity)
if args.storage_config:
    opts += " --storage-config={0}".format(args.storage_config)
if args.compute_config:
    opts += " --compute-config={0}".format(args.compute_config)

cpath = args.cloudmap.split(':')[1]

cmd = "burst {0} 'python3 fulltest_command.py --cloudpath {1}' 2>&1 | tee fulltest.log".format(opts, cpath)
print (cmd)
os.system(cmd)

f = open("fulltest.log")
s = f.read()
f.close()

print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TEST COMPLETED~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
if out1 in s and out2 in s:
    print ("PASSED")
else:
    print ("FAILED")

