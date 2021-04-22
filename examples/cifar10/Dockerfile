#FROM burstableai/burst_base:latest
FROM nvidia/cuda:11.3.0-devel-ubuntu20.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends wget nginx python3 python3-distutils nano fish git curl fuse

RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
RUN pip3 install gputil ipython

RUN wget https://github.com/rclone/rclone/releases/download/v1.53.1/rclone-v1.53.1-linux-amd64.deb
RUN dpkg --install rclone-v1.53.1-linux-amd64.deb

WORKDIR /home/burst/work

COPY requirements.txt requirements.txt
RUN pip3 install -r ./requirements.txt

CMD ["/bin/bash"]