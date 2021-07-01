.. _cifar10:

CIFAR-10: Train a CNN for Image Recognition
===========================================

CIFAR-10
--------

CIFAR-10 is a benchmark dataset for computer vision. The dataset has low-resolution (32 x 32) color images of 10 different categories of items (mostly animals and vehicles). The CIFAR-10 dataset is described in detail here: `www.cs.toronto.edu/~kriz/cifar.html <https://www.cs.toronto.edu/~kriz/cifar.html>`_

This example
------------

This example is a Pytorch implementation neural nets trained to classify the CIFAR-10 dataset using a convolutional neural net (CNN). This test model achieves ~90% accuracy on this dataset, as implemented here.

The example is implemented as a command-line python script that can be run remotely through burst.  Data visualizations are written into an output folder.  This example is in the ``burst_examples/cifar10/`` directory from the unpacked tarball.

If you typically use ``conda`` to manage your virtual environment and package versioning, try ``burst_examples/cifar10_conda/`` instead.


Run the example on a local machine
----------------------------------

*NOTE: this can take a while to run, first because you have to download the ~200Mb CIFAR-10 image dataset, and then because most local machines will not be set up to use the GPU. Feel free to skip this step and go straight to* `Run from the command line using burst`_.

First, we need to set up a virtual environment, activate it, and install the necessary package versions.

``cd`` into the ``burst_examples/cifar10/`` directory and do the following:
::

    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

to ensure that you have the correct versions of all necessary Python packages.

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

Timing benchmarks
-----------------

On an AWS test CPU with modest capacity, training this CNN takes ~5 minutes / epoch. On a laptop (2020 MacBook Air, M1 chip using Rosetta 2), training this CNN takes ~8.5 minutes / epoch (see the local run example above).

Running through burst on an AWS g4dn.xlarge GPU machine, the model trains in ~14 seconds / epoch, for a ~20-40x speed-up (see the burst example above). This CNN has ~2.4 million free parameters to train.

Simpler networks will train faster and may show less speed-up when moving to the GPU.
