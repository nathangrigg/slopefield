#! /usr/bin/python

import cgi
import sys

storage = cgi.FieldStorage()

# if there are no request parameters, write out static file, if possible
if len(storage.keys()) == 0:
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
import re
import cgitb
from math import sin,cos,tan,sqrt,e,pi,log,cosh,sinh,tanh

VALID_WORDS = ['','sin','cos','tan','t','y','abs','sqrt','e','pi','log','ln',
	'acos','asin','atan','cosh','sinh','tanh']
ln = log

cgitb.enable()
print "Content-Type: text/html;\n"

def cgi_get(name,default,convert=float):
	"""Gets the cgi value and converts it, with a default value on error"""
	field_str = storage.getfirst(name,str(default))
	try:
		value = convert(field_str)
	except ValueError:
		value = default

	return value

def clip(value,left,right):
	"""Forces value to be within the range [left, right]"""
	return min(right,max(left,value))

html_start="""<!DOCTYPE html>
<html>
<head>
<title>Slope Field</title>
<link rel="stylesheet" type="text/css" href="style.css">
<meta name="viewport" content="width=800px"/>
</head>

<body>
<h1>Slope Field by Nathan Grigg</h1>

<form name="form" method="get">
	<p>
	<label><em>y'</em>(<em>t</em>,<em>y</em>) =
		<input type="text" name="fn" size="50" value="%s"
		autocorrect="off" autocapitalize="off">
	</label>
	<p> You may use: <tt>t y + - * / ^ e pi cos sin tan abs ln acos asin atan cosh sinh tanh</tt>
	<p> Example: <tt>2*y/tan(2*t)</tt>
	<p>
	<table><tr>
	<td><label>t-min:
		<input type="number" name="tmin" size="5" value="%g">
	</label></td>
	<td><label>t-max:
		<input type="number" name="tmax" size="5" value="%g">
	</label></td>
	<td><label>t-ticks:
		<input type="number" name="tticks" size="5" value="%d"
		min="10" max="40">
	</label></td>
	</tr><tr>
	<td><label>y-min:
		<input type="number" name="ymin" size=5 value="%g">
	</label></td>
	<td><label>y-max:
		<input type="number" name="ymax" size=5 value="%g">
	</label></td>
	<td><label>y-ticks:
		<input type="number" name="yticks" size=5 value="%d"
		min="10" max="50">
	</label></td>
	</table>
	<p><button type="submit">Draw the slope field</button>
</form>
"""

footer = """<footer>
<p>This page requires an up-to-date internet browser.
<p>Want to host this on your own site and/or make changes?
<a href="https://github.com/nathan11g/slopefield">Get
the source from GitHub</a>.
<p>This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-ShareAlike 3.0 License</a>.
</footer>
"""

html_end="</body>\n</html>"""

def sanitize(fn_str):
	words = re.split(r'[0-9+\-*/^ ()]+',fn_str)
	for word in words:
		 if word not in VALID_WORDS:
		 	error('Unrecognized expression in function: %s' % word)

	s = fn_str.replace('^','**')

	# replace 1.232 with float(1.234)
	s = re.sub(r'[0-9.]+', r'float(\g<0>)', s)

	try:
		fn = eval("lambda t,y: " + s)
	except SyntaxError:
		error('Syntax Error. Something is wrong with the function you entered.\
		Common mistakes include writing <tt>3x</tt> instead of <tt>3*x</tt> or\
		<tt>sin t</tt> instead of <tt>sin(t)</tt>.')
	except NameError:
		error('Undefined function: %s' % sys.exc_value)
	except:
		error('Something is wrong with the function you entered.')

	# sanity check
	try:
		output = fn(1.25,1.25)
	except ValueError:
		pass
	except ZeroDivisionError:
		pass
	except OverflowError:
		pass
	except:
		error('Something is wrong with the function you entered.')

	return fn

def error(message):
	print html_start % (fn_str,tmin,tmax,tticks,ymin,ymax,yticks)
	print "<p class='alert'>" + message + "</p>"
	print footer
	print html_end
	sys.exit()


# extract values
tmin = cgi_get("tmin",0)
tmax = cgi_get("tmax",3)
tticks = clip(cgi_get('tticks',40,int),10,50)

ymin = cgi_get("ymin",-1)
ymax = cgi_get("ymax",1)
yticks = clip(cgi_get('yticks',30,int),10,40)

# ensure that delta_t and delta_y will be positive
if (tmax-tmin)/tticks <= 0 :
	tmax = tmin + 1
if (ymax-ymin)/yticks <= 0:
	ymax = ymin + 1

fn_str=storage.getfirst("fn")

if fn_str is None:
	fn_str = ""
	fn = lambda t,y: 2*y/tan(2*t)
	title = "y'=2*y/tan(2*t)"
else:
	fn = sanitize(fn_str)
	title = "y'=" + fn_str

# graph output

print html_start % (fn_str,tmin,tmax,tticks,ymin,ymax,yticks)

print '<div id="plot">'

for line in slopefield.svg_slopefield(fn,tmin,tmax,ymin,ymax,tticks,yticks,
  title=title):
	print line

print '</div>'

print footer

print html_end

