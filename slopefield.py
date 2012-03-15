#! /usr/bin/python

__DEBUG = True

class Canvas:
    def __init__(self,xmin=-1,xmax=1,ymin=-1,ymax=1,canvas_size=(400,400)):
        self.xmin=xmin
        self.xmax=xmax
        self.ymin=ymin
        self.ymax=ymax
        self.canvas_w,self.canvas_h = canvas_size
        self.ctop,self.cbottom = 0,self.canvas_h
        self.cleft,self.cright = 0,self.canvas_w

        # sets up translation from x,y to canvas
        self.xm = float(self.cright-self.cleft)/(self.xmax-self.xmin)
        self.xb = self.cleft - self.xm * self.xmin
        self.ym = float(self.ctop-self.cbottom)/(self.ymax-self.ymin)
        self.yb = self.cbottom - self.ym * self.ymin

    def translate(self,tick):
        """Translates a tick from x,y coords to canvas coords"""
        x1,y1,x2,y2 = tick
        return [x1*self.xm + self.xb, y1*self.ym + self.yb,
                x2*self.xm + self.xb, y2*self.ym + self.yb]

    def svg_tick(self,tick):
        """Returns a line of svg representing the tick"""
        return '<line x1 = "%.03f" y1 = "%.03f" x2 = "%.03f" y2 = "%.03f" />' \
               % tuple(self.translate(tick))

    def svg_head(self):
        return """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20001102//EN" "svg-20001102.dtd">
<svg viewBox="0 0 600 600"
 xmlns="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink">
 <g style="stroke-width:1; stroke:black;">
 """

    def svg_foot(self):
        return "</g></svg>"



def tick(x,y,f,length):
    """Returns a tick centered at x,y with slope f(x,y) and given length"""
    try:
        slope = f(x,y)
    except ZeroDivisionError:
        # vertical tick on division by zero
        out = [x, y-0.5*length,
               x, y+0.5*length]
    except:
        # no tick on other error
        if __DEBUG:
            raise()
        else:
            out = [x,y,x,y]
    else:
        norm = (1+slope**2)**0.5
        vx = 0.5 * length / norm
        vy = 0.5 * slope * length / norm
        out = [x-vx, y-vy, x+vx, y+vy]

    return out

def slopefield(f,xmin=-1,xmax=1,ymin=-1,ymax=1,xticks=20,yticks=20):
    """Returns a generator for a slopefield"""
    assert 1 <= xticks <= 50 and 1 <= yticks <= 50
    dx = float(xmax-xmin)/(xticks+1)
    dy = float(ymax-ymin)/(yticks+1)
    ticklength = 0.7 * min(dx,dy)

    # loop
    x = xmin + 0.5 * dx
    while x < xmax:
        y = ymin + 0.5 * dy
        while y < ymax:
            yield tick(x,y,f,ticklength)
            y += dy
        x += dx

def svg_slopefield(f,xmin=-1,xmax=1,ymin=-1,ymax=1,canvas_size=(400,400),
               xticks=20,yticks=20):
    """Returns an svg image for a slopefield"""
    canvas = Canvas(xmin,xmax,ymin,ymax,canvas_size)
    yield canvas.svg_head()

    for tick in slopefield(f,xmin,xmax,ymin,ymax,xticks,yticks):
        yield canvas.svg_tick(tick)

    yield canvas.svg_foot()


if __name__ == "__main__":
    for line in svg_slopefield(lambda x,y: y):
        print line
