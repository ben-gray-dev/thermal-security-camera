from Adafruit_AMG88xx import Adafruit_AMG88xx
import os
import math
import time
import numpy as np
from scipy.interpolate import griddata
from colour import Color
import json

# file name for the data capture
FILENAME_FOR_CAPTURED_DATA = 'person_absent.json'

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

#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

time.sleep(10)
t_end = time.time() + 10
#let the sensor initialize
dataCaptured = []
time.sleep(.1)
while(time.time() < t_end):

	#read the pixels
	pixels = sensor.readPixels()
	interp = []
	#perform interpolation
	bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')

	for ix, row in enumerate(bicubic):
		for jx, pixel in enumerate(row):
			interp.append(int(pixel))
	dataCaptured.append(interp)


with open('%s.json' % FILENAME_FOR_CAPTURED_DATA, 'w') as f:
    f.write(json.dumps(dataCaptured))
