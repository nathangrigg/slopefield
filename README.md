# About

This is a cgi script and python module to draw a slope field for a first-order differential equation in the form `y'=f(t,y)`.

The input is checked against a whitelist and then converted to a python function using `eval`.

# Installation

Requires Python 2.6 or 2.7

Put the files `index.cgi`, `template.html`, `style.css`, and `slopefield.py`
in a folder that can run cgi scripts.

Speed things up by creating a landing page using

    $ ./index.cgi --no-cache > landing.html

If you make changes to `template.html`, you will need to do this again to update
the cache.

# License

Written by Nathan Grigg

This work is licensed under a [Creative Commons Attribution-ShareAlike 3.0 License][1].

[1]: http://creativecommons.org/licenses/by-sa/3.0/
