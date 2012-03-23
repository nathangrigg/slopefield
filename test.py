#! /usr/bin/python

import slopefield as sf

f = lambda t,y: 9.8-y**float(2)/float(300)
form = {'tmin':0,'tmax':20,'tticks':15,'ymin':0,'ymax':70,
    'yticks':10,'fn':f,'title':''}

for line in sf.svg_slopefield(form):
    print line


