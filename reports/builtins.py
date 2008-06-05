from __future__ import absolute_import

import os, sys
import bisect
from Crypto.Cipher import Blowfish as blowfish
from sha import sha
from os import urandom as random
import xml.dom.minidom as dom
import re
from Queue import Queue, Empty

from turbogears import controllers, url, expose, flash, redirect
from cherrypy import session, request, response, HTTPRedirect
from turbogears.toolbox.catwalk import CatWalk
from docutils.core import publish_parts
from pydoc import html

from . import model as db

from .html import FixIE

import logging

class Presentation(object):
  def _path(self, path):
    return ('home', ) + path

  def __getattr__(self, operation):
    if operation in ['retrieve_css', 'retrieve_javascript']:  #Turbogears junk
      return None
    
    def default(obj,  path, **args):
      op = operation
      
      if not op:
        return self.show(obj, path, **args)

      concreteOp = getattr(obj, op)
      if not concreteOp:
        return self.show(obj, path) if op is not 'show' else None
        
      output = concreteOp(**args)
      if output is None:
        return self.show(obj, path) if op is not 'show' else None
    
      raise ReturnedObject(output)

    return default
    
  def write(self, obj, path, data=None):
    if not data:
      data = findPage(loginRoot(), ('~hand',)).getData()

    obj.write(data)
    raiseRedirectToShow(path)

  def copy(self, obj, path):
    session['hand'] = obj.descriptor
    raiseRedirectToShow(path)

  @FixIE
  @expose(template="reports.templates.search")
  def search(self, obj, path, query=None):
    if query is None:
      return dict(session=session, root=session['root'], results=[], path=self._path(path), name="Search", obj=obj)

    hits = {}
    root = loginRoot()
    pathCut = len(root.path)
#    assert False, (query.lower(), re.escape(query.lower()))
    query = re.compile(r'\b%s\b' % re.escape(query.lower()))
    
    def doSearch(page):
      if not page.data:
        return

      if page.id in hits:
        hits[page.id][1] -= 1          
        if query.search(page.path[-1].lower()):
          hits[page.id][0] -= 1
        return
      
      titleMatches = query.search(page.path[-1].lower())
      contentMatches = query.search(page.data.show(page).lower())

      if not (titleMatches or contentMatches):
        return
        
      #TODO check complexity on len(hits<dict>) 
      hits[page.id] = [0, 0, len(hits), page.name, page.id, page.path[pathCut:]]
      if titleMatches:
        hits[page.id][0] -= 1
      if contentMatches:
        hits[page.id][1] -= 1                    
            
    walk(root, doSearch)
    
    results = []
    for hit in hits.values():
      bisect.insort(results, hit)

    return dict(session=session, root=session['root'], results=results, path=self._path(path), name="Search", obj=obj)  
    
    raise ReturnedObject(results)
    return '\n'.join(results)    


  def changePermission(self, obj, path, link=None, permission=None, value=None):
    values = {'none': None, 'true': True, 'false': False}
    value = values[value.lower()]

    obj.changePermission(link, permission, value)
    raiseRedirectToShow(path)    

  def waitForChange(self, obj, path, hash=None):
    queue = Queue()
    action = lambda: queue.put(True)
    obj.watch(action)
    try:
#      yield '<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">\n'
      for interval in range(60 * 60):
        try:
          queue.get(timeout=5)
      #        response.status=204 #no content
#          yield  '''
#            <body onLoad="window.parent.location.reload()"></body></html>          
#          '''
          return
        except Empty:
          yield ' '  # requires patch to cherrypy
    finally:
      obj.removeWatch(action)
#      response.status=200 #reset content
  waitForChange._cp_config = {'response.stream': True}


class WikiPresentation(Presentation):
  def _path(self, path):
    return ('home', ) + path
  
  def _name(self, path):
    return self._path(path)[-1]

  @FixIE
  @expose(template="reports.templates.show")
  def show(self, obj,  path, formatted=True, prefix=None):
    content = obj.show(formatted=formatted, prefix=prefix)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  
    
  @FixIE
  @expose(template="reports.templates.edit")
  def edit(self, obj,  path):    
    return dict(session=session, this=self, prototype=obj.__class__.__name__, root=session['root'], name=self._name(path), path=self._path(path), data=obj.show(), obj=obj)  #XXX deprecate data;  'this' can't be called 'self'
    
  @expose()
  def save(self, obj, path, data='', save=None):    
    if 'file' in dir(data):  #allow file uploads, handled by the framework
      data = data.file.read()
    
    logging.getLogger('root.controller.http').debug("Wiki saving: %s %s", type(data), dir(data))
    obj.save(data)      

    flash("Changes saved!")
    raiseRedirectToShow(path)

  @expose()
  def append(self, obj, path, data='', submit=None):
    if 'file' in dir(data):
      data = data.file.read()     
    return self.save(obj, path, data=obj.show() + '\n' + data, )
    
  @expose()
  def prepend(self, obj, path, data='', submit=None):
    if 'file' in dir(data):
      data = data.file.read()
    return self.save(obj, path, data=data + '\n' + obj.show())
            
  @FixIE
  @expose(template="reports.templates.caps")    
  def links(self, obj, path):
    links = obj.links
    assert links is not None
    
    permissions = {}
    
    for id in links:
      if links[id][1] == 0:
        links[id] = (links[id][0], {})
        continue
        
      name, unset, set = links[id]

      links[id] = (name, {})
      for permission in unset:
        links[id][1][permission] = False
        if permission not in corePermissions:
          corePermissions.append(permission)

      for permission in set:
        links[id][1][permission] = True
        if permission not in corePermissions:
          corePermissions.append(permission)
                          
    return dict(session=session, root=session['root'], links=links, permissions=corePermissions, path=self._path(path), name=self._name(path), obj=obj)    
  
  @FixIE
  @expose(template="reports.templates.login")
  def login(self, obj, path, user=None, password=None, login=None):        
    while True:
      if not user and not password:
        response.status=403
        return dict(message="Please log in.")
        
      username = user
      user = findPage(None, [request.headers['Host'], user])
      if not user or not user.data:
        break        
      user = user.data
      if 'checkPassword' not in dir(user):
        break
      if not user.checkPassword(username, password):
        break
        
      session['root'] = (request.headers['Host'], username,)
      session['path'] = []    
      
      flash("Logged in as %s" % session['root'][-1])
      raiseRedirectToShow(['/'])

    msg=_("%s - Incorrect password or username." % username)
    response.status=403
    return dict(message=msg)

  @expose()
  def logout(self, obj,  path):
    del session['root']
    session['path'] = []    
    flash('Logged out')
    raiseRedirectToShow(['/'])

class PrimitivePresentation(WikiPresentation):
  @FixIE
  @expose(template="reports.templates.show")
  def show(self, obj, path, prefix=None):
    try:
      content = obj.show()
    except:
      content = html.escape("%s" % obj)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  

class RawPresentation(WikiPresentation):
  @expose()
  def show(self, obj, path, prefix=None, formatted=True):    
    return obj.show(formatted=formatted, prefix=None)

class XmlPresentation(WikiPresentation):
  @FixIE
  @expose(template="reports.templates.show")
  def show(self, obj, path, prefix=None, formatted=True):
    content = obj.show(formatted=formatted, prefix=None)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  

class Constructor(object):
  def __init__(self, class_=None):
    self.class_ = class_
    self.links = {}
  
  def show(self, page, prefix=None, formatted=False):
    return self.class_
    
  def save(self, page, class_):
    self.class_ = class_
    page.data = self

  def construct(self, page):    
    return metaTypes[self.class_]()

class Wiki(object):
  def __init__(self, data=''):
    self.data = data
    self.links = {}

  #This is becoming a problem
#  wikiWords = r'(?P<type>\[\(?)(?P<name>[^\ \[\]][^\[\]]*?\)?)\]'
#  inlineWords = r'(?P<type>\{)(?P<name>\(?[^\ \[\}][^\[\}]*?\)?)\}'

  linkWords = re.compile(r'(?P<type>[\[\(\{]+)(?P<name>[^\ \[\]\(\)\{\}][^\[\]]*?)[\]\)\}]+')
#  wikiWords = re.compile(wikiWords)
#  inlineWords = re.compile(inlineWords)   
  indentWords = re.compile(r'\s*\*')   
  
  def _wikiFormat(self, page, content, prefix=None):
    #  name = html.escape(name)
    if not prefix:
      prefix = tuple()

    def wikiLink(match):
      name = match.group('name')
      link = name[:-1] if name.endswith('*') else name
      link = '/'.join(prefix+(link,))
      return '<a href="http:%s/">%s</a>' % (link, name)
      
    def inlineLink(match):
      name = match.group('name')
      extension = tuple(name.split('/'))
      
      #meta = findPage(page, extension)
      assert len(extension) == 1, len(extension)
      meta = page.get(page.resolve(extension[0]), extension[0])
      
      inlineObject = meta.data
      if not inlineObject:
        return None
        
      presentation = Presentation()
      content = inlineObject.show(meta, prefix=prefix + extension, formatted=True) #XXX tuples, not list            
#      print content
      return content
#      return dom.parseString(content).getElementsByTagName('body')[0].toxml()
        
#      return findPage(page, name.split('/')).show(formatted=True, prefix=prefix+[name])
#      return '<a href="http:%s/">%s</a>' % name
  
#    content = commentblock.split(content)
    
    linkTypes = { "(": lambda match: match.group(0), "[(": lambda match: None, "[": wikiLink, "{": inlineLink }
    
    def replaceLink(match):
      name = match.group('name')
      return linkTypes[match.group('type')](match)
    
#    lastIndent = None
#    newContent = []
#    for line in content.splitlines():
#      matches = resolveWiki.indentWords.findall(line)
#      if matches and len(matches[0]) != lastIndent:
#        if lastIndent: 
#          newContent.append('\n')
#        lastIndent = len(matches[0])
#      if not matches:
#        lastIndent = None
#      newContent.append(line)
#    content = '\n'.join(newContent)        
    settings = { 'halt_level': 10, 'report_level': 10 }
    content = publish_parts(content, writer_name="html", settings_overrides=settings)['html_body']

    content = Wiki.linkWords.sub(replaceLink, ''.join(content))
#    content = Wiki.inlineWords.sub(inlineLink, ''.join(content))
#    content = Wiki.wikiWords.sub(wikiLink, ''.join(content))
    return content
    
  def show(self, page, formatted=False, prefix=None):
    if formatted:
      formatted = self._wikiFormat(page, self.data, prefix)
#      print formatted
      return formatted
    return self.data
          
  def save(self, page, data=''):    
    self.data, self.links = self.resolveWikiLinks(page, data)
    
    for key in self.links:
      self.links[key] = (db._assertId(self.links[key][0]),) + self.links[key][1:]
    page.data = self
            
  def list(self, page):
    return self.links

  def resolveWikiLinks(self, page, content):
    knownIds = {}
    for link in self.links:
      knownIds[self.links[link][0]] = self.links[link]
#      knownIds[page.get(self.links[link]).id] = self.links[link]

    templates = { "[(": "[(%s)]", "[": "[%s]", "{": "{%s}"}

    nameMapping = {}
    def resolveLinks(match):
      linkType = match.group('type')
      link = match.group('name')
     
#    content = Wiki.linkWords.split(content)


#    text = content[::2]
#    links = content[1::2]

#    for link in links:
      template = templates.get(linkType, None)
      if not template:
        return match.group(0)

      if not '/' in link and not '=' in link and link in self.links:
        nameMapping[link] = self.links[link]
        return template % link

      
      name = None
      if '=' in link:        
        name, link = link.split('=', 1)     
        if not link:  #[name=]
          return template % name
  
      if link.endswith('*'):
        return template % link
            
      path = link.split('/')
      if path and path[-1] == '':  # '/' goes to root, 'foo/bar/baz/' strips off the '/'
        path = path[:-1]
              
      if path[0] == '':
        path[0:1] = []
        meta = findPage(loginRoot(), path)
      else:
        meta = findPage(page, path)
      
      
#      assert False, (link.split('/'), path, s)
      if not path:
        name = 'home'        
      
      name = name if name else path[-1] if path else None	
  
      link = template % (name) 
      if not meta or not meta.id:
        if '/' in link:
          link = template % (link + '*')
        return link
      if meta.id in knownIds:
        nameMapping[name] = knownIds[meta.id]
      else:
        nameMapping[name] = meta.descriptor

      return link

    return Wiki.linkWords.sub(resolveLinks, content), nameMapping

  def resolve(self, page, name):
    if name in self.links:
      return self.links[name]
    elif name.lower() in '\n'.join(list(self.links)).lower():
      name = name.lower()
      for key in self.links:
        if name == key.lower():
          return self.links[key]
    else:
      return None      
    
  def link(self, page, name, id):
    logging.getLogger('root.controller.http').debug("Linking %s %s", name, id)
    if 'links' not in dir(self):
      self.links = {}
  
    self.links[name] = id
    page.data = self
    
class CapRoot(Wiki):
  def resolve(self, page, name):
    if name == '~hand':  # I don't like this
      return session.get('hand', None)
    return super(CapRoot, self).resolve(page, name)
#    return self.links.get(name, None)

class User(Wiki):
  def setPassword(self, page, password=None):
    logging.getLogger('root.controller.user').info("Setting password (%s)", page)
    self.salt = sha(os.urandom(64)).hexdigest()
    self.token = self.getToken(page, password)
    page.data = self
    flash("Password set successfully")

  def checkPassword(self, page, password):
    logging.getLogger('root.controller.user').info("Checking password (%s)", page)
    if 'salt' not in dir(self) or not self.salt:
      return True
    return self.getToken(page, password) == self.token
    
  def getToken(self, page, password):
    logging.getLogger('root.controller.user').debug("User: %s", page)
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

  def resolve(self, page, name):
    if name == '~hand':  #FIXME I don't like this
      return session['hand']
    return super(User, self).resolve(page, name)

class AutoLogin(Wiki):
  def show(self, obj, *args, **kargs):
    def login():
      if 'guest' not in session['root']:
        return
      user = findPage(obj, [self.links.keys()[0]])
      if not user or not user.data:
        return
      loginRoot(user)
      
      flash("Logged in as %s" % session['root'][-1])
      raiseRedirectToShow(['/'])

    return login() or Wiki.show(self, obj, *args, **kargs)

  @expose()
  def logout(self, obj,  path):
    del session['root']
    flash('Logged out')
    raiseRedirectToShow(['/'])
    
class Raw(object):
  def __init__(self, data=''):
    self.data = data
    self.links = {}

  def show(self, page, prefix=None, formatted=False):
    return self.data
    
  def save(self, page, data=''):
    self.data = data
    page.data = self
    
  def list(self, page):
    return self.links

  def resolve(self, page, name):
    return self.links.get(name, None)
    
  def link(self, page, name, id):
    self.links[name] = id    
    page.data = self

class XML(object):
  def __init__(self, data=''):
    self.data = data
    self.links = {}

  def show(self, page, prefix=None, formatted=False):
    if not formatted or not self.data:
      return self.data

    return dom.parseString(self.data).getElementsByTagName('body')[0].toxml()
    
  def save(self, page, data=''):
    self.data = data
    page.data = self
    
  def list(self, page):
    return self.links

  def resolve(self, page, name):
    return self.links.get(name, None)
    
  def link(self, page, name, id):
    self.links[name] = id    
    page.data = self    
        
metaTypes = dict((name, eval(name)) for name in ('Wiki', 'User', 'CapRoot', 'Raw', 'XML', 'Constructor', 'AutoLogin'))

