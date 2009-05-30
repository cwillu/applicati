from __future__ import absolute_import

import os
from sha import sha
import xml.dom.minidom as dom
import re

from turbogears import flash
from cherrypy import session
from docutils.core import publish_parts

#import urllib

import logging

class _(object):
  def __init__(self, **kargs):
    for k in kargs:
      setattr(self, k, kargs[k])

try:  
  import psyco
  psyco.log()
  compile = psyco.proxy
  publish_parts = psyco.proxy(publish_parts)
  from psyco.classes import *
except ImportError:
  logging.getLogger('root.builtins').warn('Psyco not installed, the program will just run slower')  
  compile = lambda func: func

def _assertId(id):  #XXX change to assert
  '''from model'''
  
  logging.getLogger('root.model.descriptors').debug("ASSERTING %s", id)
  if not isinstance(id, tuple): 
    assert len(str(id)) > 10 or id == '1' or id == (1, ), (id, type(id)) #XXX fix root id
    logging.getLogger('root.model.descriptors').warn("old-style descriptor in use: %s (%s)", id, type(id))
    return (id, )
  return id

_nest=0

class Constructor(object):
  def __init__(self, class_=None):
    self.class_ = class_
    self.links = {}
  
  def show(self, meta, prefix=None, formatted=False):
    return self.class_
    
  def save(self, meta, class_, links=None):
    self.class_ = class_
    meta.data = self

  def construct(self, meta):    
    return metaTypes[self.class_]()

class Wiki(object):
  settings = { 'halt_level': 10, 'report_level': 10 }
  def __init__(self, data=''):
    self.data = data       
    self.published = publish_parts(data, writer_name="html", settings_overrides=self.settings)['html_body']
     
    self.links = {}

  linkWords = re.compile(r'(?P<type>[\[\(\{]+)(?P<name>[^\ \[\]\(\)\{\}][^\[\]]*?)[\]\)\}]+')
  indentWords = re.compile(r'\s*\*')   
  
  @compile  
  def _wikiFormat(self, meta, content, prefix=None):
    if not prefix:
      prefix = tuple()

    def wikiLink(match):
      name = match.group('name')
      link = name[:-1] if name.endswith('*') else name
      link = '/'.join(prefix+(link,))
      return '<a href="%s/">%s</a>' % (link, name)
      
    def inlineLink(match):
      name = match.group('name')
      extension = tuple(name.split('/'))
      
      assert len(extension) == 1, len(extension)
      linkMeta = meta.get(meta.resolve(extension[0]), extension[0])
      
      inlineObject = linkMeta.data
      if not inlineObject:
        return None
             
      content = inlineObject.show(linkMeta, prefix=prefix + extension, formatted=True) #XXX tuples, not list            
      return content

    linkTypes = { "(": lambda match: match.group(0), "[(": lambda match: None, "[": wikiLink, "{": inlineLink }
    
    def replaceLink(match):
      name = match.group('name')
      return linkTypes[match.group('type')](match)
    
    if hasattr(self, 'published'):
      content = self.published
    else: 
      content = publish_parts(content, writer_name="html", settings_overrides=self.settings)['html_body']

    content = Wiki.linkWords.sub(replaceLink, ''.join(content))
    return content
    
  def show(self, meta, formatted=False, prefix=None):
    if formatted:
      formatted = self._wikiFormat(meta, self.data, prefix)
      return formatted
    return self.data
          
  def save(self, meta, data='', links=None):    
    self.data = data
    self.published = publish_parts(data, writer_name="html", settings_overrides=self.settings)['html_body']
    if links is not None:
      self.links = links
    
    for key in self.links:
      self.links[key] = (_assertId(self.links[key][0]),) + self.links[key][1:]
    meta.data = self
            
  def list(self, meta):
    return self.links

  def resolve(self, meta, name):
    if name in self.links:
      return self.links[name]
    
    name = name.lower()
    for key in self.links:
      if hasattr(key, 'lower') and name == key.lower():
        return self.links[key]
    raise KeyError(name)
    
  def link(self, meta, name, id):
    logging.getLogger('root.controller.http').debug("Linking %s %s", name, id)
    if 'links' not in dir(self):
      self.links = {}
  
    self.links[name] = id
    meta.data = self
    
class CapRoot(Wiki):
  def resolve(self, meta, name):
    if name == '~hand':  # I don't like this
      return session.get('hand', None)
    return super(CapRoot, self).resolve(meta, name)

class User(Wiki):
  def setPassword(self, meta, password=None):
    logging.getLogger('root.controller.user').info("Setting password (%s)", meta)
    self.salt = sha(os.urandom(64)).hexdigest()
    self.token = self.getToken(meta, password)
    meta.data = self
    flash("Password set successfully")

  def checkPassword(self, meta, password):
    logging.getLogger('root.controller.user').info("Checking password (%s)", meta)
    if 'salt' not in dir(self) or not self.salt:
      return True
    return self.getToken(meta, password) == self.token
    
  def getToken(self, meta, password):
    logging.getLogger('root.controller.user').debug("User: %s", meta)
    logging.getLogger('root.controller.user').debug("Salt: %s", self.salt)
    
    token = sha(password).hexdigest()
    token = self.salt + token

    logging.getLogger('root.controller.user').debug("Hashing...")
    factor = 100000  # ~1 second for a single lookup
    token = reduce(lambda token, i: sha(token).digest(), xrange(factor), token)
    logging.getLogger('root.controller.user').debug("Done hashing")

    token = sha(token).hexdigest()
    logging.getLogger('root.controller.user').debug("Token: %s", token)

    return token 

  def resolve(self, meta, name):
    if name == '~hand':  #FIXME I don't like this
      return session['hand']
    return super(User, self).resolve(meta, name)

class AutoLogin(Wiki):
  '''Broken, relied on privileged access to findpage'''
  
  def show(self, obj, *args, **kargs):
    def login():
      return
      #if 'guest' not in session['root']:
      #  return
      #assert False, "findpage!?"
      #user = findPage(obj, [self.links.keys()[0]])
      #if not user or not user.data:
      #  return
      #loginRoot(user)
      #      
      #flash("Logged in as %s" % session['root'][-1])
      #raiseRedirectToShow(['/'])

    return login() or Wiki.show(self, obj, *args, **kargs)

  def logout(self, obj,  path):
    del session['root']
    flash('Logged out')
    raiseRedirectToShow(['/'])
    
class Raw(object):
  def __init__(self, data=''):
    self.data = data
    self.links = {}

  def show(self, meta, prefix=None, formatted=False):
    return self.data
    
  def save(self, meta, data='', links=None):
    self.data = data
    meta.data = self
    
  def list(self, meta):
    return self.links

  def resolve(self, meta, name):
    return self.links[name]
    
  def link(self, meta, name, id):
    self.links[name] = id    
    meta.data = self

class XML(object):
  def __init__(self, data=''):
    self.data = data
    self.links = {}

  def show(self, meta, prefix=None, formatted=False):
    if not formatted or not self.data:
      return self.data

    return dom.parseString(self.data).getElementsByTagName('body')[0].toxml()
    
  def save(self, meta, data='', links=None):
    self.data = data
    meta.data = self
                                
  def list(self, meta):
    return self.links

  def resolve(self, meta, name):
    return self.links[name]
    
  def link(self, meta, name, id):
    self.links[name] = id    
    meta.data = self    
        
class Clone(object):
  def __init__(self, source=""):
    self.source = source
    self.data = None
    
  def setSource(self, meta, source=""):
    self.source = source
    meta.data = self
            
  def show(self, meta):
    if not self.data:
      meta.data = self
    
    return self.data

class Editor(Wiki):
  def __init__(self, data=''):
    self.data = data
    self.links = {}
    
  def resolve(self, meta, name):
    raise KeyError(name)
    
  def link(self, meta, name, id):
    pass
    
  def list(self, meta):
    pass
  
  def show(self, meta, formatted=False, prefix=None):
    self.reset(meta)
    return self.data

  def reset(self, meta):    
    self.data = _(
      content=[ 
        'Lorem Ipsum Dolor Sit Amet',
        '<br />'.join('consectetuer adipiscing elit Curabitur semper'.split(' ')),
        ' | '.join('Aliquam ullamcorper suscipit est'.split(' ')),
        """<p>Mauris a pede at nulla auctor tristique. Aenean tortor libero, feugiat sed, eleifend nec, interdum vel, lacus. Nunc ultrices placerat arcu. Donec mi felis, vestibulum at, scelerisque eget, ultrices nec, mauris. Fusce scelerisque sodales odio. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Duis mauris tortor, elementum ut, mattis nec, semper vitae, eros. Suspendisse purus nisl, porta a, dapibus non, sollicitudin sit amet, urna. Nulla faucibus pharetra eros. Mauris velit tellus, tincidunt at, sollicitudin at, tempor eu, tortor. Etiam nisi. Etiam venenatis risus vitae arcu. Suspendisse dictum nisi sit amet dolor hendrerit lacinia.</p>

<p>Proin mattis. Vestibulum rutrum eleifend ante. Aenean nunc pede, commodo in, fringilla id, dictum ac, pede. Curabitur et enim. Cras in lorem ut nisi auctor pretium. Vestibulum metus turpis, volutpat eget, sodales quis, ultricies aliquam, erat. Vestibulum vehicula mi eu pede. Maecenas pretium. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Duis quis mauris. Proin vehicula sollicitudin felis. Nulla id velit. Praesent nec libero ac libero tempus pharetra. Mauris enim turpis, volutpat in, dignissim ac, rhoncus quis, est. Proin diam. Praesent euismod tristique tortor.</p>

<p>Duis lobortis magna quis tellus. Morbi auctor, dui et luctus ultricies, neque dolor adipiscing lectus, elementum feugiat nisi tortor in erat. Aenean sed nisi id diam ultricies aliquet. Aenean eros nisi, fermentum sed, vehicula vitae, tristique sollicitudin, enim. Integer tempus cursus justo. Suspendisse nibh. Etiam suscipit ipsum sed sem. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Curabitur at eros. Donec venenatis. Curabitur augue dolor, condimentum mollis, pellentesque commodo, varius ultrices, purus.</p>""",
        """Maecenas augue pede, venenatis id, facilisis a, pellentesque ut, nunc. Proin vulputate. Nullam mi. Etiam posuere turpis nec dolor. Quisque ut lorem sit amet tortor ultricies iaculis. Fusce placerat diam eu lorem. Aliquam neque arcu, consequat sit amet, laoreet ut, tincidunt vel, purus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Duis risus. Vivamus pellentesque purus sit amet urna. Morbi quis orci. Ut ipsum ligula, vehicula congue, molestie ac, interdum at, urna. Nam sed elit. Etiam faucibus, odio tristique dignissim consectetuer, purus urna ullamcorper leo, at molestie mi lorem eu erat. Cras a metus.""",
        'Phasellus vehicula, ipsum vel commodo dapibus, turpis pede aliquam sapien, eu facilisis diam nisi ac augue.',
        'Donec auctor dolor a elit. Pellentesque sollicitudin odio nec metus.',
        ], 
      grid=_(x=[120,640,240], y=[100,50,360,100,100]),      
      dimensions=[
        (_(x=0, y=0), _(x=3, y=1)), #h
        (_(x=0, y=1), _(x=1, y=3)), #*
        (_(x=1, y=1), _(x=3, y=2)), #t
        (_(x=1, y=2), _(x=2, y=3)), #c
        (_(x=2, y=2), _(x=3, y=4)), #s
        (_(x=0, y=3), _(x=2, y=4)), #f
        (_(x=0, y=4), _(x=3, y=5)), #@
        ], 
      )    
          
#  def save(self, meta, data='', links=None):    
#    pass
        
metaTypes = dict((name, eval(name)) for name in ('Wiki', 'User', 'CapRoot', 'Raw', 'XML', 'Constructor', 'AutoLogin', 'Clone', 'Editor'))

