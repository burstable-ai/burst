Examples 
========

Download the examples:
----------------------

Download the examples tarball from here: `burst_examples <https://burstable.ai/static/burst_examples.tgz>`_

Build & test a simple burst environment: Hello Burst!
-----------------------------------------------------

Unpack the examples tarball and cd into the ``burst_examples/hello_burst/`` directory. You should see a file called ``hello_burst.py.``

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

Train a CNN for Image Classification
------------------------------------

We recommend walking through the CIFAR-10 example, which uses Pytorch to train a Convolutional Neural Net (CNN) for image classification on the benchmark CIFAR-10 computer vision dataset. This example also illustrates how to use burst to run a Jupyter notebook on a remote GPU, for real-time model building and manipulation on a GPU.

This example is in the ``burst_examples/cifar10/`` directory from the unpacked tarball.

Run your own Python project
---------------------------

If your project is a pure Python project, you should be able to get it running through burst using some simple templates.

These are in the ``burst_examples/your_python_project/`` directory from the unpacked tarball.


Run your own Python project (conda)
-----------------------------------

If you use ``conda`` to manage your virtual environment and Python packages, use the ``burst_examples/your_
