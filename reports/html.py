from __future__ import absolute_import

import re

from cherrypy import request

#class FixIE(object):
def FixIE(presenter):
  img_png = re.compile(r'<img[^>]*>')
  attrs = re.compile(r'(\w+)="([^"]*)')

  def fixPNG(match):
    '''
    This looks like it should work, but DXImageTransform doesn't work under wine,
    so instead we just drop to a gif until I can confirm this works
    '''    
    iepng = "filter: progid:DXImageTransform.Microsoft.AlphaImageLoader(src='%s');"
  
    img = match.group(0)
    attributes = dict(attrs.findall(img))
    attributes['style'] = iepng % attributes['src'] + attributes.get('style', '')
    attributes['src'] = ''
    return "<img %s />" % ' '.join('%s="%s"' % (key, attributes[key]) for key in attributes)

  def replacePNG(match):
    img = match.group(0)
    attributes = dict(attrs.findall(img))
    attributes['src'] = attributes['src'].replace('.png', '.gif')  #-nq8.png
    return "<img %s />" % ' '.join('%s="%s"' % (key, attributes[key]) for key in attributes)

  def __call__(*args, **kargs):
    output = presenter(*args, **kargs)
    userAgent = request.headers["User-Agent"]
    if "MSIE" in userAgent and float(re.findall(r'MSIE (.*?);', userAgent)[0]) < 7:
      output = img_png.sub(replacePNG, output)
    return output
  return __call__

