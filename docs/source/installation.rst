Installation
============

*Note: If you want to contribute to the Burst OSS project or just follow bleeding-edge development, install through gitHub as described* `here <https://github.com/burstable-ai/burst/wiki/Contributing-To-Burst>`_ *instead.*

SSH keys:
^^^^^^^^^
You must have a public/private ssh key pair, stored as ``~/.ssh/id_rsa.pub`` and ``~/.ssh/id_rsa`` by default.

If you do not already have ssh keys, run ssh-keygen to generate them:
::

    ssh-keygen -t rsa -b 4096

[Recommended] Set up a virtual environment:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow the instructions here: `python-virtual-environments-a-primer. <https://realpython.com/python-virtual-environments-a-primer/>`_

Launch the virtual environment and do the remainder of your installation and set-up inside the virtual environment.

Check versions of Python and Docker at the command line:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure you are running the necessary versions of python and Docker (you need Python 3, Docker >= 19)
::
   
    python --version
    docker --version

Install the command-line tool:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::
   
    pip install burstable

Run the interactive configuration setup:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::
   
    burst configure

Enter your configuration information as prompted to set up a remote compute service.

Test the installation:
^^^^^^^^^^^^^^^^^^^^^^

Test your installation of Burst by running the test example provided `here. <https://burstable.ai/examples>`_
