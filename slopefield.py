import re
import functools
from string import Template
from math import sin,cos,tan,sqrt,e,pi,log,cosh,sinh,tanh

VALID_WORDS = ['','sin','cos','tan','t','y','abs','sqrt','e','pi','log','ln',
    'acos','asin','atan','cosh','sinh','tanh']
ln = log

class SanitizeError(Exception):
    pass

def parse_form(cgi_input,log_file=None):
    """Returns dictionary with pertinent data from a FieldStorage instance"""

    def cgi_get(name,default,convert=float):
        """Gets the cgi value and converts it, with a default value on error"""
        field_str = cgi_input.getfirst(name,str(default))
        try:
            value = convert(field_str)
        except ValueError:
            value = default

        return value

    tmin = cgi_get("tmin",0)
    tmax = cgi_get("tmax",3)
    tticks = clip(cgi_get('tticks',21,int),10,50)

    ymin = cgi_get("ymin",-1)
    ymax = cgi_get("ymax",1)
    yticks = clip(cgi_get('yticks',15,int),10,40)

    # ensure that delta_t and delta_y will be positive
    if (tmax-tmin)/tticks <= 0:
        tmax = tmin + 1
    if (ymax-ymin)/yticks <= 0:
        ymax = ymin + 1

    fn_str=cgi_input.getfirst("fn")

    return {'tmin':tmin, 'tmax':tmax, 'tticks':tticks,
            'ymin':ymin, 'ymax':ymax, 'yticks':yticks,
            'fn_str': fn_str}

def clip(value,left,right):
    """Forces value to be within the range [left, right]"""
    return min(right,max(left,value))

def sanitize(fn_str,log_file=None):
    """Sanitizes fn_str, evaluates and returns function"""
    words = re.split(r'[0-9.+\-*/^ ()]+',fn_str)
    for word in words:
         if word not in VALID_WORDS:
             raise SanitizeError(
               'Unrecognized expression in function: %s' % word)

    s = fn_str.replace('^','**')

    # replace 1.232 with float(1.234)
    s = re.sub(r'[0-9.]+', r'float(\g<0>)', s)

    try:
        fn = eval("lambda t,y: " + s)
    except SyntaxError:
        raise SanitizeError(
        'Syntax Error. Something is wrong with the function you entered. ' + \
        'Common mistakes include writing <tt>3x</tt> instead of <tt>3*x</tt> '+\
        ' or <tt>sin t</tt> instead of <tt>sin(t)</tt>.')
    except NameError,S:
        write_log(log_file,fn_str,S,'eval')
        raise SanitizeError(
         'Something is wrong with the function you entered')
    except Exception,S:
        write_log(log_file,fn_str,S,'eval')
        raise SanitizeError(
          'Something is wrong with the function you entered.')

    # sanity check
    try:
        output = fn(1.25,0.75)
    except (ValueError, ZeroDivisionError, OverflowError):
        pass
    except Exception,S:
        write_log(log_file,fn_str,S,'sanity check')
        raise SanitizeError(
          'Something is wrong with the function you entered.')

    return fn

def write_log(log_file,fn_str,msg,s):
    if log_file is not None:
        try:
            f = open(log_file, 'a')
        except:
            pass
        else:
            f.write("%s\t%s\t%s\n" % (fn_str,msg,s))
            f.close()

def svg_tick(tick):
    """Returns a line of svg representing the tick"""
    return '<line x1 = "%.01f" y1 = "%.01f" x2 = "%.01f" y2 = "%.01f" />' \
           % tuple(tick)

def translate(stretch,shift,value,noshift=False):
    """Performs an affine transformation, optionally skipping the translation"""
    if noshift:
        return stretch * value
    else:
        return stretch * value + shift

def translation(p1,i1,p2,i2):
    """Returns the affine translation that takes p1 to i1 and p2 to i2"""
    stretch = float(i2-i1)/(p2-p1)
    shift = i1 - stretch * p1
    return functools.partial(translate,stretch,shift)

translate_t = functools.partial(translate,1,0)
translate_y = functools.partial(translate,1,0)

def axes(canvas,title=""):
    """Creates a box with axis labels"""

    # the box
    yield '<g style="stroke-width:1; stroke:grey;">'
    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (canvas['left'],canvas['top'],canvas['left'],canvas['bottom']+2)
    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (canvas['left']-2,canvas['bottom'],canvas['right'],canvas['bottom'])
    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (canvas['right'],canvas['bottom']+2,canvas['right'],canvas['top'])
    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (canvas['left']-2,canvas['top'],canvas['right'],canvas['top'])

    # the axis ticks
    for t in canvas['taxis'][1:-1]:
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (translate_t(t),canvas['bottom']-2,
           translate_t(t),canvas['bottom']+2)
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (translate_t(t),canvas['top'],
           translate_t(t),canvas['top']+2)

    for y in canvas['yaxis'][1:-1]:
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (canvas['left']-2,translate_y(y),
           canvas['left']+2,translate_y(y))
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (canvas['right']-2,translate_y(y),
           canvas['right'],translate_y(y))

    yield "</g>"

    # the t axis labels
    yield '<g font-family="Verdana" font-size="10px" ' + \
     'style="text-anchor: middle;">'
    for value,label in zip(canvas['taxis'],canvas['taxis_label']):
        yield '<text x="%s" y="%s">%s</text>' % \
        (translate_t(value),canvas['h'],label)

    # and the title
    yield '<text x="%s" y="%s">%s</text>' % \
      (float(canvas['right']-canvas['top'])/2,canvas['top']-5,title)
    yield '</g>'

    # the y axis labels
    yield '<g font-family="Verdana" font-size="10px" ' + \
     'style="text-anchor:end;">'
    for value,label in zip(canvas['yaxis'],canvas['yaxis_label']):
        yield '<text x="%d" y="%s">%s</text>' % \
        (canvas['left']-6,translate_y(value)+4,label)
    yield '</g>'

def tick(t,y,f,length):
    """Returns a tick centered at t,y with slope f(t,y) and given length"""
    tt = translate_t(t)
    yy = translate_y(y)
    try:
        slope = f(t,y)
    except ZeroDivisionError:
        # vertical tick on division by zero
        out = [tt, yy-0.5*length,
               tt, yy+0.5*length]
    except OverflowError:
        out = [tt, yy-0.5*length,
               tt, yy+0.5*length]
    except:
        out = [tt,yy,tt,yy]
    else:
        vt =  translate_t(1,noshift=True)
        vy =  translate_y(slope,noshift=True)
        norm = (vt**2 + vy**2)**0.5
        vt *= 0.5 * length / norm
        vy *= 0.5 * length / norm
        out = [tt-vt,yy-vy,tt+vt,yy+vy]

    return out

def slopefield(form):
    """Returns a generator for a slopefield"""
    dt = float(form['tmax']-form['tmin'])/form['tticks']
    dy = float(form['ymax']-form['ymin'])/form['yticks']
    ticklength = 0.6 * min(translate_t(dt,noshift=True),
                           translate_y(dy,noshift=True))

    # loop
    t = form['tmin'] + 0.5 * dt
    while t < form['tmax']:
        y = form['ymin'] + 0.5 * dy
        while y < form['ymax']:
            yield tick(t,y,form['fn'],ticklength)
            y += dy
        t += dt

def canvas_dimensions(form,canvas_size=(750,500)):
    """calculate dimensions of the canvas, making room for axes"""
    w,h = canvas_size

    # make axis ticks and labels
    taxis = [form['tmin'] + float(form['tmax']-form['tmin'])*i/10 \
      for i in range(11)]
    taxis_label = ["%.3g" % t for t in taxis]
    yaxis = [form['ymin'] + float(form['ymax']-form['ymin'])*i/10 \
      for i in range(11)]
    yaxis_label = ["%.3g" % y for y in yaxis]
    yaxis_label_width = max([len(label) for label in yaxis_label])

    # adjust canvas for labels
    top,bottom = 15,h - 15
    left,right = 6*yaxis_label_width+6,w-15

    return {'top':top, 'left':left, 'bottom':bottom, 'right': right,
        'w':w, 'h':h, 'taxis':taxis, 'taxis_label':taxis_label,
        'yaxis':yaxis, 'yaxis_label':yaxis_label}

def svg_slopefield(canvas,slopefield_generator,title=""):
    """Returns an svg image for a slopefield"""

    # beginning of svg
    yield """<svg viewBox="0 0 %(w)d %(h)d"
width="%(w)d" height="%(h)d"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">""" % canvas

    for line in axes(canvas,title):
        yield line

    # style for tick marks
    yield '<g style="stroke-width:1; stroke:black;">'

    for i,tick in enumerate(slopefield_generator):
        yield svg_tick(tick)
        if i>3000:
            raise Exception("3000 ticks and counting. Infinite loop?")

    # close out svg
    yield "</g></svg>"

def cgi_output(cgi_input,template_file,log_file=None):
    """Generator for cgi output, one line at a time."""

    yield "Content-Type: text/html\r\n\r"

    form = parse_form(cgi_input,log_file)

    if form['fn_str'] is None:
        form['fn_str'] = ""
        form['fn'] = lambda t,y: 2*y/tan(2*t)
        form['title'] = "y'=2*y/tan(2*t)"
    else:
        try:
            form['fn'] = sanitize(form['fn_str'],log_file)
        except SanitizeError,msg:
            form['content'] = "<p class='alert'>%s</p>" % msg
            yield Template(open(template_file).read()).safe_substitute(form)
            return
        else:
            form['title'] = "y'=" + form['fn_str']


    # set up the canvas

    canvas = canvas_dimensions(form,canvas_size=(750,500))

    # calculate the translation factors based on canvas dimensions
    global translate_t,translate_y
    translate_t = translation(form['tmin'],canvas['left'],
                              form['tmax'],canvas['right'])
    translate_y = translation(form['ymin'],canvas['bottom'],
                              form['ymax'],canvas['top'])

    # get a generator for the slopefield
    slopefield_generator = slopefield(form)

    svg_generator = svg_slopefield(canvas,slopefield_generator,form['title'])

    # print it out

    start,end = Template(open(template_file).read()).safe_substitute(form)\
      .split('$content',1)

    yield start

    yield '<div id="plot">'

    for line in svg_generator:
        yield line

    yield '</div>'

    yield end
