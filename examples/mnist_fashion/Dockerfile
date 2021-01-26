FROM nvidia/cuda:10.1-devel-ubuntu18.04
WORKDIR /home/burst/work
RUN apt-get update && apt-get install -y python3 python3-dev python3-pip nano fish git curl rclone fuse wget
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py  && rm get-pip.py
RUN pip3 install gputil ipython
COPY requirements.txt requirements.txt
RUN pip3 install -r ./requirements.txt
CMD ["/bin/bash"]

