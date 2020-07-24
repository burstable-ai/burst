from setuptools import setup, find_packages
setup(
    name="rexec",
    version="0.1.0",
    packages=find_packages(),
    python_requires='>=3',
    scripts=['bin/rexec'],
    install_requires=[
        # "requests == 2.23.0",
        "blessings == 1.7",
        # "python_dateutil == 2.8.1",
        "apache-libcloud == 3.1.0"
    ],
    include_package_data=True
)
