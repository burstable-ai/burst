.. _your_python_project_page:

Your Python Project
===================

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
