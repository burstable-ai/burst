import multiprocessing, GPUtil


print ("Welcome rexec-utioners! You're running a virtual machine with %i cpus" % (multiprocessing.cpu_count()))

try:
    avail = GPUtil.getAvailable()
    if len(avail):
        print ("The following GPU's are available: %s" % avail)
    else:
        print ("GPU drivers are installed but no GPU's are available")
except:
    print ("No GPU drivers available")
