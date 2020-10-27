import multiprocessing, GPUtil


print ("Welcome burst-utioners! You're running a virtual machine with %i cpus" % (multiprocessing.cpu_count()))

try:
    gpus = GPUtil.getGPUs()
    if len(gpus):
        print ("The following GPU's are available:")
        for gpu in gpus:
            print (gpu.name)
    else:
        print ("GPU drivers are installed but no GPU's are available")
except:
    print ("No GPU drivers available")
