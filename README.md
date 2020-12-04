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

    burst --config

# Build & test a simple burst environment

### check out source code

    git clone https://github.com/burstable-ai/burst
    cd burst/tests

### build burst environment

    burst --gpus all --build
 
 ### run a command
 
     burst --gpus all --verbosity 1  python3 hello_burst.py
 
 ### expected output:
 
 