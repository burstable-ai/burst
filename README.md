# burst
## Command-line tool to remotely execute code in the cloud

## Introduction

`burst` lets you run your software remotely - on any sized virtual machine - without any change to your existing development process, as long as you have a working Dockerfile.

We currently support Amazon cloud services and will be adding more.

## Dependencies

* Python3 
* Docker version 19 or higher
* A folder/project with a working `Dockerfile`
* ssh keys
* AWS or Google Cloud Services account and access keys

## Check versions of Python and Docker at the command line
Make sure you are running the necessary versions of python and Docker (need Python 3, Docker >= 19)

    python --version
    docker --version 

## Installation 

_Note: if you want to contribute or just follow bleeding-edge development, install as described [here](https://github.com/burstable-ai/burst/wiki/Contributing-To-Burst) instead._

### ssh keys:
You must have a public/private ssh key pair, stored as ~/.ssh/id_rsa.pub and ~/.ssh/id_rsa.  If you do not already have ssh keys, run ssh-keygen to generate them.

    ssh-keygen -t rsa -b 4096

### recommended: 
set up a virtual environment 

https://realpython.com/python-virtual-environments-a-primer/

### Install command-line tool:

    pip install burstable

## Interactive configuration setup:

    burst --configure

## Build & test a simple burst environment

### check out source code:

    git clone https://github.com/burstable-ai/burst
    cd burst/tests

### Make sure Docker is running
The Docker daemon must be running in the background to use burst.

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


 ### run a machine learning example
 
The `examples/` folder contains pre-built machine learning examples to help you get started.  

We recommend walking through the CIFAR-10 example, which uses Pytorch to implement a Convolutional Neural Net (CNN) for image classification on the benchmark CIFAR-10 dataset.  This example also illustrates how to use `burst` to run a Jupyter notebook on a remote GPU, for real-time model building and manipulation on a GPU.

The instructions for running this CNN example are [here.](examples/cifar10/README.md)

The instructions for setting up your own Python project to run through `burst` are [here.](examples/your_project/README.md)
