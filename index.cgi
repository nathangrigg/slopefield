#! /usr/bin/python
#
# Use as a cgi script
#
# Draws a slope field
#
# Create a cache of the landing file with ./index.cgi --no-cache > landing.html

import cgi
import sys

cgi_input = cgi.FieldStorage()

# if there are no request parameters, write out static file, if possible
if len(cgi_input.keys()) == 0 and (len(sys.argv) == 1
                                   or sys.argv[1] <> "--no-cache"):
    try:
        f = open('landing.html','r')
    except:
        pass
    else:
        try:
            for line in f:
                print line,
        finally:
            f.close()
            sys.exit()

import slopefield
import cgitb

cgitb.enable()

for line in slopefield.cgi_output(cgi_input,
      template_file="template.html",
      log_file=None):
    print line

