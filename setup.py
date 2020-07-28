from setuptools import setup, find_packages
setup(
    name="rexec",
    version="0.1.1",
    packages=find_packages(),
    python_requires='>=3',
    scripts=['bin/rexec'],
    install_requires=[
        "blessings == 1.7",
        "apache-libcloud == 3.1.0",
	"cryptography==3.0"
    ],
    include_package_data=True
)
