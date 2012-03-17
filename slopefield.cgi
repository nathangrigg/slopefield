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

print """<html>
<head>
<link rel="stylesheet" type="text/css" href="style.css">
<title>Slope Field</title>

<script type="text/javascript">
function validateForm(){
	return true;
}
</script>
</head>

<body>

<h1>Slope Field by Nathan Grigg</h1>

<form name="form" onsubmit="return validateForm()" method="get">
<p><label><em>y'</em>(<em>t</em>,<em>y</em>)= <input type="text" name="fn" size=40></label>
<p>Operations: + - * / ^ Functions: sin,cos,abs Variables: t,y
<p><label>xmin<input type="text" name="xmin" size=5></label>
<label>xmax<input type="text" name="xmax" size=5></label>
<label>xticks<input type="text" name="xticks" size=5></label>
<p><label>ymin<input type="text" name="ymin" size=5></label>
<label>ymax<input type="text" name="ymax" size=5></label>
<label>yticks<input type="text" name="yticks" size=5></label>
<p><button type="submit">Submit</button>
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
