# Introduction

`rexec` is an open-source tool enabling developers to run their software remotely - on any sized virtual machine - without any change to their existing development process.

We currently support Amazon and Google cloud services, with the intent to add more over time.

# Dependencies

* Python3 
* Docker version 19 or higher
* A folder/project with a working `Dockerfile`

# Installation 

`git clone https://github.com/datahub-projects/rexec.git && cd rexec && pip install -r requirements.txt`

or 

TODO - add `pip install -e git+ssh://git@github.com/datahub-projects/rexec#egg=rexec`

# Configuration

Our configuration is currently manual. You will need to do the following: 

`mkdir -p ~/.rexec` # create config folder if it the folder does not exist

Edit `config.py` with:

```
access="<your-aws-access-key>"
secret="<your-aws-secret>"
region="us-west-2"
```

# Run `rexec` tests

```
cd rexec/tests


 % ../bin/rexec python3 test_script.py 
ARGV: ['python3', 'test_script.py']
REXARGS: []
CMDARGS: ['python3', 'test_script.py']
ARGS: Namespace(access=None, command=None, delay=0, dockerfile='Dockerfile', gpus=None, image=None, list_servers=False, local=False, p=None, pubkey=None, region=None, rexecuser=None, secret=None, shutdown=900, size=None, sshuser='ubuntu', stop_instance_by_url=None, terminate_servers=False, url=None, uuid=None)
Rexec username: kevincollins
Waiting for sshd
['ssh', '-o StrictHostKeyChecking=no', 'ubuntu@34.221.2.128', 'echo', "'sshd responding'"]
SSH returns -->sshd responding
|True<--
['ssh', '-o StrictHostKeyChecking=no', '-NL', '2376:/var/run/docker.sock', 'ubuntu@34.221.2.128']
['docker', '-H localhost:2376', 'ps', '--format', '{{json .}}']
Removing topmost layer
['docker', '-H localhost:2376', 'rmi', '--no-prune', 'rexec_image']
Error: No such image: rexec_image

rexec: name rexec_kevincollins size t2.small image ami-0ba3ac9cd67195659 url 34.221.2.128
rsync -vrltzu /Users/kevincollins/datahub/rexec/tests/* ubuntu@34.221.2.128:/home/ubuntu/_REXEC_datahub_rexec_tests/
building file list ... done
created directory /home/ubuntu/_REXEC_datahub_rexec_tests
Dockerfile
foo
longtest.py
test_local
test_remote
test_remote2
test_remote3
test_script.py
data/
data/touched_by_fire

sent 1498 bytes  received 224 bytes  688.80 bytes/sec
total size is 1273  speedup is 0.74
docker -H localhost:2376 build . --file Dockerfile -t rexec_image
Sending build context to Docker daemon  3.072kB
Step 1/6 : FROM ubuntu:20.04
 ---> adafef2e596e
Step 2/6 : RUN apt-get update && apt-get install -y python3 python3-pip nano fish git curl
 ---> Using cache
 ---> b1a602f9a279
Step 3/6 : RUN pip3 install git+https://github.com/datahub-projects/rexec#egg=rexec
 ---> Using cache
 ---> 1e59e57c8cfe
Step 4/6 : RUN adduser --disabled-password --gecos '' ubuntu
 ---> Using cache
 ---> 6fb6472103f2
Step 5/6 : WORKDIR /home/rexec
 ---> Using cache
 ---> 178b736f8ae9
Step 6/6 : CMD ["/bin/bash"]
 ---> Running in 7039377cb232
Removing intermediate container 7039377cb232
 ---> 44c0f2e4825f
Successfully built 44c0f2e4825f
Successfully tagged rexec_image:latest
docker -H localhost:2376 run   --rm -it -v /home/ubuntu/_REXEC_datahub_rexec_tests:/home/rexec rexec_image python3 test_script.py


---------------------OUTPUT-----------------------
test_script running, args: []
----------------------END-------------------------


rsync -vrltzu 'ubuntu@34.221.2.128:/home/ubuntu/_REXEC_datahub_rexec_tests/*' /Users/kevincollins/datahub/rexec/tests/
receiving file list ... done
foo

sent 44 bytes  received 248 bytes  116.80 bytes/sec
total size is 1274  speedup is 4.36
Scheduling shutdown of VM at 34.221.2.128 for 900 seconds from now
docker -H localhost:2376 run --rm -d rexec_image rexec --stop_instance_by_url 34...
Shutdown process container ID:
b518a1110e7f9f6607166637f012d36c96b93c3d38be3f0c2c50bcc6302f11ce
DONE




