.. _examples_page:

===============
Examples 
===============

.. ............................................................................................................
..
..  Explanation of how to get the examples, and a list of all examples with links lower in the page.
..
.. ............................................................................................................

   
Download the examples
=====================

Several test examples are available in the burst gitHub repo `here <https://github.com/burstable-ai/burst>`_.  Download the repo.  The examples can be found in the ``burst_examples`` folder.

Burst Examples:
---------------

:ref:`Hello Burst!<ex_hello_burst>`
  This simple example illustrates how to use ``burst`` to launch a GPU, verify the hardware available, and then shut down the server.

:ref:`CIFAR-10: A CNN for Image Recognition<ex_cifar10>`
  This example uses Pytorch to train a Convolutional Neural Net (CNN) for image classification on the benchmark CIFAR-10 computer vision dataset. 
  
:ref:`Your Python Project<ex_your_python_project>`
  If your project is a pure Python project, you should be able to get it running through burst using the simple templates provided here.

----------------------------

.. ............................................................................................................
..
.. The simplest "Hello Burst" example, including basic info on how to set up and run burst for the first time
..
.. ............................................................................................................

.. _ex_hello_burst:
Hello Burst!
=============

Build & test a simple burst environment: 
-----------------------------------------------------

``cd`` into the ``burst_examples/hello_burst/`` directory. You should see a file called ``hello_burst.py``.

Make sure Docker is running:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Docker daemon must be running in the background to use burst. Test to make sure it is running and that you have the correct version:
::

    docker --version

It should return something like:
::

    Docker version 19.03.12, build 48a66213fe

Build the burst environment:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::
   
    burst build --gpu

This may take several minutes; be patient. After some output, you should see this:
::

    ---------------------OUTPUT-----------------------
    Build phase 1 success
    ----------------------END-------------------------
    Synchronizing folders
    receiving file list ... 
    7 files to consider

    sent 43 bytes  received 159 bytes  134.67 bytes/sec
    total size is 1911  speedup is 9.46

    Build phase 2 success
    DONE

Run a command on the remote server:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::
   
    burst run python3 hello_burst.py

The response should look like this:
::

    ---------------------OUTPUT----------------------- 
    Welcome burstables! You're running a virtual machine with 4 cpus
    The following GPUs are available:
    Tesla T4
    ----------------------END-------------------------
    burst: DONE


Stopping or terminating the remote server:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After 15 minutes of inactivity, the remote server will automatically be stopped so that you are not paying for compute power you are not using.  You can check that this has indeed occured by listing the servers associated with your account.

::

   burst list-servers

The response will show your current server and its status.  A running server looks like this:

::
   
   ~$ burst list-servers
   -------------------------------------------------------------                                              
   Sessions with config graves_aws & user burst-graves:
   IMAGE: ami-0c3d256527de69215 STATE: running IPs: ['34.217.124.164'] ID: EC2/i-0ee0a62fe4e437bc5
   Time: 2021/06/30 21:17:30 utc Stop: 2021/06/30 22:14:10 utc in 3400 sec

   -------------------------------------------------------------

Once the server has stopped, listing the server will reflect that stopped status:

::
   
   ~$ burst list-servers
   -------------------------------------------------------------                                              
   Sessions with config graves_aws & user burst-graves:
   IMAGE: ami-0c3d256527de69215 STATE: stopped IPs: [] ID: EC2/i-0ee0a62fe4e437bc5
   -------------------------------------------------------------

Rather than waiting 15 minutes for the server to stop itself, you can also manually stop the server with the command

::
   
   burst stop


----------------------------

.. ............................................................................................................
..
.. The CIFAR-10 example
..
.. ............................................................................................................

.. _ex_cifar10:
CIFAR-10: Train a CNN for Image Recognition
===========================================

The CIFAR-10 Dataset
----------------------

CIFAR-10 is a benchmark dataset for computer vision. The dataset has low-resolution (32 x 32) color images of 10 different categories of items (mostly animals and vehicles). The CIFAR-10 dataset is described in detail here: `www.cs.toronto.edu/~kriz/cifar.html <https://www.cs.toronto.edu/~kriz/cifar.html>`_

This example
------------

This example is a Pytorch implementation neural nets trained to classify the CIFAR-10 dataset using a convolutional neural net (CNN). This test model achieves ~90% accuracy on this dataset, as implemented here.

The example is implemented as a command-line python script that can be run remotely through burst.  Data visualizations are written into an output folder.  This example is in the ``burst_examples/cifar10/`` directory from the unpacked tarball.

``conda`` users
^^^^^^^^^^^^^^^^

If you typically use ``conda`` to manage your virtual environment and package versioning, try ``burst_examples/cifar10_conda/`` instead.  All burst commands will work exactly the same, but the provided ``Dockerfile``, ``.burstignore``, and ``.dockerignore`` will be better templates for you use as a starting point for your own projects.


Run the example on a local machine
----------------------------------

*NOTE: this can take a while to run, first because you have to download the ~200Mb CIFAR-10 image dataset, and then because most local machines will not be set up to use the GPU. Feel free to skip this step and go straight to* `Run from the command line using burst`_.

Set up a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, we need to set up a virtual environment, activate it, and install the necessary package versions.  If you use ``venv``, ``virtualenv``, or ``pyenv`` to manage your python environments, follow the instructions for ``venv`` users below.  If you use ``conda`` or ``Anaconda`` to manage your python environments, follow the instructions for ``conda`` users.

``venv`` users
^^^^^^^^^^^^^^

``cd`` into the ``burst_examples/cifar10/`` directory and do the following:
::

    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

to ensure that you have the correct versions of all necessary Python packages.

``conda`` users
^^^^^^^^^^^^^^^

``cd`` into the ``burst_examples/cifar10_conda/`` directory and do the following:
::

    conda create --name cifar python=3.8
    [WINDOWS:] activate cifar
    [LINUX, macOS:] source anaconda3/bin/activate cifar
    conda install -c conda-forge numpy matplotlib scikit-learn torchvision jupyterlab
    pip install torchsummary

to ensure that you have the correct versions of all necessary Python packages.


Run the example locally without burst
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Then, run the command line examples with
::

    python3 trainCNN_CIFAR10.py 

The output should look something like this (shortened):
::

    graves@pescadero ~/g/v/s/b/e/cifar10> python3 trainCNN_CIFAR10.py
    Loading CIFAR dataset...
    Downloading https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz to ./cifar-10-python.tar.gz
    100.0%Extracting ./cifar-10-python.tar.gz to .
    Files already downloaded and verified
    GPU is available?: False
    Using device: cpu
    Training NN through 2 epochs.  Start time: 2021-02-18 15:07:09.813288
    Iteration   0, avg train_loss = 1.360, avg test_loss = 1.034,1 epoch duration: 0:08:47.014887
    Iteration   1, avg train_loss = 0.961, avg test_loss = 0.802,1 epoch duration: 0:08:56.699187
    Done training.
    ---------------------------------------
    Training set accuracy: 0.7123
    Test set accuracy: 0.7269
    ------------- Test Set: ---------------
    # Correct predictions: 7269
    # Wrong predictions: 2731
    ---------------------------------------
    .
    .
    .
    stdout flushed
    stderr flushed
    graves@pescadero ~/g/v/s/b/e/cifar10>

   
The default only trains for 2 epochs, which produces a poor (underfit) model, but is good for quick testing purposes, especially when you are running on a low-power CPU where each epoch can take 5-10 minutes to run.

You can experiment with running for more epochs by specifying ``--nepochs`` at the command line, e.g.,
::

    python3 trainCNN_CIFAR10.py --nepochs 40

You can also open the ``CIFAR10_CNN.ipynb`` notebook and run the model there.

Note that the first time you run the command line tool or notebook, it will download the CIFAR-10 dataset to your local drive. Subsequent runs will make use of the previously downloaded data.

The command line code will create an ``output/`` directory and store the following visualizations there:

  * ``training_example_images.png`` -- This shows one example image for each classification category.
  * ``model_losses.png`` -- This plots the loss per epoch from the model training loop, for both the training data and test data.
  * ``confusion_matrix.png`` -- This show a heat map of the confusion matrix, so that you can visualize how well your model is doing and understand what types of categories it tends to confuse with one another.
  * ``wrong_examples.png`` -- This shows several examples of test images that the model categorized incorrectly. It's a good sanity check of what types of images tend to be difficult for your model.
  * ``model_log.txt`` -- a log version of what is printed to the screen during runtime, including model structure, timing, and accuracy specifications.

If you run the Jupyter notebook, these same visualizations appear in the notebook, rather than being saved as output files.

Run from the command line using burst
-------------------------------------

First, make sure your burst build is working and ready to use, by running
::

    burst build --gpu

inside your project directory. If you encounter problems, try ramping up the verbosity for more granular feedback, e.g.
::

    burst build --gpu --verbose 127

(Note: 127 is maximum verbosity).

Once the burst build is working, run the command line examples using burst:
::

    burst run python3 trainCNN_CIFAR10.py --nepochs 40

The output should look something like this:
::

    graves@pescadero ~/g/v/s/b/e/cifar10> burst run python3 trainCNN_CIFAR10.py --nepochs 40
    burst: Session: burst-graves                                                                             
    burst: Starting server                                                                                   
    burst: server state:pending                                                                              
    burst: server state:running                                                                              
    burst: Waiting for public IP address to be assigned                                                      
    burst: Connecting through ssh                                                                            
    burst: Starting monitor process for shutdown++                                                           
    burst: Removing topmost layer                                                                            
    burst: burst: name burst-graves size g4dn.xlarge image Deep Learning AMI (Ubuntu 18.04) Version 36.0 url 
    burst: Synchronizing project folders                                                                     
    burst: Building docker container                                                                         
    burst: Running docker container                                                                          
    burst:                                                                                                   
    ---------------------OUTPUT-----------------------
    Loading CIFAR dataset...
    Files already downloaded and verified
    Files already downloaded and verified
    GPU is available?: True
    Using device: cuda:0
    Training NN through 40 epochs.  Start time: 2021-02-18 23:42:55.319599
    Iteration   0, avg train_loss = 1.322, avg test_loss = 1.085,1 epoch duration: 0:00:14.692214
    Iteration   1, avg train_loss = 0.962, avg test_loss = 0.828,1 epoch duration: 0:00:13.578531
    Iteration   2, avg train_loss = 0.815, avg test_loss = 0.730,1 epoch duration: 0:00:13.301335
    Iteration   3, avg train_loss = 0.732, avg test_loss = 0.677,1 epoch duration: 0:00:13.297348
    Iteration   4, avg train_loss = 0.671, avg test_loss = 0.646,1 epoch duration: 0:00:13.757426
    Iteration   5, avg train_loss = 0.630, avg test_loss = 0.624,1 epoch duration: 0:00:13.326413
    .
    .
    .
    .
    .
    Iteration  35, avg train_loss = 0.270, avg test_loss = 0.485,1 epoch duration: 0:00:13.413512
    Iteration  36, avg train_loss = 0.263, avg test_loss = 0.501,1 epoch duration: 0:00:13.411721
    Iteration  37, avg train_loss = 0.266, avg test_loss = 0.485,1 epoch duration: 0:00:13.283547
    Iteration  38, avg train_loss = 0.254, avg test_loss = 0.470,1 epoch duration: 0:00:13.476122
    Iteration  39, avg train_loss = 0.249, avg test_loss = 0.470,1 epoch duration: 0:00:13.343224
    Done training.
    ---------------------------------------
    Training set accuracy: 0.9195
    Test set accuracy: 0.8635
    ------------- Test Set: ---------------
    # Correct predictions: 8635
    # Wrong predictions: 1365
    ---------------------------------------
    .
    .
    .
    stdout flushed
    stderr flushed
    ----------------------END-------------------------
    burst: Synchronizing folders                                                                             
    burst: DONE                                                                                                
    graves@pescadero ~/g/v/s/b/e/cifar10> 

The first time you run burst, it will spin up a new server. This will take several minutes. It takes several more minutes to build the Docker container, as it downloads and installs all the required software and python packages. On subsequent runs, starting with a running server or a stopped server, this initial set-up time will be negligible. If you change ``requirements.txt`` between runs, the Docker container will take some time to rebuild itself on the next burst run.

When burst has finished running training and running your model, it will automatically transfer the output and any modified files back to your local directory and close the connection. Once a burst connection has been closed for > 15 minutes, it will stop the remote server so that you will not be paying for it.

You can inspect the output files that have been transferred back to your local machine, which can be found in the ``output/`` directory.

Run in a Jupyter Notebook on a GPU
----------------------------------

If you prefer working in Jupyter notebooks to running python scripts from the command line, you can use burst to launch a JupyterLab server on a remote GPU-enabled cloud machine.

As with the commandline workflow, start by building the project:

::

   burst build --gpu --verbose 1

Once you have a working build, instead of using ``burst run`` to launch the project, instead use burst to launch a remote JupyterLab session:

::

   burst jupyter

You should see output similar to this (abbreviated):

::
   
   graves@pescadero ~/b/e/t/b/b/cifar10> burst jupyter
   ---------------------OUTPUT-----------------------
   ...
   [I 2021-07-07 17:56:44.308 ServerApp] Serving notebooks from local directory: /home/burst/work
   [I 2021-07-07 17:56:44.308 ServerApp] Jupyter Server 1.9.0 is running at:
   [I 2021-07-07 17:56:44.308 ServerApp] http://81f5151ba045:8888/lab
   [I 2021-07-07 17:56:44.308 ServerApp]  or http://127.0.0.1:8888/lab
   [I 2021-07-07 17:56:44.308 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).

Cut and paste the URL provided (e.g., ``http://127.0.0.1:8888/lab``) into a web browser, and it should load the JupyterLab environment.

Open the ``CIFAR10_CNN.ipynb``.  You can step through the notebook one cell at a time to train and test a convolutional neural net.  Notice in Cell [5] that the notebook is indeed running on a GPU, with CUDA enabled.  

When you are done running the notebook, stop the JupyterLab server with ``Ctl-C``.

**NOTE: You must Ctl-C to stop the server when you are done, or the server will keep running and you will keep being charged.  There is no automatic time-out or shut-down (yet) for** ``burst jupyter``.


Timing benchmarks
-----------------

On an AWS test CPU with modest capacity, training this CNN takes ~5 minutes / epoch. On a laptop (2020 MacBook Air, M1 chip using Rosetta 2), training this CNN takes ~8.5 minutes / epoch (see the local run example above).

Running through burst on an AWS g4dn.xlarge GPU machine, the model trains in ~14 seconds / epoch, for a ~20-40x speed-up (see the burst example above). This CNN has ~2.4 million free parameters to train.

Simpler networks will train faster and may show less speed-up when moving to the GPU.


----------------------------

.. ............................................................................................................
..
.. Your Python Project:
..     Example with templates to help users create their own burst project
..
.. ............................................................................................................

.. _ex_your_python_project:
Your Python Project
====================



Run your own Python project
---------------------------

If your project is a pure Python project, you should be able to get it running through burst using some simple templates.

``venv`` projects:
^^^^^^^^^^^^^^^^^^

If you use ``virtualenv``, ``venv``, or ``pyenv`` and a ``requirements.txt`` file to manage your Python environment and do package version control, you should use the templates in ``burst_examples/your_python_project/`` as a starting point.  (We will hereafter refer to these projects as ``venv`` proejcts, where ``venv`` should be understood to include projects managed with ``venv``, ``virtualenv`` or ``pyenv``.)

``conda`` projects:
^^^^^^^^^^^^^^^^^^^

If you use ``Anaconda`` or ``conda`` to manage your Python environment and packages, you should use the templates in ``burst_examples/your_conda_project/`` as a starting point.


Required files
--------------

Every Python ``burst`` project requires the following files:

* ``.dockerignore``
* ``.burstignore``
* ``Dockerfile``

In addition, ``venv`` projects will need:

* ``requirements.txt``

Template versions of all of these files are included in the ``your_python_project/`` and ``your_conda_project/`` directories.  For most pure python projects, the ``.dockerignore``, and ``.burstignore`` files included here will work out of the box.  The only files you will need to modify are the ``requirements.txt`` file (for ``venv`` projects) or the ``Dockerfile`` (for ``conda`` projects).  The ``Dockerfile`` for ``venv`` projects should work out of the box without modifications.

Specifying python packages and versions
---------------------------------------

``venv`` projects:
^^^^^^^^^^^^^^^^^^

For ``venv`` projects, this is done in the ``requirements.txt`` file, which needs to specify the correct version of each python package you need to install in order to run your project.  These will typically be the packages that you import at the top of your python script or Jupyter notebook.

If you used ``pip3`` to install packages, either in a virtual environment or directly into your main programming environment, you can see which version of each package is installed by running

::
   
   pip3 freeze

at the command line.  Specify these versions in your ``requirements.txt`` file, following the example format included in the template ``requirements.txt`` here.  


``conda`` projects:
^^^^^^^^^^^^^^^^^^^

If you use ``conda`` to manage your python packages, the ``conda`` package solver will take responsibility for finding a set of mutually-compatible package versions, so you do not need to specify version numbers.  Simply edit the ``Dockerfile`` in ``your_conda_project/`` to install the packages you need for your project (see the template ``Dockerfile`` for the example format).


Setting up your project
-----------------------

Make sure you have all supporting data files and \*.py files in the directory with your project.  ``Burst`` will transfer all files in the directory from which it is called (except for those specified in the ``.burstignore``!).

Then, make sure your burst build is working and ready to use, by running

::

   burst build --gpu

inside your project directory.  If you encounter problems, try ramping up the verbosity for more granular feedback, e.g. 

::

   burst build --gpu --verbose 127
	
(Note: 127 is maximum verbosity).

Running command line examples using burst
-----------------------------------------

To run the command line example using burst, use

::

   burst run python3 template.py --verbose 1

The output should look something like this:

::
   
   graves@pescadero ~/g/v/s/b/e/your_python_project> burst run python3 template.py --verbose 1
   Session: burst-graves
   Waiting for sshd
   Connecting through ssh
   Killing shutdown processes: ['53aaf212b1e6']
   Removing topmost layer
   burst: name burst-graves size g4dn.xlarge image Deep Learning AMI (Ubuntu 18.04) Version 36.0 url 34.222.154.210
   Synchronizing project folders
   building file list ... 
   11 files to consider

   sent 306 bytes  received 20 bytes  217.33 bytes/sec
   total size is 31518  speedup is 96.68
   Building docker container
   Running docker container

   ---------------------OUTPUT-----------------------
   0 * 0 = 0
   1 * 1 = 1
   2 * 2 = 4
   3 * 3 = 9
   4 * 4 = 16
   5 * 5 = 25
   6 * 6 = 36
   7 * 7 = 49
   8 * 8 = 64
   9 * 9 = 81
   ----------------------END-------------------------
   Synchronizing folders
   receiving file list ... 
   11 files to consider
   example.png
   10811 100%   10.31MB/s    0:00:00 (xfer#1, to-check=4/11)

   sent 134 bytes  received 356 bytes  326.67 bytes/sec
   total size is 31518  speedup is 64.32
   Scheduling shutdown of VM at 34.222.154.210 for 900 seconds from now
   DONE

   graves@pescadero ~/g/v/s/b/e/your_python_project> 


You can suppress most of the ``burst`` information by not specifying ``verbose``, e.g., ``burst run python3 template.py``.  You can get maximum verbosity with ``--verbose 127``.

The first time you run ``burst``, it will spin up a new server.  This will take several minutes.  It takes several more minutes to build the Docker container, as it downloads and installs all the required software and python packages.  On subsequent runs, starting with a running server or a stopped server, this initial set-up time will be negligible.  If you change the ``Dockerfile`` or ``requirements.txt`` between runs, the Docker container will take some time to rebuild itself on the next ``burst`` run.

When ``burst`` has finished running your project, it will automatically transfer any modified files back to your local directory and close the connection.  Once a ``burst`` connection has been closed for > 15 minutes, it will stop the remote server so that you will not be paying for it.

You can inspect the output files that have been transferred back to your local machine.


Run in a Jupyter Notebook on a GPU
----------------------------------

If you prefer working in Jupyter notebooks to running python scripts from the command line, you can use burst to launch a JupyterLab server on a remote GPU-enabled cloud machine.

As with the commandline workflow, start by building the project:

::

   burst build --gpu --verbose 1

Once you have a working build, instead of using ``burst run`` to launch the project, instead use burst to launch a remote JupyterLab session:

::

   burst jupyter

You should see output similar to this (abbreviated):

::

   graves@pescadero ~/b/e/t/b/b/your_python_project> burst jupyter
   ---------------------OUTPUT-----------------------                                                         
   ...
   [I 18:25:03.878 LabApp] Jupyter Notebook 6.4.0 is running at:
   [I 18:25:03.879 LabApp] http://127.0.0.1:8888/lab
   [I 18:25:03.879 LabApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).

Cut and paste the URL provided (e.g., ``http://127.0.0.1:8888/lab``) into a web browser, and it should load the JupyterLab environment.

Open the ``Template.ipynb`` notebook.  You can step through the notebook one cell at a time, or modify the notebook to do other operations.

When you are done running the notebook, stop the JupyterLab server with ``Ctl-C``. Any saved files will be automatically transferred back to your local directory by burst when the server is shut down.

**NOTE: You must Ctl-C to stop the server when you are done, or the server will keep running and you will keep being charged.  There is no automatic time-out or shut-down (yet) for** ``burst jupyter``.
