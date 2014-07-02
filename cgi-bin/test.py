#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time
import subprocess
import cgi, cgitb
import os

cgitb.enable()

print "Content-type: text/html\n\n"
p = subprocess.Popen(['/tmp/pollxml.py', 'Botts'], stdout=subprocess.PIPE)

print p.communicate()
