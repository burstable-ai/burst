# burst example: minimal Hello World

If you copy this folder, make sure to also copy these hidden files:

    .dockerignore
    .burstignore

Launch a VM and build the dockerfile:

    burst --build --gpus none
    
(note: if you plan to be using gpu acceleration later, specify `--gpus all`)


If this is the first time you ran `burst` on this machine, it will take a few minutes
to do its thing. The end of the output should look like this:

    ---------------------OUTPUT-----------------------
    Build phase 1 success
    ----------------------END-------------------------
    Synchronizing folders
    receiving incremental file list
    
    Build phase 2 success
    DONE

Now you can run code in the cloud:

    burst python3 hello_burst.py

The output should look something like this:

    ---------------------OUTPUT-----------------------                                                         
    Welcome burstables! You're running a virtual machine with 2 cpus
    GPU drivers are installed but no GPU's are available
    ----------------------END-------------------------
    burst: DONE
