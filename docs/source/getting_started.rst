.. _getting_started_page:

===============
Getting Started
===============

* :ref:`installation_sec`
* :ref:`configuration_sec`
* :ref:`usage_sec`

.. _installation_sec:

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


Check to make sure that burst has installed correctly with

::

   burst --version
       
.. _configuration_sec:

Configuration (basic)
=====================

The first time you use burst, we recommend running the interactive configuration setup.  To do this, you will need credentials for the cloud account you want to use.  For AWS, this means you will need:

* an access key 
* a secret key 
* a region (e.g., ``us-west-2``)

Enter the configuration wizard and follow the instructions to set up a new compute service, entering your access key, secret key, and region as prompted.
  
::
   
    burst configure

This configuration will, by default, set up your account to use a powerful GPU when you run burst with ``--gpu``, a medium-power CPU for testing when you run burst with ``--no-gpu``, and a default harddisk with 175 Gb.

To set up other hardware configurations, see :ref:`the detailed configuration instructions.<ug_configuration>`.


.. _usage_sec:


Using burst
===========

Burst is built and run from inside a project directory.  In order to be "burstable", a project requires a working Dockerfile.  You can find examples and templates for such Dockerfiles, in the :ref:`Examples<examples_page>`.

The easiest way to test your burst installation is using the test examples that are available in the burst gitHub repo `here <https://github.com/burstable-ai/burst>`_.

Download the repo.  The examples can be found in the ``burst_examples`` folder.

Try running :ref:`Hello Burst!<ex_hello_burst>`.
