#! /usr/bin/python

import cgi
import slopefield
import parser
import cgitb

cgitb.enable()

def cgi_get(name,default,convert=float):
	"""Gets the cgi value and converts it, with a default value on error"""
	field_str = cgi.FieldStorage.getfirst(name,str(default))
	try:
		value = convert(field_str)
	except ValueError:
		value = default

	return value

def clip(value,left,right):
	"""Forces value to be within the range [left, right]"""
	return min(right,max(left,value))


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

# extract values
fn_str=getfirst("fn","t+y")

tmin = cgi_get("tmin",0)
tmax = cgi_get("tmax",2)
tticks = clip(cgi_get('tticks',30,int),10,40)

ymin = cgi_get("ymin",-1)
ymax = cgi_get("ymax",1)
yticks = clip(cgi_get('tticks',30,int),10,40)

# ensure that delta_t and delta_y will be positive
if (tmax-tmin)/tticks <= 0 :
	tmax = tmin + 1
if (ymax-ymin)/yticks <= 0:
	ymax = ymin + 1


if fn_str:
    fn = parser.parse(fn_str)

    print '<div id="plot">'

    for line in slopefield.svg_slopefield(fn,xmin,xmax,ymin,ymax,xticks,yticks):
        print line

    print '</div>'

print """</body>
</html>"""
