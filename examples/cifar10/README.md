# burst example: CIFAR-10 CNN model
=======

# CIFAR-10

CIFAR-10 is a benchmark dataset for computer vision.  The dataset has low-resolution (32 x 32) color images of 10 different categories of items (mostly animals and vehicles).  The CIFAR-10 dataset is described in detail here: https://www.cs.toronto.edu/~kriz/cifar.html.

# This example

This example is a Pytorch implementation neural nets trained to classify the CIFAR-10 dataset using a convolutional neural net (CNN).
This test model achieves ~90% accuracy on this dataset, as implemented here. 

The example is implemented two ways: 
* as a command-line python script that can be run remotely through `burst` (data visualizations are written into an `output` folder)
* in interactive Jupyter notebooks, with in-notebook visualizations

`burst` can support both types of model training.

# Running the example on a local machine

First, set up a virtual environment (instructions are [here](https://realpython.com/python-virtual-environments-a-primer/)).  In the virtual environment, run 

    pip install -r requirements.txt

to ensure that you have the correct versions of all necessary Python packages.

Then, run the command line examples with 

    python3 trainCNN_CIFAR10.py 
    
The output should look something like [this](https://github.com/genevievegraves/burst/blob/main/examples/cifar10/readme_images/local_run.png).  The default only trains for 2 epochs, which produces a poor (underfit) model, but is good for quick testing purposes, especially when you are running on a low-power CPU where each epoch can take minutes to run.  

You can experiment with running for more epochs by specifying `--nepochs` at the command line, e.g., 

    python3 trainCNN_CIFAR10.py --nepochs 40
    
You can also open the `CIFAR10_CNN.ipynb` notebook and run the model there.

Note that the first time you run the command line tool or notebook, it will download the CIFAR-10 dataset to your local drive.  Subsequent runs will make use of the previously downloaded data.

The command line code will create an `output/` file and store the following visualizations there:

* `training_example_images.png` -- This shows one example image for each classification category.
* `model_losses.png` -- This plots the loss per epoch from the model training loop, for both the training data and test data.
* `confusion_matrix.png` -- This show a heat map of the confusion matrix, so that you can visualize how well your model is doing and understand what types of categories it tends to confuse with one another.
* `wrong_examples.png` -- This shows several examples of test images that the model categorized incorrectly.  It's a good sanity check of what types of images tend to be difficult for your model.
* `model_log.txt` -- a log version of what is printed to the screen during runtime, including model structure, timing, and accuracy specifications.

If you run the Jupyter notebook, these same visualizations appear in the notebook, rather than being saved as output files.

# Running command line examples using burst

To run the command line examples using burst, use

    burst python3 trainCNN_CIFAR10.py --nepochs 40

The output should look something like [this](https://github.com/genevievegraves/burst/blob/main/examples/cifar10/readme_images/burst_run.pdf).  The first time you run burst, it will spin up a new server.  This will take several minutes.  It takes several more minutes to build the Docker container, as it downloads and installs all the required software and python packages.  On subsequent runs, starting with a running server or a stopped server, this initial set-up time will be negligible.  If you change `requirements.txt` between runs, the Docker container will take some time to rebuild itself on the next `burst` run.

When `burst` has finished running training and running your model, it will automatically transfer the output and any modified files back to your local directory and close the connection.  Once a `burst` connection has been closed for > 15 minutes, it will stop the remote server so that you will not be paying for it.

You can inspect the output files that have been transferred back to your local machine.

# Running examples in Jupyter using burst

Sometimes it is useful to be able to have an entire Jupyter notebook running on a GPU, while you are experimenting with a new model, so that the run time is fast while you are developing.  `burst` can support remote Jupyter notebooks for real-time model experimentation on a GPU.  

To run a remote Jupyter server through `burst`, use

    burst -p 8888 jupyter lab --ip 0.0.0.0 --allow-root
    
The screen will then display a URL, which will look something like

    http://0.0.0.0:8888/lab?token=f60aaf215e2bd8a92015f732388e16b6407181aaca4a1a9a

Paste this URL into a new browser window.  This will load a JupyterLab window that is running on the remote `burst` server.

Edit and run the Jupyter notebook, just as you would on a local Jupyter server.  You should notice that it can access the GPU, and that the training epochs run much faster on the remote GPU than on a local CPU.

NOTE: When you are done, *you must manually close the Jupyter server* by returning to the window where you launched it and hitting Ctl-C, then responding 'y' to shutdown the server.  *If you leave the Jupyter server running, you will continue to pay for the remote server, even if no code is being executed.  `burst` will not automatically stop a remote Jupyter server.*

# Timing benchmarks

On an AWS test CPU with modest capacity, training this CNN takes ~5 minutes / epoch.  On a laptop (2020 MacBook Air, M1 chip using Rosetta 2), training this CNN takes ~8.5 minutes / epoch (see the local run example [here](https://github.com/genevievegraves/burst/blob/main/examples/cifar10/readme_images/local_run.png)).  

Running through `burst` on an AWS g4dn.xlarge GPU machine, the model trains in ~14 seconds / epoch, for a ~20-40x speed-up (see the burst example [here](https://github.com/genevievegraves/burst/blob/main/examples/cifar10/readme_images/burst_run.pdf)).  This CNN has ~2.4 million free parameters to train.  

Simpler networks will train faster and may show less speed-up when moving to the GPU.
