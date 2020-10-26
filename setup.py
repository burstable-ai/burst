from setuptools import setup, find_packages
from rexec.version import version

setup(
    name="rexec",
    version=version,
    packages=find_packages(),
    python_requires='>=3',
    scripts=['bin/rexec'],
    install_requires=[
        "blessings == 1.7",
        "apache-libcloud == 3.1.0",
    	"cryptography==3.0",
        "easydict==1.9",
        "PyYAML==5.3.1"
    ],
    include_package_data=True
)
