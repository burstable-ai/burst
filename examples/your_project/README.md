# burst example: Setting up your own Python project
=======

# Required files

Every Python `burst` project requires the following files:

* `.dockerignore`
* `.burstignore`
* `Dockerfile`
* `requirements.txt`

Template versions of all of these files are included in this example directory.  For most pure python projects, the `Dockerfile`, `.dockerignore`, and `.burstignore` files included here will work out of the box.  The only file you will need to modify is the `requirements.txt`.

# Setting up your `requirements.txt` file

This file needs to specify the correct version of each python package you need to install in order to run your project.  These will typically be the packages that you import at the top of your python script or Jupyter notebook.

If you used `pip` to install packages, either in a virtual environment or directly into your main programming environment, you can see which version of each package is installed by running

	pip freeze

at the command line.  Specify these versions in your `requirements.txt` file, following the example format included in the template `requirements.txt` here.  

If you use `conda` to manage your python packages, you may need to look elsewhere in your system to find the correct version numbers for your packages (please update this README with instructions on how to find `conda` package versioning info!)

# Setting up your project

Make sure you have all supporting data files and *.py files in the directory with your project.  `burst` will transfer all files in the directory from which it is called (except for those specified in the `.burstignore`!).

# Running command line examples using burst

To run the command line example using burst, use

    burst python3 template.py 

The output should look something like this:

```
graves@pescadero ~/g/v/s/b/e/your_project> python template.py
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
graves@pescadero ~/g/v/s/b/e/your_project>
```

The first time you run burst, it will spin up a new server.  This will take several minutes.  It takes several more minutes to build the Docker container, as it downloads and installs all the required software and python packages.  On subsequent runs, starting with a running server or a stopped server, this initial set-up time will be negligible.  If you change `requirements.txt` between runs, the Docker container will take some time to rebuild itself on the next `burst` run.

When `burst` has finished running your project, it will automatically transfer any modified files back to your local directory and close the connection.  Once a `burst` connection has been closed for > 15 minutes, it will stop the remote server so that you will not be paying for it.

You can inspect the output files that have been transferred back to your local machine.

# Running examples in Jupyter using burst

Sometimes it is useful to be able to have an entire Jupyter notebook running on a GPU, while you are experimenting with a new model, so that the run time is fast while you are developing.  `burst` can support remote Jupyter notebooks for real-time model experimentation on a GPU.  

To run a remote Jupyter server through `burst`, use

    burst -p 8899 jupyter lab --ip 0.0.0.0 --port 8899 --allow-root
    
Make sure you use a port number that is not already in use (if the port is in use, you will get a non-transparent error message!)  The screen will then display a URL, which will look something like

    http://0.0.0.0:8899/lab?token=f60aaf215e2bd8a92015f732388e16b6407181aaca4a1a9a

Paste this URL into a new browser window.  This will load a JupyterLab window that is running on the remote `burst` server.

Edit and run the Jupyter notebook, just as you would on a local Jupyter server.  

NOTE: When you are done, *you must manually close the Jupyter server* by returning to the window where you launched it and hitting Ctl-C, then responding 'y' to shutdown the server.  *If you leave the Jupyter server running, you will continue to pay for the remote server, even if no code is being executed.  `burst` will not automatically stop a remote Jupyter server.*

