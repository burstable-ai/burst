import os, sys, argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--testpath", required=True)
args = parser.parse_args()

def do(cmd):
    print (cmd)
    os.system(cmd)

print ("fulltest_command:")

do("rm fulltest.foo")
do("echo 123 > {0}/foo".format(args.testpath))
do("echo 456 >> {0}/foo".format(args.testpath))
do("cp {0}/foo fulltest.foo".format(args.testpath))
do("rm {0}/foo".format(args.testpath))

sys.stdout.flush()