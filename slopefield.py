from __future__ import division
import re
from string import Template
import numpy as np
from numpy import sin, cos, tan, sqrt, e, pi, log, \
    cosh, sinh, tanh, arccos, arcsin, arctan, abs

with open("template.html") as f:
    TEMPLATE = Template(f.read())

VALID_WORDS = ['', 'sin', 'cos', 'tan', 't', 'y', 'abs', 'sqrt', 'e',
    'pi', 'log', 'ln', 'acos', 'asin', 'atan', 'cosh', 'sinh', 'tanh',
    'arcsin', 'arctan', 'arccos']
ln, asin, acos, atan = log, arcsin, arccos, arctan

np.seterr(divide='ignore', invalid='ignore')

###########################################
# Methods to handle parameters
###########################################


class SanitizeError(Exception):
    pass


def clip(value, left, right):
    """Force value to be within the range [left, right]"""
    return min(right, max(left, value))


def sanitize(params):
    """Sanitize the function and limit number of ticks"""

    d = dict(params)

    d['tticks'] = clip(d['tticks'], 10, 50)
    d['yticks'] = clip(d['yticks'], 10, 40)

    # ensure that min < max
    if d['tmax'] <= d['tmin']:
        d['tmax'] = d['tmin'] + 1
    if d['ymax'] <= d['ymin']:
        d['ymax'] = d['ymin'] + 1

    if d['fn_str']:
        d['fn_str'] = re.sub(r'\bx\b', 't', d['fn_str'])  # replace x with t
        d['fn'] = sanitize_fn(d['fn_str'])

    return d


def sanitize_fn(fn_str):
    """Sanitizes fn_str, evaluates and returns function.

    Raises SanitizeError if something goes wrong with sanitation"""
    words = re.split(r'[0-9.+\-*/^ ()]+', fn_str)
    for word in words:
        if word not in VALID_WORDS:
            raise SanitizeError(
              'Unrecognized expression in function: %s' % word)

    s = fn_str.replace('^', '**')

    # replace 1.232 with float(1.234)
    s = re.sub(r'[0-9.]+', r'float(\g<0>)', s)

    try:
        fn = eval("lambda t,y: " + s)
    except SyntaxError:
        raise SanitizeError(
        'Syntax Error. Something is wrong with the function you entered. ' +
        'Common mistakes include writing <tt>3t</tt> instead of <tt>3*t</tt>' +
        ' or <tt>sin t</tt> instead of <tt>sin(t)</tt>.')
    except NameError as S:
        raise SanitizeError(
         'Something is wrong with the function you entered')
    except Exception as S:
        raise SanitizeError(
          'Something is wrong with the function you entered.')

    # sanity check
    try:
        fn(1.25, 0.75)
    except (ValueError, ZeroDivisionError, OverflowError):
        pass
    except TypeError as S:
        if S.message == "'float' object is not callable":
            raise SanitizeError(
              'Invalid syntax. Please use explicit multiplication. ' +
              '(Bad: 5y. Good: 5*y.)')
        else:
            raise SanitizeError(
              'Something is wrong with the function you entered.')

    except Exception as S:
        raise SanitizeError(
          'Something is wrong with the function you entered.')

    return fn

###########################################
# Methods to output svg
###########################################


def svg_tick(tick):
    """Returns a line of svg representing the tick"""
    return '<line x1 = "%.01f" y1 = "%.01f" x2 = "%.01f" y2 = "%.01f" />' \
           % tuple(tick)


def axes(canvas, trans, title=""):
    """Creates a box with axis labels"""

    # the box
    yield '<g style="stroke-width:1; stroke:grey;">'
    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
        (canvas['left'], canvas['top'], canvas['left'], canvas['bottom'] + 2)
    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
        (canvas['left'] - 2, canvas['bottom'],
         canvas['right'], canvas['bottom'])
    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
        (canvas['right'], canvas['bottom'] + 2, canvas['right'], canvas['top'])
    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
        (canvas['left'] - 2, canvas['top'], canvas['right'], canvas['top'])

    # the axis ticks
    for t in canvas['taxis'][1:-1]:
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (t * trans['tm'] + trans['tb'], canvas['bottom'] - 2,
           t * trans['tm'] + trans['tb'], canvas['bottom'] + 2)
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (t * trans['tm'] + trans['tb'], canvas['top'],
           t * trans['tm'] + trans['tb'], canvas['top'] + 2)

    for y in canvas['yaxis'][1:-1]:
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (canvas['left'] - 2, y * trans['ym'] + trans['yb'],
           canvas['left'] + 2, y * trans['ym'] + trans['yb'])
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
          (canvas['right'] - 2, y * trans['ym'] + trans['yb'],
           canvas['right'], y * trans['ym'] + trans['yb'])

    yield "</g>"

    # the t axis labels
    yield '<g font-family="Verdana" font-size="10px" ' + \
     'style="text-anchor: middle;">'
    for value, label in zip(canvas['taxis'], canvas['taxis_label']):
        yield '<text x="%s" y="%s">%s</text>' % \
        (value * trans['tm'] + trans['tb'], canvas['h'], label)

    # and the title
    yield '<text x="%s" y="%s">%s</text>' % \
      ((canvas['right'] - canvas['top']) / 2, canvas['top'] - 5, title)
    yield '</g>'

    # the y axis labels
    yield '<g font-family="Verdana" font-size="10px" ' + \
     'style="text-anchor:end;">'
    for value, label in zip(canvas['yaxis'], canvas['yaxis_label']):
        yield '<text x="%d" y="%s">%s</text>' % \
        (canvas['left'] - 6, value * trans['ym'] + trans['yb'] + 4, label)
    yield '</g>'


def canvas_dimensions(form, canvas_size=(750, 500)):
    """calculate dimensions of the canvas, making room for axes"""
    w, h = canvas_size

    # make axis ticks and labels
    taxis = [form['tmin'] + float(form['tmax'] - form['tmin']) * i / 10
      for i in range(11)]
    taxis_label = ["%.3g" % t for t in taxis]
    yaxis = [form['ymin'] + float(form['ymax'] - form['ymin']) * i / 10
      for i in range(11)]
    yaxis_label = ["%.3g" % y for y in yaxis]
    yaxis_label_width = max([len(label) for label in yaxis_label])

    # adjust canvas for labels
    top, bottom = 15, h - 15
    left, right = 6 * yaxis_label_width + 6, w - 15

    return {'top': top, 'left': left, 'bottom': bottom, 'right': right,
        'w': w, 'h': h, 'taxis': taxis, 'taxis_label': taxis_label,
        'yaxis': yaxis, 'yaxis_label': yaxis_label}


def svg_slopefield(canvas, tick_array, **kwargs):
    """Returns an svg image for a slopefield"""

    # beginning of svg
    yield """<svg viewBox="0 0 %(w)d %(h)d"
width="%(w)d" height="%(h)d"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">""" % canvas

    for line in axes(canvas, **kwargs):
        yield line

    # style for tick marks
    yield '<g style="stroke-width:1; stroke:black;">'

    for tick in tick_array:
        yield svg_tick(tick)

    # close out svg
    yield "</g></svg>"

###########################################
# Methods to create tick array
###########################################


def translation(p1, i1, p2, i2):
    """Returns the affine translation that takes p1 to i1 and p2 to i2"""
    stretch = (i2 - i1) / (p2 - p1)
    shift = i1 - stretch * p1
    return stretch, shift


def tick(t, y, f, length, trans):
    """Returns a tick centered at t,y with slope f(t,y) and given length"""
    tt = t * trans['tm'] + trans['tb']
    yy = y * trans['ym'] + trans['yb']
    slope = f(t, y)
    # just in case f is a constant function
    if not isinstance(slope, np.ndarray):
        constant = slope
        slope = t.copy()
        slope.fill(constant)

    # vector components
    vt = trans['tm']
    vy = trans['ym'] * slope
    # normalize
    norm = (vt ** 2 + vy ** 2) ** 0.5
    vt *= 0.5 * length / norm
    vy *= 0.5 * length / norm
    # combine
    out = np.vstack([tt - vt, yy - vy, tt + vt, yy + vy]).T

    # fix infinite slopes
    inf_mask = np.isinf(slope)
    inf_y = yy[inf_mask]
    out[inf_mask, 1] = inf_y - 0.5 * length
    out[inf_mask, 3] = inf_y + 0.5 * length

    # delete NaNs
    return out[~np.isnan(slope)]


def ticks_step(min, max, num_ticks):
    """Calculate steps and step size"""
    ticks, step = np.linspace(min, max, num_ticks,
      retstep=True, endpoint=False)
    return ticks + step / 2, step


def slopefield(form, trans):
    """Returns a slopefield array"""

    tticks, dt = ticks_step(form['tmin'], form['tmax'], form['tticks'])
    yticks, dy = ticks_step(form['ymin'], form['ymax'], form['yticks'])

    ts, ys = np.meshgrid(tticks, yticks)
    ticklength = 0.6 * min(abs(dt * trans['tm']), abs(dy * trans['ym']))

    return tick(ts.flatten(), ys.flatten(), form['fn'],
      ticklength, trans=trans)

###########################################
# Methods to create html output
###########################################


def html_output(params):
    """Generator for html output, one line at a time."""

    form = params
    try:
        form = sanitize(form)
    except SanitizeError as msg:
        form['content'] = "<p class='alert'>%s</p>" % msg
        yield TEMPLATE.safe_substitute(form)
        return
    else:
        form['title'] = "y'=" + form['fn_str']

    if not form['fn_str']:
        form['fn_str'] = ""
        form['fn'] = lambda t, y: 2 * y / tan(2 * t)
        form['title'] = "y'=2*y/tan(2*t)"

    # set up the canvas

    canvas = canvas_dimensions(form, canvas_size=(750, 500))

    # calculate the translation factors based on canvas dimensions
    trans = dict()
    trans['tm'], trans['tb'] = translation(form['tmin'], canvas['left'],
                              form['tmax'], canvas['right'])
    trans['ym'], trans['yb'] = translation(form['ymin'], canvas['bottom'],
                              form['ymax'], canvas['top'])

    # get a generator for the slopefield
    slopefield_generator = slopefield(form, trans=trans)

    svg_generator = svg_slopefield(canvas, slopefield_generator,
      trans=trans, title=form['title'])

    # print it out

    start, end = TEMPLATE.safe_substitute(form).split('$content', 1)

    yield start

    yield '<div id="plot">'

    for line in svg_generator:
        yield line

    yield '</div>'

    yield end

BLANK = "\n".join(html_output({'tmin': 0, 'tmax': 3, 'tticks': 21,
            'ymin': -1, 'ymax': 1, 'yticks': 15, 'fn_str': ""}))

