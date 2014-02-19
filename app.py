import os
from flask import Flask, request
import slopefield

app = Flask(__name__)

def parse_form(form):
    """Returns dictionary with pertinent data from a FieldStorage instance"""

    tmin = float(form.get("tmin", 0))
    tmax = float(form.get("tmax", 3))
    tticks = int(form.get('tticks', 21))

    ymin = float(form.get("ymin", -1))
    ymax = float(form.get("ymax", 1))
    yticks = int(form.get('yticks', 15))

    t0 = float(form.get("t0", 0))
    y0 = float(form.get("y0", 0))
    step = float(form.get("step", 0.1))
    drawsol = "" if form.get("drawsol", "off")=="off" else "checked"

    fn_str = form.get("fn", "")

    return {'tmin': tmin, 'tmax': tmax, 'tticks': tticks,
            'ymin': ymin, 'ymax': ymax, 'yticks': yticks,
            'step': step, 't0': t0, 'y0': y0, 'drawsol': drawsol,
            'fn_str': fn_str}


@app.route('/')
def graph():
    if request.args:
        params = parse_form(request.args)
        return "\n".join(slopefield.html_output(params))
    else:
        return slopefield.BLANK


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
