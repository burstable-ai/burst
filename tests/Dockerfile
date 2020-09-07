FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3 python3-pip nano fish git curl rclone fuse
RUN echo boo
RUN pip3 install git+https://github.com/datahub-projects/rexec#egg=rexec
RUN pip3 install gputil ipython

RUN adduser --disabled-password --gecos '' ubuntu

WORKDIR /home/rexec

CMD ["/bin/bash"]
