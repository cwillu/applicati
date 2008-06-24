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
from . import builtins

import logging
logging.getLogger('root').setLevel(19)

logging.getLogger('root').info('\n' + "-" * 40 + '\nSystem Start')
if not os.fork():
  os.system('git add .')
#  os.system('cg-rm -a')
  os.system('git commit -a -m "$(date)"')
  sys.exit(0)


# import logging
# log = logging.getLogger("reports.controllers")

corePermissions = ['read', 'modify', 'replace', 'cross', 'override']

try:
  import psyco
  psyco.log()
  compile = psyco.proxy
  
  expose = psyco.proxy(expose)
except ImportError:
  print 'Psyco not installed, the program will just run slower'  
  compile = lambda func: func

@psyco.proxy
def visit(root, path, op):
  target = root
  if target is None:
    target = db.BaseComponent()
  if path is None:
    path = []
  
  result = op(target)
  for segment in path:
    assert type(segment) in [str, unicode], (path, segment, type(segment))
    source = target
    descriptor = source.resolve(segment)
      
    if not descriptor:
      logging.getLogger('root.controller.find').warn("Access to non-existant path attempted: %s %s", path, segment)
      return op(None)
                
    target = source.get(descriptor, segment)
    result = op(target)
  return result

@psyco.proxy
def findPageName(target, path, find=tuple()):
  """
  Ugly mess
  
  Check the chain represented by path from the graph root object, returning the
  descriptor of the final link, None if the final link doesn't exist, or False
  if there's a problem at an earlier point.
  
  If the path contains ~hand, then we skip to that point before we start.  This 
  allows navigating to that object without breaking the crumbtrail, but I'm not
  a big fan of the approach to providing it.
  
  If the optional parameter 'find' is specified, then at each segment in path,
  the find path is tested; the _last_ success is then returned.  (The more 
  straightforward approach of checking the last path first and working backwards
  isn't used because I'm a masochist; XXX)  
  """

  logging.getLogger('root.controller.find').debug(path)
  
  if '~hand' in path:
    path = path[list(path).index('~hand'):]
  
  if find:
    bestFound = None
    class _(object):
      def __init__(self):
        self.bestFound = (None, None)
      def __call__(self, page):
        if not page:
          return self.bestFound
        page, descriptor = findPageName(page, find)        
        if page:
          self.bestFound = (page, descriptor)
        return self.bestFound
    return visit(target, path, _())
  else:    
    page = target
    page = visit(page, path[:-1], op=lambda page: page)
    if not page:
      return False, None

    page = visit(page, path[-1:], op=lambda page: page)      
    return page, page.descriptor if page else None
      
@psyco.proxy  
def findPage(root, path, find=tuple(), onNew=None):
  reachable, descriptor = findPageName(root, path, find=find)
      
  if reachable:
    logging.getLogger('root.controller.find').debug("reachable")
    return reachable

  if reachable is None and not find:
    if onNew: onNew()
    source = findPage(root, path[:-1])     

    def createLink(reifiedPage):  
      source.data.link(source, path[-1], reifiedPage.descriptor)

    return source.create(onReify=createLink, path=path)
  
  return reachable

@psyco.proxy
def walk(root, action, maxDepth=5):
  stack = []
  seen = set()
  
  child = root.data  
  action(root)
  stack.append((root, child.list(root), 0)) 
  seen.add(root.id)

  while stack:
    current, links, depth = stack.pop(0)  #breadth first    
    for link in links:
      childNode = findPage(current, (link,))      
      if not childNode:  
        continue
      try:
        action(childNode)
        child = childNode.data      
      except db.PermissionError:
        continue

      if depth >= maxDepth:
        continue

      if childNode.id in seen:
        continue

      childList = getattr(child, 'list', lambda node: [])
      stack.append((childNode, childList(childNode), depth+1))
      seen.add(childNode.id)        

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
    attributes['src'] = attributes['src'].replace('.png', '.gif')
    return "<img %s />" % ' '.join('%s="%s"' % (key, attributes[key]) for key in attributes)

  def __call__(*args, **kargs):
    output = presenter(*args, **kargs)
    userAgent = request.headers["User-Agent"]
    if "MSIE" in userAgent and float(re.findall(r'MSIE (.*?);', userAgent)[0]) < 7:
      output = img_png.sub(replacePNG, output)
    return output
  return __call__
    

class Wrapper(object):
  def __init__(self, data, page):    
    self._data = data
    self.page = page
    if not page:
      self.permissions = ([], [])
      self.links = []
      return
    try:
      self.links = page.links      
    except db.PermissionError:
      self.permissions = ([], [])
      self.links = []
      return
    self.write = page.write
    self.watch = page.watch
    self.removeWatch = page.removeWatch
    self.changePermission = page.changePermission
    self.permissions = page.permissions
        
  @property
  def descriptor(self):
    return self.page.descriptor
  
  @property
  def __class__(self):
    ''' hack '''
    logging.getLogger('root.controller.wrapper').debug("Faking class: %s", self._data.__class__)
    return self._data.__class__
  
  def __getattr__(self, name):
    if not getattr(self._data, name, None):  #['retrieve_css', 'retrieve_javascript']: Turbogears junk    
      return None

    return lambda *args, **kargs: getattr(self._data, name)(self.page, *args, **kargs)

  def __str__(self):
    return str(self._data)

class ReturnedObject(Exception):
  def __init__(self, data):
    self.data = data

def loginRoot():
  if root and root.path:
    session['root'] = tuple(root.path)
    session['path'] = []    
  session.setdefault('root', (request.headers['Host'], 'guest'))
  
#  assert False, session['root']
#  return findPage(None, session['root'])
  return findPage(None, ('gateways', ) + session['root'])
#  return findPage(None, session['root'])
    

class Root(controllers.RootController):  
  @expose()
  def default(self, *path, **args):
    try:
      logging.getLogger('root.controller.http').info("Request: %s (%s)", path, args)            
      if not request.path.endswith('/'):
#        response.status=404
#        flash('''%s doesn't exist''' % (request.path, ))
#
#        loginRoot()
#        aBlank = blank()
#        return self.findPresentation(aBlank).show(Wrapper(aBlank, None), path)
        raiseRedirectToShow(path)
    
      signature = None
      if path and ':' in path[0]:
        signature, path[0] = path[0].split(':', 1)
        
      return self.dispatch(path, signature, args)
    finally:
      logging.getLogger('root.controller.http').debug("Request complete")


  def dispatch(self, path, signature, args):
    logging.getLogger('root.controller.http').debug("Dispatch: <%s> %s", '/'.join(path), args)
    
    loginRoot()
    op = args.pop('op', '')
    try:
#      meta = None  
      meta, obj = self.find(path, args)           
      presentation = self.findPresentation(obj)
      self.updateCrumbTrail(path)
            
      try:
        concreteOp = getattr(presentation, op)
      except (UnicodeEncodeError, AttributeError), err:
        response.status=404
        flash('''%s not understood by type %s''' % (repr(op), obj.__class__.__name__))
        raiseRedirectToShow(path)      

      try:
        result = concreteOp(Wrapper(obj, meta), path, **args)
        if not result:
          raiseRedirectToShow(path)
        return result        
      except ReturnedObject, obj:
        meta = meta.create()
        meta.data = obj.data
        session['hand'] = meta.descriptor
        raiseRedirectToShow(path + ('~hand',))

    except db.PermissionError, err:
      response.status=404
      if err.flash:
        flash(err.flash)
      else:
        flash('''%s permission denied''' % (err.args[0].title(), ))

      aBlank = blank()
      return self.findPresentation(aBlank).show(Wrapper(aBlank, meta), path)
 
  def find(self, path, args):
    prototype = args.pop('prototype', 'Default')

    meta = findPage(loginRoot(), path)
    if not meta:
      raise db.PermissionError(flash='''%s doesn't exist.''' % (((request.headers['Host'],) + path)[-1]))
#      raiseRedirectToShow(path[:-1], status=404)
           
    if not meta._query('read'):
      return meta, blank()
    elif not meta.data:
      constructor = findPage(loginRoot(), path, find=('Palette', prototype))
      if not constructor:
        logging.getLogger('root.controller.http').warn("Access denied for path %s, redirecting to %s", path, path[:-1])
        raise db.PermissionError(flash='''%s doesn't exist, and we couldn't find a default constructor to create it.''' % (path[-1]))
      
      obj = constructor.data.construct(constructor)
      protoTypeName = obj.__class__.__name__
      flash('New page: %s (%s)' % (path[-1], protoTypeName))
      
      logging.getLogger('root.controller.http').debug("Creating prototype %s: %s", prototype, obj)
    else:
      obj = meta.data
      logging.getLogger('root.controller.http').debug("Loading existing page: %s", obj)
      
    return meta, obj
  
  def updateCrumbTrail(self, path): 
    trail = session.get('path', [])
    if not trail or not '/'.join(trail).startswith('/'.join((path))):
      logging.getLogger('root.controller.http').debug("Updating crumb trail: %s %s", trail, path)
      session['path'] = (path)
 
  def findPresentation(self, obj):
    return findPresentation(obj)

def findPresentation(obj):
  if isinstance(obj, Presentation):    
    Log.warn("default presentation used for object %s" % obj)
    return obj
  
  if isinstance(obj, builtins.Raw):
    return RawPresentation()
  
  if isinstance(obj, tuple(builtins.metaTypes.values())):
    return WikiPresentation()
    
  return PrimitivePresentation()

def raiseRedirectToShow(path, status=None):
  if not path:
    raise HTTPRedirect("/", status=status)
  raise HTTPRedirect("/%s/" % '/'.join(path), status=status)


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
 
def blank():
  class Blank(object):
    @FixIE
    def show(self, meta, formatted=None, prefix=None):
      return ''
      '''    @expose(template="reports.templates.show")
    def blank(self, *args, **kargs):
      response.status=403
      return dict(session=session, root=session['root'], data='', path=(session['root'] + path), name=(session['root'] + path)[-1], obj=self)
     '''
  aBlank = Blank()

  return aBlank


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
    
metaTypes = dict((name, eval('builtins.' + name)) for name in ('Wiki', 'User', 'CapRoot', 'Raw', 'XML', 'Constructor', 'AutoLogin'))

#import cPickle as pickle
#pickle.dump([(o.name, o.data, o.id) for o in db.Object.select()], open('db.dump', 'w'))

#for name, data, id in pickle.load(open('db.dump')):
#  print name
#  db.Object(name=name, data=data, ident=id)

