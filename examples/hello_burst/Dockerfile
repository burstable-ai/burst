FROM burstableai/burst_base:latest
WORKDIR /home/burst/work

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends wget nginx

RUN wget https://github.com/rclone/rclone/releases/download/v1.53.1/rclone-v1.53.1-linux-amd64.deb
RUN dpkg --install rclone-v1.53.1-linux-amd64.deb

CMD ["/bin/bash"]
