# burst example: minimal Hello Burst

If you copy this folder, make sure to also copy these hidden files:

    .dockerignore
    .burstignore

Launch a VM and build the dockerfile:

    burst build --gpu
    
Note: specifying the `--gpu` flag tells `burst` to use a GPU if it is available and to fall back on the CPU only if the GPU is not available. If you instead build with `--no-gpu`, `burst` will run on the CPU, whether or not a GPU exists.

If this is the first time you ran `burst` on this machine, it will take a few minutes
to do its thing. The end of the output should look like this:

    ---------------------OUTPUT-----------------------
    Build phase 1 success
    ----------------------END-------------------------
    Synchronizing folders
    receiving file list ... 
    7 files to consider

    sent 43 bytes  received 159 bytes  134.67 bytes/sec
    total size is 1911  speedup is 9.46

    Build phase 2 success
    DONE

Now you can run code in the cloud:

    burst run python3 hello_burst.py

The output should look something like this:

    ---------------------OUTPUT----------------------- 
    Welcome burstables! You're running a virtual machine with 4 cpus
    The following GPUs are available:
    Tesla T4
    ----------------------END-------------------------
    burst: DONE
