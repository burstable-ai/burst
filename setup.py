from setuptools import setup, find_packages
from burst.version import version
import os

# Linux/MacOS setup
scripts = ['bin/burst', 'bin/burst-config', 'bin/burst-monitor']
entry_pts = None

# Windows setup
if os.name == 'nt':
    scripts = None
    entry_pts = {
                       "console_scripts": [
                           "burst = burst.burst_cli:main",
                           "burst-config = burst.config.config:main",
                           "burst-monitor = burst.monitor.monitor"
                       ]
                   }

setup(
    name="burstable",
    version=version,
    py_modules=['config'],
    packages=find_packages(),
    python_requires='>=3.6',
    scripts=scripts,
    entry_points=entry_pts,
    install_requires=[
        "blessed            >=1.18,     <2",
        "blessings          >=1.7,      <2",
        "apache-libcloud    >=3.2.0,    <4",
        "cryptography       >=3.2,      <4",
        "easydict           >=1.9,      <2",
        "PyYAML             >=5.3.1,    <6"
    ],
    include_package_data=True
)
