FROM burstableai/burst_base:ubu2004

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
RUN bash ~/miniconda.sh -b -p $HOME/miniconda

ENV PATH "/root/miniconda/bin/:$PATH$"
ENV PYTHONPATH "/home/burst/work"

RUN conda install -c conda-forge numpy matplotlib scikit-learn pytorch-gpu torchvision jupyterlab
RUN pip install torchsummary gputil

CMD ["/bin/bash"]