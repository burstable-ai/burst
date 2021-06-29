import multiprocessing, GPUtil


print ("Welcome burstables! You're running a virtual machine with %i cpus" % (multiprocessing.cpu_count()))

try:
    gpus = GPUtil.getGPUs()
    if len(gpus):
        print ("The following GPUs are available:")
        for gpu in gpus:
            print (gpu.name)
    else:
        print ("GPU drivers are installed but no GPUs are available")
except:
    print ("No GPU drivers available")
