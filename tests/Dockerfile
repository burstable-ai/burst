FROM burstableai/burst_base:latest

RUN apt-get update && apt-get install wget

RUN wget https://github.com/rclone/rclone/releases/download/v1.53.1/rclone-v1.53.1-linux-amd64.deb
RUN dpkg --install rclone-v1.53.1-linux-amd64.deb

CMD ["/bin/bash"]
