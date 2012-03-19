This is a cgi script and python module to draw a slope field for a first-order differential equation in the form `y'=f(t,y)`.

The input is checked against a whitelist and then converted to a python function using `eval`.

# Installing on your server

Put all files in a directory that is allowed to execute cgi scripts. On some hosts, this should be a subdirectory of `cgi-bin`, for example `cgi-bin/slopefield/`.


# Licence

This work is licensed under a [Creative Commons Attribution-ShareAlike 3.0 License][1].

[1]: http://creativecommons.org/licenses/by-sa/3.0/
