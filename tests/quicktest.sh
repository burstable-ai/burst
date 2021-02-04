#!/usr/bin/env bash

burst --build 2>&1 | tee quicktest.log
#
#burst --verbosity 1 python3 hello_burst.py
