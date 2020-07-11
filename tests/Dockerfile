FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3 python3-pip nano fish curl
RUN adduser --disabled-password --gecos '' ubuntu

COPY . /home/ubuntu
WORKDIR /home/ubuntu

CMD ["bash"]
