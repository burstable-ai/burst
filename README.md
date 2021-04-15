# burst
## A command-line tool to remotely execute code in the cloud

## Introduction

`burst` lets you run your software remotely---on any sized virtual machine---without any change to your existing development process.  All you need is a working Dockerfile.

We support remote computing on Amazon Web Services and will be adding more (Google Cloud Platform support is currently in beta).

Detailed installation instructions and usage examples can be found here: https://www.burstable.ai/

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

_Note: if you want to contribute to the burst OSS project or just follow bleeding-edge development, install through gitHub as described [here](https://github.com/burstable-ai/burst/wiki/Contributing-To-Burst) instead._

### SSH keys:
You must have a public/private ssh key pair, stored as `~/.ssh/id_rsa.pub` and `~/.ssh/id_rsa` by default.  

If you do not already have ssh keys, run `ssh-keygen` to generate them:

    ssh-keygen -t rsa -b 4096

### Recommended: set up a Python virtual environment

Follow the instructions here: [python-virtual-environments-a-primer](https://realpython.com/python-virtual-environments-a-primer/)

Launch the virtual environment and do the remainder of your installation and set-up _inside_ the virtual environment.

### Install the command-line tool:

    pip install burstable

### Run the interactive configuration setup:

    burst configure

Enter your configuration information as prompted to set up a remote compute service.

## Build & test a simple burst environment

### Download test examples

Download the tarball of examples from https://burstable.ai/examples

Unpack the examples tarball and `cd` into the `hello_burst/` directory.  You should see a file called `hello_burst.py`.

### Make sure Docker is running:

The Docker daemon must be running in the background to use `burst`.
Test to make sure it is running and that you have the correct version:

    docker --version

It should return something like:

    Docker version 19.03.12, build 48a66213fe

### Build the burst environment:

    burst build --gpu

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
 
### Run a command on the remote server:
 
     burst run python3 hello_burst.py
 
The response should look like this:

    ---------------------OUTPUT-----------------------
    Welcome burst-utioners! You're running a virtual machine with 4 cpus
    The following GPU's are available:
    Tesla T4
    ----------------------END-------------------------
    burst: DONE
    
## Use burst to run a Python project on a remote GPU:

### Run a machine learning example
 
There are several `burst` examples posted here: https://burstable.ai/examples  

We recommend walking through the CIFAR-10 example, which uses Pytorch to implement a Convolutional Neural Net (CNN) for image classification on the benchmark CIFAR-10 dataset.  This example also illustrates how to use `burst` to run the CNN using a Jupyter notebook on a remote GPU, for real-time model building and manipulation.

### Run your own Python project

The examples page also includes instructions and template files for setting up your own Python project to run through `burst`, and/or for using `burst` to run a Jupyter notebook on a remote GPU.
