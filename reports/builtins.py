from __future__ import absolute_import

import os
from hashlib import sha1 as sha
import xml.dom.minidom as dom
import re

from jinja2 import Environment, FileSystemLoader, Markup
jinja = Environment(loader=FileSystemLoader('templates'), autoescape=True)

#from turbogears import flash
flash = lambda *a, **k: None
from docutils.core import publish_parts

#import urllib

import logging

class _(object):
  def __init__(self, **kargs):
    for k in kargs:
      setattr(self, k, kargs[k])

#try:  
#  import psyco
#  psyco.log()
#  compile = psyco.proxy
#  publish_parts = psyco.proxy(publish_parts)
#  from psyco.classes import *
#except ImportError:
#  logging.getLogger('root.builtins').warn('Psyco not installed, the program will just run slower')  
#  compile = lambda func: func

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
#    if name == '~hand':  # I don't like this
#      from cherrypy import session
#      return session.get('hand', None)
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
        
class Base(object):
  def __init__(self):
    self.links = {}
    
  def save(self, meta, data):
    pass
  
  def resolve(self, meta, name):
    return self.links[name]
      
  def link(self, meta, name, id):
    self.links[name] = id
    meta.data = self
  

class Blog(Base):
  def __init__(self, data=''):
    self.data = data
    super(Blog, self).__init__()
    
  def init(self, meta):
    meta.posts = Wiki()
    meta.categories = Wiki()

    meta.publisher = BlogPublisher()
    meta.publisher.blog = meta.self
  
class BlogPublisher(Base):
  def __init__(self, data=''):
    self.data = data
    super(BlogPublisher, self).__init__()

  def show(self, meta, posts):
    return posts
    template = jinja.get_template('contacts/contact.html')
    context = {
      'posts': posts,
    }
    return template.render(**context)
    
    
    
class BlogCategory(Base):
  def __init__(self, data=''):
    self.data = data
    super(BlogCategory, self).__init__()

  def posts(self, meta):
    pass

metaTypes = dict((name, eval(name)) for name in ('Wiki', 'User', 'CapRoot', 'Raw', 'XML', 'Constructor', 'AutoLogin', 'Blog',))

