import re
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
    tticks = clip(cgi_get('tticks',40,int),10,50)

    ymin = cgi_get("ymin",-1)
    ymax = cgi_get("ymax",1)
    yticks = clip(cgi_get('yticks',30,int),10,40)

    # ensure that delta_t and delta_y will be positive
    if (tmax-tmin)/tticks <= 0 :
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
        'Syntax Error. Something is wrong with the function you entered.\
        Common mistakes include writing <tt>3x</tt> instead of <tt>3*x</tt> or\
        <tt>sin t</tt> instead of <tt>sin(t)</tt>.')
    except NameError as S:
        write_log(log_file,fn_str,S,'eval')
        raise SanitizeError(
         'Something is wrong with the function you entered')
    except Exception as S:
        write_log(log_file,fn_str,S,'eval')
        raise SanitizeError(
          'Something is wrong with the function you entered.')

    # sanity check
    try:
        output = fn(1.25,0.75)
    except (ValueError, ZeroDivisionError, OverflowError):
        pass
    except Exception as S:
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

class Canvas:
    def __init__(self,tmin=-1,tmax=1,ymin=-1,ymax=1,
      canvas_size=(400,400),title=""):
        self.tmin=tmin
        self.tmax=tmax
        self.ymin=ymin
        self.ymax=ymax
        self.canvas_w,self.canvas_h = canvas_size
        self.title = title

        # make axis ticks and labels

        self.xaxis = [tmin + float(tmax-tmin)*i/10 for i in range(11)]
        self.xaxis_label = ["%.3g" % x for x in self.xaxis]
        self.yaxis = [ymin + float(ymax-ymin)*i/10 for i in range(11)]
        self.yaxis_label = ["%.3g" % y for y in self.yaxis]
        self.yaxis_label_width = max([len(label) for label in self.yaxis_label])

        # adjust for labels
        self.ctop,self.cbottom = 15,self.canvas_h - 15
        self.cleft,self.cright = 5*self.yaxis_label_width+5,self.canvas_w-15

        # sets up translation from x,y to canvas
        self.xm = float(self.cright-self.cleft)/(self.tmax-self.tmin)
        self.xb = self.cleft - self.xm * self.tmin
        self.ym = float(self.ctop-self.cbottom)/(self.ymax-self.ymin)
        self.yb = self.cbottom - self.ym * self.ymin

    def translate_tick(self,tick):
        x1,y1,x2,y2=tick
        out = self.translate(x1,y1)
        out.extend(self.translate(x2,y2))
        return out

    def translate(self,x,y):
        """Translates a tick from x,y coords to canvas coords"""
        return [self.translate_x(x), self.translate_y(y)]

    def translate_x(self,x):
        return x*self.xm + self.xb

    def translate_y(self,y):
        return y*self.ym + self.yb

    def svg_tick(self,tick):
        """Returns a line of svg representing the tick"""
        return '<line x1 = "%.03f" y1 = "%.03f" x2 = "%.03f" y2 = "%.03f" />' \
               % tuple(self.translate_tick(tick))

    def svg_head(self):
        yield """<svg viewBox="0 0 %d %d"
 xmlns="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink">""" % (self.canvas_w,
                                                   self.canvas_h)
        for line in self.axes():
            yield line

        yield '<g style="stroke-width:1; stroke:black;">'

    def svg_foot(self):
        return "</g></svg>"

    def axes(self):
        """Creates a box with axis labels"""

        # the box
        yield '<g style="stroke-width:1; stroke:grey;">'
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
              (self.cleft,self.ctop,self.cleft,self.cbottom+2)
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
              (self.cleft-2,self.cbottom,self.cright,self.cbottom)
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
              (self.cright,self.cbottom+2,self.cright,self.ctop)
        yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
              (self.cleft-2,self.ctop,self.cright,self.ctop)
        #if self.tmin < 0 < self.tmax:
        #    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
        #      (self.translate_x(0),self.ctop,self.translate_x(0),self.cbottom)
        #if self.ymin < 0 < self.ymax:
        #    yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
        #      (self.cleft,self.translate_y(0),self.cright,self.translate_y(0))


        # the ticks
        for x in self.xaxis[1:-1]:
            yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
              (self.translate_x(x),self.cbottom-2,
               self.translate_x(x),self.cbottom+2)
            yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
              (self.translate_x(x),self.ctop,
               self.translate_x(x),self.ctop+2)



        for y in self.yaxis[1:-1]:
            yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
              (self.cleft-2,self.translate_y(y),
               self.cleft+2,self.translate_y(y))
            yield '<line x1="%s" y1="%s" x2="%s" y2="%s" />' % \
              (self.cright-2,self.translate_y(y),
               self.cright,self.translate_y(y))

        yield "</g>"

        # the x axis labels
        yield '<g font-family="Verdana" font-size="10px"\
         style="text-anchor: middle;">'
        for value,label in zip(self.xaxis,self.xaxis_label):
            yield '<text x="%s" y="%s">%s</text>' % \
            (self.translate_x(value),self.canvas_h,label)

        # and the title
        yield '<text x="%s" y="%s">%s</text>' % \
          (float(self.cright-self.ctop)/2,self.ctop-5,self.title)
        yield '</g>'

        # the y axis labels
        yield '<g font-family="Verdana" font-size="10px"\
         style="text-anchor:end;">'
        for value,label in zip(self.yaxis,self.yaxis_label):
            yield '<text x="%d" y="%s">%s</text>' % \
            (self.yaxis_label_width*5,self.translate_y(value)+4,label)
        yield '</g>'

def tick(t,y,f,length):
    """Returns a tick centered at t,y with slope f(t,y) and given length"""
    try:
        slope = f(t,y)
    except ZeroDivisionError:
        # vertical tick on division by zero
        out = [t, y-0.5*length,
               t, y+0.5*length]
    except OverflowError:
        out = [t, y-0.5*length,
               t, y+0.5*length]
    except:
        out = [t,y,t,y]
    else:
        norm = (1+slope**2)**0.5
        vt = 0.5 * length / norm
        vy = 0.5 * slope * length / norm
        out = [t-vt, y-vy, t+vt, y+vy]

    return out

def slopefield(f,tmin=-1,tmax=1,ymin=-1,ymax=1,tticks=20,yticks=20):
    """Returns a generator for a slopefield"""
    assert 1 <= tticks <= 50 and 1 <= yticks <= 50
    dx = float(tmax-tmin)/(tticks+1)
    dy = float(ymax-ymin)/(yticks+1)
    ticklength = 0.6 * min(dx,dy)

    # loop
    x = tmin + 0.5 * dx
    while x < tmax:
        y = ymin + 0.5 * dy
        while y < ymax:
            yield tick(x,y,f,ticklength)
            y += dy
        x += dx

def svg_slopefield(f,tmin=-1,tmax=1,ymin=-1,ymax=1,tticks=20,yticks=20,
                   canvas_size=(750,500),title=""):
    """Returns an svg image for a slopefield"""
    canvas = Canvas(tmin,tmax,ymin,ymax,canvas_size,title)

    for line in canvas.svg_head():
        yield line

    for tick in slopefield(f,tmin,tmax,ymin,ymax,tticks,yticks):
        yield canvas.svg_tick(tick)

    yield canvas.svg_foot()

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
        except SanitizeError as msg:
            form['content'] = "<p class='alert'>" + msg + "</p>"
            yield Template(open(template_file).read()).safe_substitute(form)
            return
        else:
            form['title'] = "y'=" + form['fn_str']


    # print the graph
    start,end = Template(open(template_file).read()).safe_substitute(form)\
      .split('$content',1)

    yield start

    yield '<div id="plot">'

    for line in svg_slopefield(
      form['fn'],form['tmin'],form['tmax'],form['ymin'],form['ymax'],
      form['tticks'],form['yticks'],title=form['title']):
        yield line

    yield '</div>'

    yield end
