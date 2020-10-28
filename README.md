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

`git clone https://github.com/burstable-ai/burst.git && cd burst && pip install -r requirements.txt`

or 

`pip install -e git+ssh://git@github.com/burstable-ai/burst#egg=burst`

# Configuration

Our configuration is currently manual. You will need to do the following: 

`mkdir -p ~/.burst` # create config folder if it the folder does not exist

Edit `~/.burst/config.yml` with:

```
default: myaws

myaws:
  provider: EC2
  access: <Amazon AWS Access Key>
  secret: <Amazon AWS Access Secret>
  region: us-west-2
  default_image: ami-0ba3ac9cd67195659
  default_size: t2.small
  default_gpu_image: ami-038b493084f00b948 
  default_gpu_size: g4dn.xlarge

mygoogle:
  provider: GCE
  access: <Google Cloud Account Key>
  secret: ~/.burst/<Google Cloud Account Private Key Filename>.json
  region: us-west1-b
  project: <Google Cloud Project ID>
  default_image: burst-nogpu
```

# Run `burst` tests

```
% cd tests
% ../bin/burst python3 test_script.py 
ARGV: ['python3', 'test_script.py']
REXARGS: []
CMDARGS: ['python3', 'test_script.py']
ARGS: Namespace(access=None, command=None, delay=0, dockerfile='Dockerfile', gpus=None, image=None, list_servers=False, local=False, p=None, pubkey=None, region=None, burst_user=None, secret=None, shutdown=900, size=None, sshuser='ubuntu', stop_instance_by_url=None, terminate_servers=False, url=None, uuid=None)
Burst username: kevincollins
Waiting for sshd
['ssh', '-o StrictHostKeyChecking=no', 'ubuntu@34.221.2.128', 'echo', "'sshd responding'"]
SSH returns -->sshd responding
|True<--
['ssh', '-o StrictHostKeyChecking=no', '-NL', '2376:/var/run/docker.sock', 'ubuntu@34.221.2.128']
['docker', '-H localhost:2376', 'ps', '--format', '{{json .}}']
Removing topmost layer
['docker', '-H localhost:2376', 'rmi', '--no-prune', 'burst_image']
Error: No such image: burst_image

burst: name burst_kevincollins size t2.small image ami-0ba3ac9cd67195659 url 34.221.2.128
rsync -vrltzu /Users/kevincollins/datahub/burst/tests/* ubuntu@34.221.2.128:/home/ubuntu/_BURST_datahub_burst_tests/
building file list ... done
created directory /home/ubuntu/_BURST_datahub_burst_tests
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
docker -H localhost:2376 build . --file Dockerfile -t burst_image
Sending build context to Docker daemon  3.072kB
Step 1/6 : FROM ubuntu:20.04
 ---> adafef2e596e
Step 2/6 : RUN apt-get update && apt-get install -y python3 python3-pip nano fish git curl
 ---> Using cache
 ---> b1a602f9a279
Step 3/6 : RUN pip3 install git+https://github.com/burstable-ai/burst#egg=burst
 ---> Using cache
 ---> 1e59e57c8cfe
Step 4/6 : RUN adduser --disabled-password --gecos '' ubuntu
 ---> Using cache
 ---> 6fb6472103f2
Step 5/6 : WORKDIR /home/burst
 ---> Using cache
 ---> 178b736f8ae9
Step 6/6 : CMD ["/bin/bash"]
 ---> Running in 7039377cb232
Removing intermediate container 7039377cb232
 ---> 44c0f2e4825f
Successfully built 44c0f2e4825f
Successfully tagged burst_image:latest
docker -H localhost:2376 run   --rm -it -v /home/ubuntu/_BURST_datahub_burst_tests:/home/burst burst_image python3 test_script.py


---------------------OUTPUT-----------------------
test_script running, args: []
----------------------END-------------------------


rsync -vrltzu 'ubuntu@34.221.2.128:/home/ubuntu/_BURST_datahub_burst_tests/*' /Users/kevincollins/datahub/burst/tests/
receiving file list ... done
foo

sent 44 bytes  received 248 bytes  116.80 bytes/sec
total size is 1274  speedup is 4.36
Scheduling shutdown of VM at 34.221.2.128 for 900 seconds from now
docker -H localhost:2376 run --rm -d burst_image burst --stop_instance_by_url 34...
Shutdown process container ID:
b518a1110e7f9f6607166637f012d36c96b93c3d38be3f0c2c50bcc6302f11ce
DONE
```

# Run Examples

TODO - add GPU-enabled machine learning examples! 


>>>>>>> 5fb2e81c6565677521ea069606597f49bb8e05a0
