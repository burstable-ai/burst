# burst
Command-line tool to remotely execute code in the cloud
=======
# Introduction

`burst` lets you run your software remotely - on any sized virtual machine - without any change to your existing development process, as long as you have a working Dockerfile.

We currently support Amazon and Google cloud services and will be adding more.

# Dependencies

* Python3 
* Docker version 19 or higher
* A folder/project with a working `Dockerfile`

# Installation 
### recommended: 
set up a virtual environment 

https://realpython.com/python-virtual-environments-a-primer/

### Install command-line tool:

    pip install burstable

# Interactive configuration setup:

    burst --configure

# Build & test a simple burst environment

### check out source code:

    git clone https://github.com/burstable-ai/burst
    cd burst/tests

### build burst environment:

    burst --build

This may take several minutes; be patient. After some output, 
you should see this: 

    ---------------------OUTPUT-----------------------
    Build phase 1 success
    ----------------------END-------------------------
    Synchronizing folders
    receiving incremental file list
    Scheduling shutdown of VM at 52.27.54.55 for 900 seconds from now
    
    
    Build phase 2 success
    DONE

 
 ### run a command on the remote server:
 
     burst python3 hello_burst.py
 
Response should look like this:
 
     ---------------------OUTPUT-----------------------                                                         
    Welcome burst-utioners! You're running a virtual machine with 4 cpus
    The following GPU's are available:
    Tesla T4
    ----------------------END-------------------------
    burst: DONE 

