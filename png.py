#!env python

import ImageDraw
import os

d = '/home/cwillu/work/dominos/reports/reports/static/images/'

for f in os.listdir(d):
  if '.png' not in f:
    continue  

  image = ImageDraw.Image.open(d + f)
  image.save(d + f.replace('.png', '') + '.gif', format="GIF", transparency=225)
