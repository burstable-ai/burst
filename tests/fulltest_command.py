import os, sys, argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--cloudpath", required=True)
args = parser.parse_args()

print ("fulltest_command:")

cmd = "ls {0}".format(args.cloudpath)
print (cmd)
os.system(cmd)

sys.stdout.flush()