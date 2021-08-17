from setuptools import setup, find_packages
from burst.version import version
import os

scripts = ['bin/burst.py', 'bin/burst-config.py', 'bin/burst-monitor.py']
if os.name == 'nt':
    scripts.append('bin/burst.bat')

setup(
    name="burstable",
    version=version,
    py_modules=['config'],
    packages=find_packages(),
    python_requires='>=3.6',
    scripts=scripts,
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
