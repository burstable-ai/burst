.. _user_guide_page:

============
User Guide
============


Configuration
^^^^^^^^^^^^^

In order to burst a process to the cloud, you need to have set up a remote compute service, as explained in the :ref:`installation` instructions.  If you have not already configured a compute service, do this by launching the interactive configuration setup with:

::

   burst configure

For more information about configuration options and/or specifying the configuration at runtime, see the detailed documentation on :ref:`configuration`.

   
Core functionality
^^^^^^^^^^^^^^^^^^

Within a burst project directory, there are multiple "actions" that can be taken.  The most common sequence of actions will be to build the project and then to run it on a remote server:

::
   
   burst build [--gpu] [--no-gpu]
   burst run [options] <command>

Burst server status:
^^^^^^^^^^^^^^^^^^^^

There are several actions that allow you to check the status of your burst server(s) and stop the processes running on them.

* ``burst list-servers``: lists the remote servers you are currently running, their assigned IP addresses, and their status (e.g., "running", "stopped").

* ``burst kill``: kills the Docker process running on a remote server, but leaves the server active and available to ssh into.

* ``burst stop-server``: stops a remotely running server (note: This stops the process and pauses the server so that you are no longer paying for the compute.  The server can be quickly and easily restarted when you next run a command).

* ``burst terminate-server``: terminates a remotely running server (note: This shuts down the remote server completely.  The remote environment will have to be rebuilt when launched on a new server).
  

Background mode:
^^^^^^^^^^^^^^^^

A useful option, for tasks that may take a while to complete, is to run a burst command in "background" mode.  This sets the process running on the remote burst server, then detaches from the server and leaves the process running.  Run your process in background mode using the following:

::
   
   burst run --background <command>

This launches your command, then logs out of the server and returns you to your local terminal prompt.

There are several burst actions that are useful for checking on or managing background processes:

* ``burst attach``: attaches stdin, stdout, and stderr to the remote background process, so you can see the process running, as if you had never logged out.  Ctl-C detaches and returns you to your local prompt.

* ``burst status``: shows the status of the remote tasks if the Docker container is still running, along with information about launch time and run-time so far.

* ``burst kill``: kills the Docker process running on a remote server, but leaves the server active and available to ssh into.

* ``burst sync``: when a remote background process is complete, this syncs all of the output files back to your local directory, as burst normally does at the end of a process when not running in background mode.


Command line help:
^^^^^^^^^^^^^^^^^^

To get help at the command line and a list of all avilable options, type:

::
   
   burst help

or

::
   
   burst --help

For a summary list of possible actions, type:

::

   burst actions


