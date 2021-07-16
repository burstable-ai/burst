.. _user_guide_page:

============
User Guide
============

* :ref:`ug_setup_project`
* :ref:`ug_build`
* :ref:`ug_run`
* :ref:`ug_jupyter`
* :ref:`ug_background`
* :ref:`ug_status`
* :ref:`ug_configuration`
* :ref:`ug_help`
* :ref:`ug_actions`
* :ref:`ug_options`

-------------------------------------------------------------------------

.. _ug_setup_project:

Setting up a project
==================================

A burst project, including its server configuration and support files, is tied to a project folder.  The folder needs to contain all of the files required to run your project---all supporting scripts and files, any input data, etc.  These are the files that will be "burst" to the cloud server and used there.  

It also needs to contain the following files for burst to operate:

* ``.burstignore``
* ``.dockerignore``
* ``Dockerfile``

If you use ``Anaconda`` or ``conda`` to manage your python environment, those files are all you need.  If you use ``venv``, ``virtualenv``, or ``pyenv`` to manage your python environment, you will also need:

* ``requirements.txt``
  
The easiest way to set up a project to run with burst is to download and copy the template versions for all of these files from the "Your Python Project" example in :ref:`examples_page`.  There are instructions in that example for both ``venv`` and ``conda`` style projects, and to explain how to modify the template files to include the python packages that are part of your project.

If you are already a Docker ninja, feel free to roll your own Dockerfile.  If, like some of us, you "treasure your ignorance" of Docker, these templates should get you where you need to be, for a project based in pure python.  

-------------------------------------------------------------------------

.. _ug_build:

The Basics: Build
==================================

Within a burst project directory, there are multiple "actions" that can be taken.  Once you have set up a cloud compute account (see `Configuration`_ below), the most common sequence of actions will be to build the project and then to run it on a remote server:

::
   
   burst build [--gpu | --no-gpu] [--verbose 1] [options]
   burst run [options] <command>

Building a project
--------------------

::

   burst build [--gpu | --no-gpu] [--verbose 1]

This command spins up your cloud hardware, launches a Docker container on the remote machine, and installs everything in the container you need to run your project.

A build **requires** you to specify whether you want a GPU machine (``--gpu``) or not (``--no-gpu``)---if you do not specify, you will get an error.

The build process may take several minutes; be patient.  If you are the kind of person who likes to watch the paint dry because it gives you comfort that something is happening, you can ramp up the verbosity with ``--verbose 255`` (255 is maximum verbosity---don't ask why, it just is).

NOTE: Once a project is successfully built, you will not have to wait through the build process again, even if your cloud server is stopped and you come back to it hours or days later.  You only have to wait through a build when launching a completely new server or project, or when you have made substantial changes to the ``Dockerfile`` and/or ``requirements.txt`` file.  

After some output, you should see something like this:

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

If you get an error, or something very different from this, something has likely gone wrong with your various installations in the Docker container.  Ramp up the verbosity (if you hadn't already) and run it again in the hopes of getting a useful error message:

::

   burst build --gpu --verbosity 127

Try to fix your ``Dockerfile`` and/or your ``requirements.txt`` file to deal with these problems.  If you get desperate, email help@burstable.ai.

.. _ug_build_options:

Build options
^^^^^^^^^^^^^

``--gpu | --no-gpu``
  The only required build option is to specify whether or not to use the GPU or CPU VM defined in the current compute service.  You must specify one or the other.

``--verbose NUMBER``, or ``-v NUMBER``
  You can control the verbosity of output with:
  ::

     burst build --gpu --verbose NUMBER

  Where -1 suppresses all output except for the task; 0 prints status on a single line (the default); 1 prints status, and numbers 2-255 are increasingly more verbose.  ``burst build`` defaults to ``--verbose 9``, to give the user feedback when build issues are encountered.  Use ``--verbose 127`` if your build is failing, to help diagnose problems.

``--session-name NAME``
  Specify a name for this burst project.  Default is "``burst-$USER``".  If you want to run more than one burst project *at the same time*, you will need to give them different session names and refer to the session by name when building or running commands.

``--docker-file FILE``
  Specify a Dockerfile to use for the build (default is local ``./Dockerfile``)

``--docker-port PORT``
  Specify the local port to use for remote Docker.

``--pubkey-file FILE``
  Specify a public key file for burst to use when communicating securely with remote server.  Default is ``~/.ssh/id_rsa.pub``.  If you specify a different file, it must still be located in ``~/.ssh/``.  **DO NOT SEND PRIVATE KEYS.  EVER.  TO ANYONE.**

``--vm-username NAME``
  If you are using a operating system other than Ubuntu on your remote VM, you need to specify the default username for that operating system distribution (default assumes Ubuntu with username "``ubuntu``"). 
  
``[various compute set-up options]``
  There are a number of command line options that specify aspects of the cloud compute set-up.  All of them are optional, because the build defaults to the cloud compute configuration in the ``~/.burst/config.yml`` file that was created during interactive configuration (see :ref:`ug_configuration` below).

  The list of build options for cloud configuration are explained in detail in :ref:`ug_configuration` and include:

  * ``--compute-access``
  * ``--compute-provider``
  * ``--compute-region``
  * ``--compute-secret``
  * ``--compute-service``
  * ``--config-file``
  * ``--disksize``
  * ``--gcs-project``
  * ``--storage-service``
  * ``--vm-image``
  * ``--vm-type``
  

-------------------------------------------------------------------------

.. _ug_run:

The Basics: Run
==================================

Running a project
-------------------

Once your remote workspace has been built, you are ready to run your project in the cloud.  You do this with a ``burst run`` statement, followed by the command you wish to run remotely.

::
   
   burst run [options] <command>

Any run-time options must be specified **before** the command, otherwise they are assumed to be part of the command itself, rather than a burst option, and are passed on to the Docker container as such.

Here is an example of how you would run the "Hello Burst!" example provided with the burst distribution (see :ref:`examples_page`), including options to control verbosity and to stop the server 10 seconds after it is finished:

::

   burst run --verbose 1 --stop 10 python3 hello_burst.py

The command to be run on the remote server, ``python3 hello_burst.py``, follows the burst action ``burst run`` and its associated options ``--verbose 1 --stop 10``.

.. _ug_run_options:
   
Run options
^^^^^^^^^^^

``--background`` or ``-b``
  A useful option for long processes is to run them in "background" mode.  This allows you to set a process running, then close the connection to the remote server (e.g., shut your laptop and pack it away into your bag), leaving the process running in the cloud.  When the process has finished, the server will automatically go to sleep and stop charging your account.  You can then wake up the server to "sync" and retrieve the output of the process at a later time.  Detailed use of "background mode" is described below in :ref:`ug_background`.  

``--verbose NUMBER``, or ``-v NUMBER``
  As with the ``burst build`` action, you can set the desired verbosity.  0 limits the output only to task output, 1 gives task output and status, and numbers 2-255 are increasingly more verbose (255 is maximum verbosity).  ``burst run`` defaults to ``--verbose 0``.

``--session-name NAME``
  If you built a project with a session name other than the default, you need to provide that same session name to the ``burst run`` command, so that it knows which built server to use.

``--stop SECONDS``
  You can specify a number of seconds to wait after a server becomes idle, before stopping the remote server.  The default is 900 (15 minutes).  0 means never (use this with caution, since you will continue to pay for the server indefinitely, unless you subsequently stop or terminate it manually).  Use the action ``burst stop`` to force stop a server.  See :ref:`ug_status` for more information on actions that stop or terminate a server manually.

``--storage-mount STORAGE_SERVICE:MOUNT``
  If you have configured a cloud storage service and want to use it, this options allows you to mount the cloud service as though it were local to the burst project directory.  You have to specify the storage service you want to use ("STORAGE_SERVICE" should be the alias you gave it during configuration, stored in your ``config.yml`` file) and the folder name to to mount it to ("MOUNT" should be the folder name expected by your software).  
  
``--tunnel-port LOCAL[:REMOTE], -p LOCAL[:REMOTE]``
  If you want to use burst to run a remote server, you can establish a tunnel to that remote server to make it accessible in a local browser window.  This option allows you to specify the local port number, and the remote port number if it is different from the local.
 
.. _ug_jupyter:


Running a remote JupyterLab server
----------------------------------

Jupyter notebooks are a popular way to do R&D work, or even data science in general.  Burst allows you to spin up a remote Jupyter server on any cloud hardware you desire, and to move easily between different hardware configurations.

For example, you may do your initial experimentation in a Jupyter notebook on a cheap, low-power CPU while you are constructing and debugging your process.  This might be your local laptop, or you can use burst to run Jupyter on a cheap cloud server.

Once your model is constructed and debugged, and you are ready to train through many epochs, you can burst the Jupyter server onto an expensive, powerful GPU.  There, you can use it to rapidly train your model, then stop the server and transferred the saved, trained model back to your local machine.  

Start by setting up a project to work with burst, as described in :ref:`ug_setup_project`.  The easiest way to set up a new python project is to use the templates for "Your Python Project" in :ref:`examples_page` to get working versions of the ``Dockerfile``, ``.burstignore``, ``.dockerignore``, and (if relevant) ``requirements.txt`` files you need.

Then, ``burst build`` your project environment, specifying ``--gpu | --no-gpu``.  

Once you have a successful build, you can use burst to launch a remote JupyterLab server with the "jupyter" action:

::

   burst jupyter

This will launch a JupyterLab server on the remote cloud machine and give you a local port on which to access it.  The terminal output should look like this (shortened):

::

   graves@pescadero ~/g/v/s/b/b/your_python_project> burst jupyter
   ---------------------OUTPUT-----------------------                                                         
   ...
   [I 2021-07-09 18:33:38.598 ServerApp] jupyterlab | extension was successfully loaded.
   [I 2021-07-09 18:33:38.598 ServerApp] Serving notebooks from local directory: /home/burst/work
   [I 2021-07-09 18:33:38.598 ServerApp] Jupyter Server 1.9.0 is running at:
   [I 2021-07-09 18:33:38.598 ServerApp] http://4d9dba31c145:8888/lab
   [I 2021-07-09 18:33:38.598 ServerApp]  or http://127.0.0.1:8888/lab
   [I 2021-07-09 18:33:38.598 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).

Open a browser window and use it to connect to the local URL and port provided, e.g.: http://127.0.0.1:8888/lab

This will give you a JupyterLab window running on the remote cloud machine.  In JupyterLab, you can access the shell, Jupyter notebooks, iPython windows, and the local filesystem, all in the browser session.  Develop your code, run your notebook, debug, train your models, and do any other interactive tasks you would normally do.

When you are finished, save your updated notebook(s) and then stop the JupyterLab server by typing ``Control-C`` in the shell that launched the session, typing "y" to confirm shutdown.

By default, a JupyterLab session will be stopped after 15 minutes of idle time, so that you are not paying for a server you are not using.  You can modify the length of time a JupyterLab server is allowed to sit idle with the ``--stop SECONDS`` option.

When the JupyterLab session is stopped or shutdown, all new files that have been written on the remote machine, along with any updated notebooks and files, will be synced back to your local machine automatically.  The remote server will then be stopped automatically after 900 seconds, and you will stop paying for it.  

When you are ready to relaunch JupyterLab, just type

::

   burst jupyter

again.  The server will be woken up, and you will be able to reconnect and pick up where you left off.  You do not need to build again, unless you have changed the ``Dockerfile`` or ``requirements.txt``.

.. _ug_jupyter_options:

Jupyter Options
^^^^^^^^^^^^^^^^^^

``--verbose NUMBER``, or ``-v NUMBER``
  As with the ``burst run`` action, you can set the desired verbosity.  0 limits the output only to task output, 1 gives task output and status, and numbers 2-255 are increasingly more verbose (255 is maximum verbosity).  ``burst jupyter`` defaults to ``--verbose 0``.

``--session-name NAME``
  If you built a project with a session name other than the default, you need to provide that same session name to the ``burst jupyter`` command, so that it knows which built server to use.

``--stop SECONDS``
  You can specify a number of seconds to wait after JupyterLab becomes idle, before stopping the remote server.  The default is 900 (15 minutes).  0 means never (use this with caution, since you will continue to pay for the server indefinitely, unless you subsequently stop or terminate it manually).Use ``Control-C`` in the shell that launched ``burst jupyter``, or the action ``burst stop`` to force stop a server.  See :ref:`ug_status` for more information on actions that stop or terminate a server manually.

-------------------------------------------------------------------------

.. _ug_background:
   
Running in the Background
=========================

A useful option, for tasks that may take a while to complete, is to run a burst command in "background" mode.  This sets the process running on the remote burst server, then detaches from the server and leaves the process running.  Run your process in background mode using the following:

::
   
   burst run --background <command>

or

::
   
   burst run -b <command>

This launches your command, then logs out of the server and returns you to your local terminal prompt.  The remote process will continue until completion.  Then, the remote server will automatically be stopped after it has been idle for 15 minutes.  You can change the stopping time with the option ``--stop SECONDS``.

There are several burst actions that are specifically designed for checking on or managing background processes:

``burst attach``
  Attaches stdin, stdout, and stderr to the remote background process, so you can see the process running, as if you had never logged out.  Ctl-C detaches and returns you to your local prompt.

``burst status``
  Shows the status of the remote tasks if the Docker container is still running, along with information about launch time and run-time so far.

``burst kill``
  Kills the Docker process running on a remote server, but leaves the server active and available to ssh into.

``burst sync``
  When a remote background process is complete, this syncs all of the output files back to your local directory, as burst normally does at the end of a process when not running in background mode.

A typical background workflow might look like this:

1. Build your project workspace on a GPU.

   ::
      
      graves@pescadero ~/g/v/s/b/b/cifar10> burst build --gpu --session-name cifar10
      ...
      Successfully built 6d6baf93e904
      Successfully tagged burst_image:latest
      Running docker container
      ---------------------OUTPUT-----------------------
      Build phase 1 success
      ----------------------END-------------------------
      Synchronizing folders
      receiving file list ...
      ...
      Build phase 2 success
      DONE

2. Train the model on remote GPU in background mode, while your laptop sits closed in your backpack on your commute home from work.

   ::

      graves@pescadero ~/g/v/s/b/b/cifar10> burst run --background --session-name cifar10 python3 trainCNN_CIFAR10.py --nepochs 40
      ---------------------OUTPUT-----------------------                                                         
      Running in background mode. Container = fe2c1838bcb
      ----------------------END-------------------------
      burst: DONE                                                    

3. Check the status of your job when you arrive home.

   ::

      graves@pescadero ~/g/v/s/b/b/cifar10> burst status --session-name cifar10
      -------------------------------------------------------------
      Docker process ID: fe2c1838bcbd
      Status: Up 30 minutes
      Command: "python3 trainCNN_CIFAR10.py --nepochs 40"
      -------------------------------------------------------------


4. Re-attach to the process to watch the training in-progress.

   ::

      graves@pescadero ~/g/v/s/b/b/cifar10> burst attach --session-name cifar10
      ctrl-C only detaches;  'burst kill' to stop                                                             
      ---------------------OUTPUT-----------------------
      Iteration   4, avg train_loss = 0.679, avg test_loss = 0.642,1 epoch duration: 0:00:19.001262
      Iteration   5, avg train_loss = 0.634, avg test_loss = 0.622,1 epoch duration: 0:00:19.051985
      Iteration   6, avg train_loss = 0.598, avg test_loss = 0.620,1 epoch duration: 0:00:19.154618
      ^C----------------------END-------------------------
      
5. Check the status again before bedtime and see that it is done training.

   ::

      graves@pescadero ~/g/v/s/b/b/cifar10> burst status --session-name cifar10
      -------------------------------------------------------------
      No remote host running
      -------------------------------------------------------------

   Note that the remote host has been stopped because it was idle, so I haven't been paying for the machine.

   ::

      graves@pescadero ~/g/v/s/b/b/cifar10> burst list-server --session-name cifar10
      -------------------------------------------------------------
      Sessions with config graves_aws & user cifar10:
      IMAGE: ami-0bc87a16c757a7f07 STATE: stopped IPs: [] ID: EC2/i-0789f55b295a95297
      -------------------------------------------------------------

      
6.  Sync the trained model and files back to your laptop.  Because it has been more than 15 minutes, burst first has to restart the remote machine before it can sync (just takes a few extra seconds).

    ::

       graves@pescadero ~/g/v/s/b/b/cifar10> burst sync --session-name cifar10 -v 9
       Starting server
       server state: stopped
       server state: pending
       server state: running
       Waiting for public IP address to be assigned
       Public IPs: ['54.187.76.64']
       Waiting for sshd
       Connecting through ssh
       burst: name cifar10 vmtype g4dn.xlarge image Deep Learning AMI (Ubuntu 18.04) Version 36.0 url 54.187.76.64
       Synchronizing folders
       receiving file list ... 
       13 files to consider
       output/
       output/confusion_matrix.png
       89245 100%    1.70MB/s    0:00:00 (xfer#1, to-check=4/13)
       output/model_log.txt
       988990 100%   15.99MB/s    0:00:00 (xfer#2, to-check=3/13)
       output/model_losses.png
       29327 100%  469.50kB/s    0:00:00 (xfer#3, to-check=2/13)
       output/training_example_images.png
       84247 100%  831.03kB/s    0:00:00 (xfer#4, to-check=1/13)
       output/wrong_examples.png
       132897 100%    1.17MB/s    0:00:00 (xfer#5, to-check=0/13)

       sent 220 bytes  received 305541 bytes  122304.40 bytes/sec
       total size is 1668746  speedup is 5.46
       DONE

    

-------------------------------------------------------------------------

.. _ug_status:
   
Checking server status
======================

There are several actions that allow you to check the status of your burst server(s) and stop the processes running on them.

``burst list-server [--session-name NAME]``
  Lists the remote server you are currently running, its assigned IP address, and its status (e.g., "running", "stopped").  It assumes the default session name (``burst-$UNAME``), unless you specify a different session-name.

``burst kill [--session-name NAME]``
  Kills the Docker process running on a remote server, but leaves the server active and available to ssh into.  Assumes the default session name (``burst-$UNAME``), unless you specify a different session-name.

``burst stop-server [--session-name NAME]``
  Stops a remotely running server (note: This stops the process and pauses the server so that you are no longer paying for the compute.  The server can be quickly and easily restarted when you next run a command).  Assumes the default session name (``burst-$UNAME``), unless you specify a different session-name.

``burst terminate-server [--session-name NAME]``
  Terminates a remotely running server (note: This shuts down the remote server completely.  The remote environment will have to be rebuilt when launched on a new server).  Assumes the default session name (``burst-$UNAME``), unless you specify a different session-name.

-------------------------------------------------------------------------

.. _ug_configuration:

Configuration
==============

Configuration Quick-Start
--------------------------

Configure your cloud compute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first time you use burst, we recommend running the interactive configuration setup.  To do this, you will need credentials for the cloud account you want to use.  For AWS, this means you will need:

* an access key 
* a secret key 
* a region (e.g., ``us-west-2``)

Enter the configuration wizard and follow the instructions to set up a new compute service, entering your access key, secret key, and region as prompted.
  
::
   
    burst configure

This configuration will, by default, set up your account to use a powerful GPU when you run burst with ``--gpu``, a medium-power CPU for testing when you run burst with ``--no-gpu``, and a default harddisk with 175 Gb.

This configuration is stored by default in ``~/.burst/config.yml``.

NOTE: Google Cloud support is still in beta, and not yet integrated into the interactive configuration tool.  Please see `Override cloud account keys at build time`_ below for guidance on setting up GCE, and contact help@burstable.ai if you need additional support.


Configure your cloud storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can configure burst to access and use cloud storage, rather than having to sync data back and forth between your local and cloud machines (this is strongly recommended for sizable datasets).

To do this, run the interactive configuration setup and follow the instructions to set up a new storage service.  For AWS s3 (currently the only option supported by the wizard), you will need:

* an access key 
* a secret key 
* a region (e.g., ``us-west-2``)

Enter these when prompted by the interactive configuration tool.

This storage configuration, along with the alias you give it, will be stored in the ``~/.burst/config.yml`` file, and set as the default cloud storage device.

You can set up multiple cloud storage systems by running ``burst configure`` again and entering a new storage system, with a different alias.  The first storage system you configure will be used as the default, unless you manually edit your ``~/.burst/config.yml`` file to specify a different alias as the default.


Configure different default hardware
-------------------------------------

You can change the default compute settings by manually editing the ``~/.burst/config.yml`` file created by ``burst configure``.  

The interactive configuration currently sets your default cloud compute hardware to be a "g4dn.xlarge" AWS machine for GPU processing and a "t2.medium" AWS machine for CPU processing.  

To choose a different default machine for either GPU or CPU, first find the name of the virtual machine (VM) you want to use (e.g., "t2.large" or "g4ad.8xlarge") on AWS's list of available machines, along with a compatible VM image (e.g., "ami-ubuntu-18.04-1.16.0-00-1569343567").  Edit the ``config.yml`` file to specify the VM name and image you want to use.  Change the ``default_gpu_vmtype`` and ``default_gpu_image`` to specify an alternate GPU compute default, and/or change ``default_vmtype`` and ``default_image`` to specify an alternate CPU compute default.

The default GPU VM will be used with ``burst build --gpu`` and the default CPU VM will be used with ``burst build --no-gpu``. 


Override default configuration
---------------------------------------

If you want to experiment with a different hardware set-up, you can override the specifications in ``config.yml`` at the command line when you build a burst project.  You do this using the ``--vm-type``, ``--vm-image``, and/or ``disksize`` options to specify the VM, VM image, and hard disk size (in Gb) to use, e.g.:

::

   burst build --vm-type t2.xlarge --vm-image ami-ubuntu-18.04-1.16.0-00-1569343567 --disksize 512

Similarly, you can override the default cloud storage specified in ``config.yml`` at the command line when you build a project.  You do this using the ``--storage-service ALIAS`` option to specify the alias of the cloud storage configuration you want to use, e.g.:

::

   burst build --storage-service graves_aws_s3

Note that the requested cloud storage alias must already have been added to your ``config.yml`` file using ``burst configure``.
   
   
Store and use alternative hardware configurations
--------------------------------------------------

If you have several different hardware configurations you like to use with burst, it would be annoying to have to manually specify them each time with command line options.  You can store multiple configuration choices in your ``~/.burst/config.yml`` file and choose between them at build time.

To add a new configuration option, run ``burst configure`` again and set up a new compute service.  Specify the access key, secret key, and region (these can be the same as your default, but don't have to be), and give this configuration a different alias---you will use this alias to refer to it, so pick something descriptive and easy to remember (e.g., "aws_multicore_cpu").

This will add a new compute configuration section to your ``~/.burst/config.yml`` file.  You should see it there under its alias when you open the ``config.yml`` file.

Manually edit the relevant fields to specify the paramters of this alternative hardware configuration:

* ``default_gpu_image``
* ``default_gpu_vmtype``
* ``default_image``
* ``default_vmtype``
* ``disksize``

Notice at the bottom of the "compute" section of your ``config.yml`` file, there is a setting for "default_compute".  Make sure this is set to the alias of the compute service you wish to use by default.

Now when you run

::

   burst build --gpu

or

::

   burst build --no-gpu

burst will use whichever hardware configuration you have set as your default.  If you wish to use a configured compute service other than the default, specify it at build time with the ``--compute-service [ALIAS]`` option, e.g.:

::

   burst build --no-gpu --compute-service aws_multicore_cpu

You can store and use as many different configurations as you like, as long as they have different aliases, but you can only have one default for CPU and one for GPU compute.


Specify an alternate config file
--------------------------------------------------

There are times when it is useful to have not just multiple compute service configurations to choose from (as described above), but completely separate ``config.yml`` files to specify alternative configurations.

This can be true, for example, when you want to have specific hardware configurations for specific projects and it makes most sense to store those in a ``config.yml`` in the local project directory, rather than a central ``~/.burst/config.yml``.  Or, alternatively, you might want to experiment with some other burst user's cloud configuration (e.g., ``genevieves_config.yml``) without overwriting or appending her set-up to your own.

You can use any correctly-formatted ``*.yml`` file by passing it as a command line option:

::

   burst build --gpu --config-file FILE

This will use the specified FILE instead of ``~/.burst/config.yml``.


Override cloud account keys at build time
---------------------------------------------

It is possible to specify the cloud compute account you want to use at the command line, overriding the configuration set-up in ``config.yml``.  You do this with the following options:

* ``--compute-provider``: the cloud account provider.  Can be "EC2" for AWS or "GCE" for Google Cloud.
* ``--compute-access``: the account key
* ``--compute-secret``: the account secret key
* ``--compute-region``: the account region
* ``--gcs-project``: the Google Cloud project ID (Google Cloud only)

Any options not explicitly set at the command line will default to the configuration in ``config.yml``.

Please contact help@burstable.ai if you need support setting up Google Cloud accounts---GCE support is still in beta.

-------------------------------------------------------------------------

.. _ug_help:
  
Help at the Command Line
=========================

To get help at the command line and a list of all avilable options, type:

::
   
   burst help

or

::
   
   burst --help

For a summary list of possible actions, type:

::

   burst actions


-------------------------------------------------------------------------

.. _ug_actions:
  
Burst Actions: a complete list
===============================

``burst actions``
  List available actions
``burst attach`` 
  Attach stdin, stdout, stderr to background process. ctl-C detaches (see :ref:`ug_background`)
``burst build``
  Build project (see :ref:`ug_build`)
``burst configure``
  Interactive configuration (see :ref:`ug_configuration`)
``burst help``
  Print helpful information
``burst jupyter``
  Run JupyterLab (respects idle timeout, see :ref:`ug_jupyter`)
``burst kill``
  Stop docker process on remote (see :ref:`ug_background`)
``burst list-server``
  List available servers; display time till automatic stop (see :ref:`ug_status`)
``burst run <command>``
  Run <command> on remote server (see :ref:`ug_run`)
``burst status``
  Show status of remote task (if running, see :ref:`ug_background`)
``burst stop-server``
  Force-stop server (prompts for confirmation, see :ref:`ug_status`)
``burst sync``
  Synchronize local directory to remote (see :ref:`ug_background`)
``burst termimate-server``
  Terminate (delete) remote server (prompts for confirmation, see :ref:`ug_status`)

-------------------------------------------------------------------------

.. _ug_options:
  
Burst Options: a complete list
===============================

``--background`` or ``-b``
  Run task in background mode (see :ref:`ug_background`)
``--compute-access KEY``
  libcloud username (aws: ACCESS_KEY, see :ref:`ug_configuration`)
``--compute-provider PROVIDER``
  GCE, EC2 etc. (see :ref:`ug_configuration`)
``--compute-region REGION``
  libcloud location (aws: region, see :ref:`ug_configuration`)
``--compute-secret SECRET``
  libcloud password (aws: SECRET, see :ref:`ug_configuration`)
``--compute-service COMPUTE_SERVICE``
  override default compute configuration service (see :ref:`ug_configuration`)
``--config-file FILE``
  override default config.yml (see :ref:`ug_configuration`)
``--disksize GIGABYTES``
  disk size in gigabytes (see :ref:`ug_configuration`)
``--docker-file FILE``
  Docker file (defaults to ./Dockerfile, see :ref:`ug_build_options`)
``--docker-port PORT``
  local port to map to remote host docker daemon(default: 2377, see :ref:`ug_build_options`)
``--gcs-project PROJECT``
  Google Cloud project ID (see :ref:`ug_configuration`)
``--gpu``
  Build with gpu (see :ref:`ug_build_options`)
``--help``
  Print usage info
``--local``
  run on local device
``--no-gpu``
  Build without gpu (see :ref:`ug_build_options`)
``--pubkey-file PUBKEY``
  public key to access server (defaults to ~/.ssh/id_rsa.pub, see :ref:`ug_build_options`)
``--session-name NAME``
  Burst session name (defaults to burst-username; different sessions launch new machine instances, see :ref:`ug_build_options`, :ref:`ug_run_options`)
``--stop SECONDS``
  seconds before server is stopped (default 900) 0 means never. Use action 'stop' to force stop (see :ref:`ug_run_options`)
``--storage-mount STORAGE:MOUNT``
  map (mount) burst storage service to local folder (see :ref:`ug_run_options`)
``--storage-service STORAGE_SERVICE``
  override default storage configuration (see :ref:`ug_configuration`)
``--tunnel-port LOCAL[:REMOTE], -p LOCAL[:REMOTE]``
  port mapping; example: -p 8080 or -p 8081:8080 (see :ref:`ug_run_options`)
``--verbose VERBOSITY, -v VERBOSITY``
  -1: just task output, 0: status on single line, 1: status, 2-255: more verbose (default: 0)
``--version``
  Print version # & exit
``--vm-image IMAGE``
  libcloud image (aws: ami image_id, see :ref:`ug_configuration`)
``--vm-type TYPE``
  aws: instance_type; gce: size (see :ref:`ug_configuration`)
``--vm-username SSHUSER``
  remote server username for login (see :ref:`ug_build_options`)
