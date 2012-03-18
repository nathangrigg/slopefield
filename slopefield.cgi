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

print "Content-Type: text/html;"
print

print """<!DOCTYPE html>
<html>
<head>
<title>Slope Field</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>

<body>
<h1>Slope Field by Nathan Grigg</h1>

<form name="form" method="get">
	<p>
	<label><em>y'</em>(<em>t</em>,<em>y</em>) =
		<input type="text" name="fn" size=50
		autocorrect="off" autocapitalize="off">
	</label>
	<p> Example: <tt>sin(t*pi)+y^2/e^t</tt>
	<p> You may use: <tt>t y + - * / ^ e pi sin cos abs</tt>
	<p>
	<table><tr>
	<td><label>t-min:
		<input type="number" name="tmin" size="5" value="0">
	</label></td>
	<td><label>t-max:
		<input type="number" name="tmax" size="5" value="2">
	</label></td>
	<td><label>t-ticks:
		<input type="number" name="tticks" size="5" value="30"
		min="10" max="40">
	</label></td>
	</tr><tr>
	<td><label>y-min:
		<input type="number" name="ymin" size=5 value="-1">
	</label></td>
	<td><label>y-max:
		<input type="number" name="ymax" size=5 value="1">
	</label></td>
	<td><label>y-ticks:
		<input type="number" name="yticks" size=5 value="30"
		min="10" max="40">
	</label></td>
	</table>
	<p><button type="submit">Draw the slope field</button>
</form>
"""


if fn_str:
    fn = parser.parse(fn_str)

    print '<div id="plot">'

    for line in slopefield.svg_slopefield(fn,xmin,xmax,ymin,ymax,xticks,yticks):
        print line

    print '</div>'

print """</body>
</html>"""
