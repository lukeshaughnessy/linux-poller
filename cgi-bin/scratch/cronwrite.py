#!/usr/bin/python
import subprocess
interval = '*/15 * * * *'

subprocess.call(["./cronwrite.sh", interval])



