.. _hello_burst:

Hello Burst!
============

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
