#! /usr/bin/python
#
# Use as a cgi script
#
# Draws a slope field
#
# Create a cache of the landing file with ./index.cgi --no-cache > landing.html

import cgi
import sys

def parse_form(cgi_input):
    """Returns dictionary with pertinent data from a FieldStorage instance"""

    def cgi_get(name, default, convert=float):
        """Gets the cgi value and converts it, with a default value on error"""
        field_str = cgi_input.getfirst(name, str(default))
        try:
            value = convert(field_str)
        except ValueError:
            value = default

        return value

    tmin = cgi_get("tmin", 0)
    tmax = cgi_get("tmax", 3)
    tticks = cgi_get('tticks', 21, int)

    ymin = cgi_get("ymin", -1)
    ymax = cgi_get("ymax", 1)
    yticks = cgi_get('yticks', 15, int)

    fn_str = cgi_input.getfirst("fn")

    return {'tmin': tmin, 'tmax': tmax, 'tticks': tticks,
            'ymin': ymin, 'ymax': ymax, 'yticks': yticks,
            'fn_str': fn_str}

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

params = parse_form(cgi_input)

for line in slopefield.cgi_output(params,
      template_file="template.html",
      log_file=None):
    print line

