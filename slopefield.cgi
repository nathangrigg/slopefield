#! /usr/bin/python

import cgi
import slopefield
import parser
import cgitb

cgitb.enable()


getfirst=cgi.FieldStorage().getfirst

fn_str=getfirst("fn","")
xmin=getfirst("xmin","-1")
xmax=getfirst("xmax","1")
ymin=getfirst("ymin","-1")
ymax=getfirst("ymax","1")
xticks=getfirst("xticks","20")
yticks=getfirst("yticks","20")

xmin=float(xmin)
xmax=float(xmax)
ymin=float(ymin)
ymax=float(ymax)
xticks=float(xticks)
yticks=float(yticks)

fn = parser.parse(fn_str)

#print "Content-Type: text/html;"
print "Content-Type: image/svg+xml;"
print

for line in slopefield.svg_slopefield(fn,xmin,xmax,ymin,ymax,xticks,yticks):
	print line
        pass
