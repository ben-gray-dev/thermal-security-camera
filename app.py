

from flask import Flask, render_template
from flask_sse import sse
from flask import request
from multiprocessing import Process, Value
import time
import numpy
from Adafruit_AMG88xx import Adafruit_AMG88xx
import os
import math
import time
import numpy as np
from scipy.interpolate import griddata
from colour import Color
from joblib import load



# Citing use of Flask sse quickstart guide: https://flask-sse.readthedocs.io/en/latest/quickstart.html
# Citing use of Adafruit AMG8833 thermal_cam.py example code: https://github.com/adafruit/Adafruit_AMG88xx_python/blob/master/examples/thermal_cam.py

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')
runningProcs = []


# Load classification model
clf = load('personClassifier.joblib')

#low range of the sensor (this will be blue on the screen)
MINTEMP = 18

#high range of the sensor (this will be red on the screen)
MAXTEMP = 30

#how many color values we can have
COLORDEPTH = 1024

os.putenv('SDL_FBDEV', '/dev/fb1')


#initialize the sensor
sensor = Adafruit_AMG88xx()

points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

#sensor is an 8x8 grid so lets do a square
height = 240
width = 240

#the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30

@app.route('/')
def index():
    global MINTEMP
    global MAXTEMP
    global runningProcs
    min_temp = MINTEMP
    max_temp = MAXTEMP
    if 'mintemp' in request.args:
        min_temp = int(request.args.get('mintemp', ''))
    if 'maxtemp' in request.args:
        max_temp = int(request.args.get('maxtemp', ''))
    for proc in runningProcs:
        proc.terminate()
        proc.join()
    p = Process(target=record_loop, args=(min_temp, max_temp,))
    p.start()
    runningProcs = []
    runningProcs.append(p)
    return render_template("index.html")


#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def record_loop(min_temp, max_temp):
    #let the sensor initialize
    while(1):

        #read the pixels
        pixels = sensor.readPixels()
        raw_pixels = pixels
        pixels = [map(p, min_temp, max_temp, 0, COLORDEPTH - 1) for p in pixels]
        #data = numpy.asarray([pixels])
        #print(clf.predict(data))
        #print(pixels)
        interp = []
        predictor = []
        #perform interpolation
        bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
        rawbicubic = griddata(points, raw_pixels, (grid_x, grid_y), method='cubic')
        #draw everything
        for ix, row in enumerate(rawbicubic):
            for jx, pixel in enumerate(row):
                predictor.append(int(pixel))
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                interp.append(colors[constrain(int(pixel), 0, COLORDEPTH- 1)])
        data = numpy.asarray([predictor])
       	if clf.predict(data)[0] == 1:
            sse.publish({"message": "Person detected"}, type='classification')
        else:
            sse.publish({"message": "No person detected"}, type='classification')
        sse.publish({"message": interp}, type='pixels')







