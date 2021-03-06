from __future__ import absolute_import

# 9977553311

import os, sys
import bisect
import uuid
import math
import thread
from Crypto.Cipher import Blowfish as blowfish
from Crypto.Hash import SHA
#from os import urandom as random
from random import SystemRandom as sysrandom; random = sysrandom()
import xml.dom.minidom as dom
import re
import time

from Queue import Queue, Empty

from turbogears import controllers, url, expose, flash, redirect
from cherrypy import session, request, response, HTTPRedirect, server, config
from docutils.core import publish_parts
import pydoc

from . import model as db
from . import builtins
from . import html

try:  
  import psycos
  psyco.log()
#  psyco.full()
  compile = psyco.proxy
  
  def codeFilter(co):
    if 'enclosing_frame' in co.co_name:
      return False
    print co
    print co.co_name
    return True
  
  psyco.setfilter(codeFilter)
  expose = psyco.proxy(expose)
  
  from psyco.classes import *

except ImportError:
  print 'Psyco not installed, the program will just run slower'  
  compile = lambda func: func

compile = lambda func: func

import logging
logging.getLogger('root').setLevel(19)

logging.getLogger('root').info('\n' + "-" * 40 + '\nSystem Start')


def car(a, b):
  return a
def cdr(a, b):
  return b

class _(object):
  def __init__(self, **kargs):
    for k in kargs:
      setattr(self, k, kargs[k])

@compile
def bitString(bits, dictionary='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
  requiredLength = math.ceil(bits / math.log(len(dictionary), 2))
  return ''.join(random.choice(dictionary) for x in range(requiredLength))

@compile
def hexToBase(bits, dictionary='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
  base = len(dictionary)
  bits = long(bits, 16)
  output = []  
  while bits:
    output.insert(0, dictionary[bits % base])
    bits /= base
  return ''.join(output)

@compile
def baseToHex(bits, dictionary='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
  base = len(dictionary)
  output = 0l
  for digit in bits:
    output *= base
    output += dictionary.index(digit)
    
  assert type(output) is long
  return hex(output)[2:-1]

assert "71681123891927401278340" == baseToHex(hexToBase("71681123891927401278340"))
    
corePermissions = ['read', 'modify', 'replace', 'cross', 'override']


baseMeta = db.BaseComponent('pickles')/'web'

@compile
def visit(root, path, op):
  target = root if root else baseMeta
  if path is None:
    path = []
  
  result = op(None, target)
  for segment in path:
    assert type(segment) in [str, unicode], (path, segment, type(segment))
    source = target
    descriptor = source.resolve(segment)
      
    if not descriptor:
      return op(result, None)
                
    target = source.get(descriptor, segment)
    result = op(result, target)
  return result

@compile
def findPage(find, root, path):
  if '~hand' in path:
    path = path[list(path).index('~hand'):]
  
  return visit(root, path, lambda bestSoFar, page: visit(page, find, cdr) or bestSoFar)
  
@compile  
def getPage(root, path, onNew=None):
  if '~hand' in path:
    path = path[list(path).index('~hand'):]
    
  page = visit(root, path[:-1], cdr)
  page = visit(page, path[-1:], cdr) if page else False      

  if page is None:
    if onNew: 
      onNew()
    
    source = getPage(root, path[:-1])     
    def createLink(reifiedPage):  
      source.data.link(source, path[-1], reifiedPage.descriptor)
      
    return source.create(onReify=createLink, path=path)

  return page

@compile
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
      try:
        childNode = getPage(current, (link,))      
        if not childNode:  
          continue
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

class Wrapper(object):
  def __init__(self, data, page):
    if data is None and page is not None:
      data = page.data
#    if data is None:
#      raise AttributeError
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
    self.changePermission = page.changePermission
    self.permissions = page.permissions
        
  @property
  def descriptor(self):
    return self.page.descriptor
  
  @property
  def __class__(self):
    if not self._data:
      return Wrapper
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

def gateway():
  protocol = request.headers.get('X-Protocol', 'http')
  return "%s://%s" % (protocol, request.headers['Host'])
  
def loginRoot():
  session.setdefault('root', (gateway(), 'guest'))
  return getPage(None, ('gateways', gateway()))

class Root(controllers.RootController):  
  try:
    componentSecret = eval(open(os.path.expanduser('~/secret')).read())
  except IOError:
    componentSecret = uuid.uuid4()
    print >>open(os.path.expanduser('~/secret'), 'w'), "uuid.%s" % `componentSecret`
  
  def __init__(self):
    class DirtyHacks(object):
      def before_main(nested):
        self._cp_filters.remove(nested)
        for index, filter in enumerate(self._cp_filters):
          if filter.__class__.__name__ == 'NestedVariablesFilter':            
            self._cp_filters.remove(filter)            
            break  
    self._cp_filters = [DirtyHacks()]   
    
  @expose()
  def default(self, *path, **args):
    start = time.time()
    print
    print "\033[1;34m" + "*" * 80 + "\033[0m"
    print gateway(), path, args
    print request.browser_url
    print request.headers

    loginRoot()

    try:
      if not request.path.endswith('/'):
        raiseRedirectToShow((None,) + path)
         
      slug = re.findall(r'^~(.*)\((.*)-(.*)\)$', path[0]) if path else None
      if slug:
        name, salt, signature = slug.pop()
        path = ('protected', "~%s(%s)" % (name, salt)) + path[1:]

        if not self._checkSignature(path, signature):
          if self._checkSignaturePath(path, signature):  
            raiseRedirectToShow(path, self._signPath(path))
            
          response.status=403          
          flash('''bad signature (%s) ''' % (request.path, ))
          aBlank = blank()
          return self.findPresentation(aBlank).show(Wrapper(aBlank, None), path)               
      else:
        path = ('public',) + path
        pass
        
      return self.dispatch(path, args)
    finally:
      stop = time.time()
      print "\033[1;35m" + "Request finished: %10f" % (stop - start) + "\033[0m"
      print >>open('requestTimings', 'a'), "%10f" % (stop - start), request.browser_url 
  

  def addProtected(self, path):
    protectedRoot = getPage(loginRoot(), ('protected',))
    if not protectedRoot.descriptor:
      return None, None
    links = protectedRoot.data.links
    name = path[-1]

    requiredBits = max(32, math.log(len(links) + 1, 2))  
    while True:
      salt = bitString(requiredBits)
      if salt + ":" + name not in links:
        break              
   
    name = "~%s(%s)" % (name, salt)
    
    protectedRoot.data.link(protectedRoot, name, getPage(loginRoot(), path).descriptor)
    protectedPath = ['protected', name]
    
    return name, self._signPath(protectedPath)

  @compile
  def _checkSignaturePath(self, path, signature, maxDepth=128):
    if len(path) > maxDepth:
      return self._checkSignature(path, signature)       
    
    candidate = ''
    for index, segment in enumerate(path):
      candidate = SHA.new(candidate + segment).hexdigest()
      if hexToBase(SHA.new(candidate + str(Root.componentSecret)).hexdigest()[:20]) == signature:                
        #verify the implementations are in sync
        return self._checkSignature(path[:index+1], signature)  
    else:      
      return False

  def _checkSignature(self, path, signature):
    return signature == self._signPath(path)
  
  @compile  
  def _signPath(self, path):
    path = list(path)
    signature = ''
    for segment in path + [str(Root.componentSecret)]:
      signature = SHA.new(signature + segment).hexdigest()
    
    signature = hexToBase(signature[:20])
    #signature = hexToBase(reduce(lambda x, y: SHA.new(x + y).hexdigest(), [''] + path + [str(Root.componentSecret)])[:20])
    return signature
    
  def removeProtected(self, name):
    protectedRoot = getPage(loginRoot(), ('protected',))
    links = protectedRoot.data.links
    del links[name]
    protectedRoot.data.save(protectedRoot)

#  @FixIE
  @expose(template="reports.templates.login")
  def login(self, user=None, password=None, login=None):
    while True:
      protectedRoot = getPage(loginRoot(), ('protected',))
      if not protectedRoot.descriptor:                
        raise HTTPRedirect(request.browser_url.replace('http://', 'https://', 1))

      if not user and not password:
        response.status=403
        return dict(message="Please log in.")
        
      userName = user
      userPath = ['users', userName]
      userMeta = getPage(loginRoot(), userPath)
      if not userMeta or not userMeta.data:
        print "login fail at 1", userMeta, userMeta.data
        break        
      userObject = userMeta.data
      if 'checkPassword' not in dir(userObject):
        print "login fail at 2, checkPassword not in ", userObject 
        break
      if not userObject.checkPassword(userName, password):
        print "login fail at 3, invalid password"
        break

      #session['root'] = (request.headers['Host'], userName,)
      session['path'] = () 
      
      name, signature = self.addProtected(userPath)
      if not signature:
        print "login fail at 4, logins not being accepted"
        break
        
      #flash("Logged in as %s" % session['root'][-1])
      flash("Logged in as %s" % userName)
      raiseRedirectToShow(('protected', name), signature)

    msg=_("%s - Incorrect password or username." % user)
    response.status=403
    return dict(message=msg)

  @expose()
  def logout(self):
    session.pop('root', None)
    session['path'] = ()   
    flash('Logged out')
    raiseRedirectToShow(('public',))
    

  def dispatch(self, path, args):
    logging.getLogger('root.controller.http').debug("Dispatch: <%s> %s", '/'.join(path), args)
        
    op = str(args.pop('op', ''))
    prototype = args.pop('prototype', None)
    try:
      meta = self.find(path, args)           
              
      if not meta:
        response.status=404
        flash('''%s doesn't exist.''' % (((request.headers['Host'],) + path)[-1]))
        aBlank = blank()
        return self.findPresentation(aBlank).show(Wrapper(aBlank, None), path)
             
      if not meta._query('read'):
        obj = blank()        
      elif not meta.data:
        if not prototype:
          prototype = Wrapper(None, findPage(('prototype',), loginRoot(), path))
#          prototype = Wrapper(None, findPage(('prototype',), loginRoot(), path))
#          prototype.show()
          if prototype.show:
            prototype = prototype.show().strip().splitlines()[0].strip().strip('[()]')
          else:
            prototype = None
                   
        constructor = Wrapper(None, findPage(('prototype', prototype), loginRoot(), path)) if prototype else None
        if not constructor or not constructor.construct:
          logging.getLogger('root.controller.http').warn("Access denied for path %s, redirecting to %s", path, path[:-1])
          raise db.PermissionError(flash='''%s doesn't exist, and we couldn't find a default constructor to create it.''' % (path[-1]))
        
        obj = constructor.construct()
        prototypeName = obj.__class__.__name__
        flash('New page: %s (%s)' % (path[-1], prototypeName))
        
        logging.getLogger('root.controller.http').debug("Creating prototype %s: %s", prototype, obj)
      else:
        obj = meta.data
        logging.getLogger('root.controller.http').debug("Loading existing page: %s", obj)
        
      presentation = self.findPresentation(obj)
      self.updateCrumbTrail(path)
            
      try:
        concreteOp = getattr(presentation, op)
      except (UnicodeEncodeError, AttributeError), err:
        response.status=404
        flash('''%s not understood by type %s''' % (repr(op), obj.__class__.__name__))
        raiseRedirectToShow(path, self._signPath(path))      

      try:
        result = concreteOp(Wrapper(obj, meta), path, **args)
        if not result:
          raiseRedirectToShow(path, self._signPath(path))
        return result        
      except ReturnedObject, obj:
        meta = meta.create()
        meta.data = obj.data
        session['hand'] = meta.descriptor
        raiseRedirectToShow(path + ('~hand',), self._signPath(path + ('~hand',)))

    except db.PermissionError, err:
      response.status=404
      if err.flash:
        flash(err.flash)
      else:
        flash('''%s permission denied''' % (err.args[0].title(), ))

      aBlank = blank()
      return self.findPresentation(aBlank).show(Wrapper(aBlank, None), path)
 
  def find(self, path, args):
    prototype = str(args.pop('prototype', 'Default'))

    meta = getPage(loginRoot(), path)
    return meta
      
  def updateCrumbTrail(self, path): 
    trail = session.get('path', ())
    if not trail or not '/'.join(trail).startswith('/'.join((path))):
      logging.getLogger('root.controller.http').debug("Updating crumb trail: %s %s", trail, path)
      session['path'] = path
 
  def findPresentation(self, obj):
    return findPresentation(obj)

def findPresentation(obj):
  if isinstance(obj, Presentation):    
    Log.warn("default presentation used for object %s" % obj)
    return obj
  
  if isinstance(obj, builtins.Raw):
    return RawPresentation()
  
  if isinstance(obj, builtins.metaTypes['Editor']):
    return WiabPresentation()
  
  if isinstance(obj, tuple(builtins.metaTypes.values())):
    return WikiPresentation()
    
  return PrimitivePresentation()

def raiseRedirectToShow(path=None, signature=None, status=None):
  #import traceback; traceback.print_stack()  
  protocol = request.headers.get('X-Protocol', 'http')
  originalPath = request.browser_url.split('?', 1)[0]
          
  print "Redirect %s" % (path,)
  if not path:
    raise HTTPRedirect("%s://%s/" % (protocol, originalPath), status=status)

  source, path = path[0], path[1:]
  assert source in ['public', 'protected', None], source  
  if path and signature and re.findall(r'^~(.*)\((.*)\)$', path[0]):    
    name, salt = re.findall(r'^~(.*)\((.*)\)$', path[0]).pop()
    path = ("~%s(%s-%s)" % (name, salt, signature),) + path[1:]      
  redirect = "%s/" % '/'.join(('',)+path)
  assert '//' not in redirect, (path, redirect)
    
  raise HTTPRedirect('%s://%s' % (protocol, request.headers['host']) +redirect, status=status)

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
      data = getPage(loginRoot(), ('~hand',)).getData()

    obj.write(data)
    #raiseRedirectToShow(path)

  def copy(self, obj, path):
    session['hand'] = obj.descriptor
    #raiseRedirectToShow(path)

  @html.FixIE
  @expose(template="reports.templates.search")
  def search(self, obj, path, query=None):
    if query is None:
      return dict(session=session, root=session['root'], results=[], path=self._path(path), name="Search", obj=obj)

    hits = {}
    root = loginRoot()
    pathCut = len(root.path)
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
      try:
        contentMatches = query.search(page.data.show(page).lower())
      except AttributeError:
        contentMatches = None

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
    #return ''
    #raiseRedirectToShow()    

#  def waitForChange(self, obj, path, hash=None):
#    queue = Queue()
#    action = lambda: queue.put(True)
#    obj.watch(action)
#    try:
##      yield '<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">\n'
#      for interval in range(60 * 60):
#        try:
#          queue.get(timeout=5)
#      #        response.status=204 #no content
##          yield  '''
##            <body onLoad="window.parent.location.reload()"></body></html>          
##          '''
#          return
#        except Empty:
#          yield ' '  # requires patch to cherrypy
#    finally:
#      obj.removeWatch(action)
##      response.status=200 #reset content
#  waitForChange._cp_config = {'response.stream': True}
 
class blank(object):
  @html.FixIE
  def show(self, meta, formatted=None, prefix=None):
    return ''      

class WikiPresentation(Presentation):
  def _path(self, path):
    path = ('home', ) + path[1:]
    index = len(path)-1
    path += session.setdefault('path', ())[len(path):]
    path = (index, [('/'.join(('',) + path[1:index+1] + ('',)), segment) for index, segment in enumerate(path)])
    
    return path
  
  def _name(self, path):
    return path[-1]

  @html.FixIE
  @expose(template="reports.templates.show")
  def show(self, obj,  path, formatted=True, prefix=None):
    content = obj.show(formatted=formatted, prefix=prefix)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  
    
  @html.FixIE
  @expose(template="reports.templates.edit")
  def edit(self, obj,  path):    
    return dict(session=session, this=self, prototype=obj.__class__.__name__, root=session['root'], name=self._name(path), path=self._path(path), data=obj.show(), obj=obj)  #XXX deprecate data;  'this' can't be called 'self'
    
  #@expose()
  def save(self, obj, path, data='', save=None):    
    if 'file' in dir(data):  #allow file uploads, handled by the framework
      data = data.file.read()
    
    logging.getLogger('root.controller.http').debug("Wiki saving: %s %s", type(data), dir(data))
    data, links = self.resolveWikiLinks(path, obj.links, data)    
    
    obj.save(data, links)      

    flash("Changes saved!")
    #raiseRedirectToShow()

  #@expose()
  def append(self, obj, path, data='', submit=None):
    if 'file' in dir(data):
      data = data.file.read()     
    return self.save(obj, path, data=obj.show() + '\n' + data, )
    
  #@expose()
  def prepend(self, obj, path, data='', submit=None):
    if 'file' in dir(data):
      data = data.file.read()
    return self.save(obj, path, data=data + '\n' + obj.show())
            
  @html.FixIE
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
 
  def resolveWikiLinks(self, objectPath, links, content):
    knownIds = {}
    for link in links:
      knownIds[link] = links[link]

    templates = { "[(": "[(%s)]", "[": "[%s]", "{": "{%s}"}

    nameMapping = {}
    def resolveLinks(match):
      linkType = match.group('type')
      link = match.group('name')
     
      template = templates.get(linkType, None)
      if not template:
        return match.group(0)

      if not '/' in link and not '=' in link and link in links:
        nameMapping[link] = links[link]
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
        path[0:1] = ['~hand']
      else:
        path = objectPath + tuple(path)

      meta = getPage(loginRoot(), path) 
      
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

    return builtins.Wiki.linkWords.sub(resolveLinks, content), nameMapping

class WiabPresentation(WikiPresentation):
  @html.FixIE
  @expose(template="reports.templates.wiab")
  def show(self, obj,  path, formatted=True, prefix=None):    
    data = obj.show(formatted=formatted, prefix=prefix)
          
    pageWidth = sum(data.grid.x)
    output = []
    for content, dim in zip(data.content, data.dimensions):
      output.append(_(
        content=content, 
        x=sum(data.grid.x[:dim[0].x]),
        y=sum(data.grid.y[:dim[0].y]),
        width=sum(data.grid.x[dim[0].x:dim[1].x]),
        height=sum(data.grid.y[dim[0].y:dim[1].y]),
        css=[],
        styles=["wiab_west%s" % dim[0].x, "wiab_north%s" % dim[0].y, "wiab_east%s" % dim[1].x, "wiab_south%s" % dim[1].y],
      ))
     
    return dict(session=session, root=session['root'], data=output, pageWidth=pageWidth, path=self._path(path), name=self._name(path), obj=obj)

class PrimitivePresentation(WikiPresentation):
  @html.FixIE
  @expose(template="reports.templates.show")
  def show(self, obj, path, prefix=None):
    try:
      content = obj.show()
    except:
      content = pydoc.html.escape("%s" % obj)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  

class RawPresentation(WikiPresentation):
  @expose()
  def show(self, obj, path, prefix=None, formatted=True):    
    return obj.show(formatted=formatted, prefix=None)

class XmlPresentation(WikiPresentation):
  @html.FixIE
  @expose(template="reports.templates.show")
  def show(self, obj, path, prefix=None, formatted=True):
    content = obj.show(formatted=formatted, prefix=None)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  
    
#metaTypes = dict((name, eval('builtins.' + name)) for name in ('Wiki', 'User', 'CapRoot', 'Raw', 'XML', 'Constructor', 'AutoLogin'))
metaTypes = builtins.metaTypes

import nose
thread.start_new_thread(nose.run, ())
