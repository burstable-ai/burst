FROM burstableai/burst_base:ubu2004

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
RUN bash ~/miniconda.sh -b -p $HOME/miniconda

ENV PATH "/root/miniconda/bin/:$PATH$"
ENV PYTHONPATH "/home/burst/work"

RUN conda install pytorch torchvision numpy matplotlib scikit-learn
RUN conda install -c forge pytorch-model-summary

CMD ["/bin/bash"]