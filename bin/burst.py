#! /usr/bin/env python3
import os
import sys
import platform

args = " ".join(sys.argv[1:])
if "windows" in platform.platform().lower:
    os.system(f"CALL python \"..\\Lib\\site-packages\\burst\\burst_cli.py\" {args}")
else:
    os.system("../burst/burst_cli.py")

