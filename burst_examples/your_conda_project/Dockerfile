########################################################################################
# Set up burst and conda (you shouldn't need to modify these!)
########################################################################################

FROM burstableai/burst_base:ubu2004

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
RUN bash ~/miniconda.sh -b -p $HOME/miniconda

ENV PATH "/root/miniconda/bin/:$PATH$"
ENV PYTHONPATH "/home/burst/work"

########################################################################################
# Install conda packages needed for your project -- MODIFY AS NEEDED
#
#    Make sure you put all conda packages in the same install line, so that the conda
#    package solver is able to work its magic!
########################################################################################

#----------------------------
# Install packages from conda
#----------------------------

RUN conda install -c conda-forge numpy matplotlib jupyterlab

#------------------------------------------------------------------------------------------
# Use pip to install any packages that are available through the pypi server, but not conda
#     (for this example, there are none so the line is commented out, but the CIFAR10_conda
#      example needs torchsummary)
#------------------------------------------------------------------------------------------

# RUN pip install torchsummary 

########################################################################################
# Launch bash shell on new server (you shouldn't need to modify this!)
########################################################################################

CMD ["/bin/bash"]