# burst
## A command-line tool to remotely execute code in the cloud

## Introduction

`burst` lets you run your software remotely in the cloud, on powerful GPU's or multi-CPU hardware instances that are
booted up and stopped automatically, so you only pay for the time you use.

We support remote computing on Amazon Web Services and will be adding more 
(Google Cloud Platform support is currently in beta).

Documentation is available here:
* [Overview](https://burstable.readthedocs.io/en/latest/index.html)
* [Quickstart](https://burstable.readthedocs.io/en/latest/getting_started.html)
* [Examples](https://burstable.readthedocs.io/en/latest/examples.html)
* [Full User Guide](https://burstable.readthedocs.io/en/latest/user_guide.html)

## Dependencies

* Python3 
* Docker version 19 or higher
* A folder/project with a working `Dockerfile`
* ssh keys
* AWS or Google Cloud Services account and access keys

_Note: if you want to contribute to the burst OSS project or just follow bleeding-edge development, install through 
gitHub as described [here](https://github.com/burstable-ai/burst/wiki/Contributing-To-Burst) instead._
