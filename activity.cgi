#!/usr/bin/env python

# enable debugging
import cgitb
import cgi
import sys
import time
cgitb.enable()

print "Content-Type: text/html;charset=utf-8"
print

template = open('activity.html')
lines = template.read()
template.close()

print lines
