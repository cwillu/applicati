import os, sys
from Crypto.Cipher import Blowfish as blowfish
from sha import sha
from os import urandom as random
import xml.dom.minidom as dom
import re
from Queue import Queue, Empty

from turbogears import controllers, url, expose, flash, redirect
from cherrypy import session, request, response
from turbogears.toolbox.catwalk import CatWalk
from docutils.core import publish_parts
from pydoc import html

import model as db

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
  
  if target is None:
    target = db.BaseComponent()
  
#  if target.data is None:  #move to model
#    target.data = CapRoot()    

  bestFoundForFind = None
  if find:
    logging.getLogger('root.controller.find').debug("searching", find)
    _reachable, _descriptor = findPageName(target, find)
    if _reachable:
      logging.getLogger('root.controller.find').debug("found", find)
      bestFoundForFind = _reachable, _descriptor


  if not path:  #no root user  
    if bestFoundForFind:
      return bestFoundForFind
  
    return target, target.descriptor #XXX
#    return (False, None)


  for index, segment in enumerate(path[:-1]):
    assert type(segment) in [str, unicode], (path, segment, type(segment))
    source = target
    descriptor = source.resolve(segment)
      
    if not descriptor:
      logging.getLogger('root.controller.find').warn("Access to non-existant path attempted: %s %s", path, segment)
      if bestFoundForFind:
        return bestFoundForFind
      return False, None
          
    target = source.get(descriptor, segment)
    if not target:
      assert False, ("Invalid signature!", type(descriptor), descriptor)
      if bestFoundForFind:
        return bestFoundForFind
      return False, None
    
    if find:
      _reachable, _descriptor = findPageName(target, find)
      if _reachable:
        logging.getLogger('root.controller.find').debug("found %s", path[:index] + find)
        bestFoundForFind = _reachable, _descriptor

  for segment in path[-1:]:
    source = target

    logging.getLogger('root.controller.find').debug("segment: %s", segment)
  
    descriptor = source.resolve(segment)  
    logging.getLogger('root.controller.find').debug(descriptor)
    
    if not descriptor:
      logging.getLogger('root.controller.find').debug("no descriptor")
      if bestFoundForFind:
        return bestFoundForFind
      return None, None

    target = source.get(descriptor, segment)    

    if not target:
      logging.getLogger('root.controller.find').debug("no page")
      if bestFoundForFind:
        return bestFoundForFind
      return None, None

    if find:
      _reachable, _descriptor = findPageName(target, find)
      if _reachable:
        logging.getLogger('root.controller.find').debug("found %s", path + find)
        bestFoundForFind = _reachable, _descriptor

  if find:
    logging.getLogger('root.controller.find').debug("************ %s", bestFoundForFind)
  if bestFoundForFind:
    return bestFoundForFind
  return target, descriptor
      
  
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

def visit(root, action, maxDepth=5):
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
      if childNode.id in seen:
        continue
      try:
        action(childNode)
        child = childNode.data      
      except db.PermissionError:
        continue

      if depth >= maxDepth:
        continue

      childList = getattr(child, 'list', lambda node: [])
      stack.append((childNode, childList(childNode), depth+1))
      seen.add(childNode.id)        
    

class Wrapper(object):
  def __init__(self, data, page):    
    self._data = data
    self.page = page
    if not page:
      self.permissions = ([], [])
      return
    self.write = page.write
    self.links = page.links
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
    if not getattr(self._data, name):  #['retrieve_css', 'retrieve_javascript']: Turbogears junk    
      return None

    return lambda *args, **kargs: getattr(self._data, name)(self.page, *args, **kargs)

  def __str__(self):
    return str(self._data)

class ReturnedObject(Exception):
  def __init__(self, data):
    self.data = data

def loginRoot():
  # (, <username>)
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
        redirectToShow(path)
      return self.dispatch(path, args)
    finally:
      logging.getLogger('root.controller.http').debug("Request complete")


  def dispatch(self, path, args):
    logging.getLogger('root.controller.http').debug("Dispatch: <%s> %s", '/'.join(path), args)
    op = args.pop('op', '')
    try:
      meta = None  
      meta, obj = self.find(path, args)           
      presentation = self.findPresentation(obj)
      self.updateCrumbTrail(path)
            
      try:
        concreteOp = getattr(presentation, op)
      except AttributeError, err:
        response.status=404
        flash('''%s not understood by type %s''' % op, obj.__class__.__name__)
        redirectToShow(path)      

      try:
        result = concreteOp(Wrapper(obj, meta), path, **args)
        if not result:
          redirectToShow(path)
        return result        
      except ReturnedObject, obj:
        presentation = self.findPresentation(obj.data)      
        meta = meta.create()
        meta.data = obj.data
        session['hand'] = meta.descriptor
        redirectToShow(path + ('~hand',))

    except db.PermissionError, err:
      response.status=403
      flash('''%s permission denied''' % (err.args[0].title(), ))

      aBlank = blank()
      return self.findPresentation(aBlank).show(Wrapper(aBlank, meta), path)
 
  def find(self, path, args):
    prototype = args.pop('prototype', 'Default')

    def onNew():
      flash('New page: %s (%s)' % (path[-1], prototype))
          
    meta = findPage(loginRoot(), path, onNew=onNew)
    if not meta:
      response.status=404
      flash('''%s doesn't exist.''' % (path[-1]))
      redirectToShow(path[:-1])
           
    if not meta._query('read'):
      return meta, blank()
    elif not meta.data:
      constructor = findPage(loginRoot(), path, find=('Palette', prototype))
      if not constructor:
        response.status=404
        flash('''%s doesn't exist, and we couldn't find a default constructor to create it.''' % (path)[-1])
        redirectToShow(path[:-1])
        
      obj = constructor.data.construct(constructor)

      logging.getLogger('root.controller.http').debug("Creating prototype %s: %s", prototype, obj)
    else:
      obj = meta.data
      logging.getLogger('root.controller.http').debug("Loading existing page: %s", obj)
      
    return meta, obj
  
  def updateCrumbTrail(self, path): 
    if not '/'.join(session.get('path', [])).startswith('/'.join((path))):
      logging.getLogger('root.controller.http').debug("Updating crumb trail: %s %s", session.get('path', []), path)
      session['path'] = (path)
 
  def findPresentation(self, obj):
    return findPresentation(obj)

def findPresentation(obj):
  if isinstance(obj, Presentation):    
    Log.warn("default presentation used for object %s" % obj)
    return obj
  
  if isinstance(obj, Raw):
    return RawPresentation()
  
  if isinstance(obj, tuple(metaTypes.values())):
    return WikiPresentation()
    
  return PrimitivePresentation()

def redirectToShow(path):
  raise redirect("/%s/?op=show" % '/'.join(path))


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

      output = getattr(obj, op)(**args)
      if output is None:
        return self.show(obj, path) if op is not 'show' else None
    
      raise ReturnedObject(output)

    return default
    
  def write(self, obj, path, data=None):
    if not data:
      data = findPage(loginRoot(), ('~hand',)).getData()

    obj.write(data)
    redirectToShow(path)

  def copy(self, obj, path):
    session['hand'] = obj.descriptor
    redirectToShow(path)

  @expose(template="reports.templates.search")    
  def search(self, obj, path, query):
    results = []
    seen = set()
    root = loginRoot()
    pathCut = len(root.path)
    def doSearch(page):
      if not page.data:
        return
      if query not in page.data.show(page).lower():
        return
      if page.id in seen:
        return
      results.append((page.name, page.id, page.path[pathCut:]))
      seen.add(page.id)
      
    visit(root, doSearch)
    
    return dict(session=session, root=session['root'], results=results, path=self._path(path), name="Search", obj=obj)  
    
    raise ReturnedObject(results)
    return '\n'.join(results)    


  def changePermission(self, obj, path, link=None, permission=None, value=None):
    values = {'none': None, 'true': True, 'false': False}
    value = values[value.lower()]

    obj.changePermission(link, permission, value)
    redirectToShow(path)    

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

  @expose(template="reports.templates.show")
  def show(self, obj,  path, formatted=True, prefix=None):
    content = obj.show(formatted=formatted, prefix=prefix)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  
    
  @expose(template="reports.templates.edit")
  def edit(self, obj,  path):    
    return dict(session=session, this=self, prototype=obj.__class__.__name__, root=session['root'], name=self._name(path), path=self._path(path), data=obj.show(), obj=obj)  #XXX deprecate data;  'this' can't be called 'self'
    
  @expose()
  def save(self, obj, path, data='', submit=None):    
    if 'file' in dir(data):  #allow file uploads, handled by the framework
      data = data.file.read()
    
    logging.getLogger('root.controller.http').debug("Wiki saving: %s %s", type(data), dir(data))
    obj.save(data)      

    flash("Changes saved!")
    redirectToShow(path)

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
      
      flash("Logged in as %s" % session['root'][-1])
      redirectToShow(['/'])

    msg=_("%s - Incorrect password or username." % username)
    response.status=403
    return dict(message=msg)

  @expose()
  def logout(self, obj,  path):
    del session['root']
    flash('Logged out')
    redirectToShow(['/'])

class PrimitivePresentation(WikiPresentation):
  @expose(template="reports.templates.show")
  def show(self, obj, path, prefix=None):
    content = html.escape("%s" % obj)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  

class RawPresentation(WikiPresentation):
  @expose(template="reports.templates.show")
  def show(self, obj, path, prefix=None):
    content = obj.show(formatted=True, prefix=None)
    return dict(session=session, root=session['root'], data=content, path=self._path(path), name=self._name(path), obj=obj)  
 
class Login(object):
  @expose(template="reports.templates.login")
  def login(self, page,  path, user=None, password=None, login=None):        
    assert False
    while True:
      if not user and not password:
        response.status=403
        return dict(message="Please log in.")
        
      username = user
      user = findPage([user])
      if not user or not user.data:
        break        
      user = user.data
      if 'checkPassword' not in dir(user):
        break
      if not user.checkPassword(page, password):
        break

      session['root'] = (request.headers['Host'], username,)
#      session['root'] = (username,)

      flash("Logged in as %s" % session['root'])
      redirectToShow(path)

    msg=_("%s - Incorrect password or username." % username)
    response.status=403
    return dict(message=msg)

  @expose()
  def logout(self, page,  path):
    del session['root']
    flash('Logged out')
    redirectToShow(path)

class Constructor(object):
  def __init__(self, class_=None):
    self.class_ = class_
    self.links = {}
  
  def show(self, page, prefix=None):
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

  wikiWords = re.compile(r'\[(\(?[^\ \[\]][^\[\]]*?\)?)\]')
  inlineWords = re.compile(r'\{(\(?[^\ \[\}][^\[\}]*?\)?)\}')   
  indentWords = re.compile(r'\s*\*')   
  
  def _wikiFormat(self, page, content, prefix=None):
    #  name = html.escape(name)
    if not prefix:
      prefix = tuple()

    def wikiLink(match):
      name = match.group(1)
      if name.startswith('(') and name.endswith(')'):
        return ''
      link = name[:-1] if name.endswith('*') else name
      link = '/'.join(prefix+(link,))
      return '<a href="http:%s/">%s</a>' % (link, name)
      
    def inlineLink(match):
      name = match.group(1)
      if name.startswith('(') and name.endswith(')'):
        return ''      
      
      extension = tuple(name.split('/'))

      meta = findPage(page, tuple(name.split('/')))
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
    
    lastIndent = None
    newContent = []
    for line in content.splitlines():
      matches = Wiki.indentWords.findall(line)
      if matches and len(matches[0]) != lastIndent:
        if lastIndent: 
          newContent.append('\n')
        lastIndent = len(matches[0])
      if not matches:
        lastIndent = None
      newContent.append(line)
    content = '\n'.join(newContent)        
    
    content = publish_parts(content, writer_name="html")['html_body']
    content = Wiki.inlineWords.sub(inlineLink, ''.join(content))
    content = Wiki.wikiWords.sub(wikiLink, ''.join(content))
    return content
    
  def show(self, page, formatted=False, prefix=None):
    if formatted:
      formatted = self._wikiFormat(page, self.data, prefix)
#      print formatted
      return formatted
    return self.data
          
  def save(self, page, data=''):    
    self.data, self.links = self.resolveWikiLinks(page, data)
    page.data = self
            
  def list(self, page):
    return self.links

  def resolveWikiLinks(self, page, content):
    knownIds = {}
    for link in self.links:
      knownIds[page.get(self.links[link]).id] = self.links[link]

    content = Wiki.wikiWords.split(content)
    text = content[::2]
    links = content[1::2]
    new = []
    nameMapping = {}
    for link in links:
      template = "[%s]"
      if link.startswith('(') and link.endswith(')'):
        template = "[(%s)]"
        link = link[1:-1]
      
      name = None
      if '=' in link:        
        name, link = link.split('=', 1)     
        if not link:  #[name=]
          new.append(template % name)
          continue
  
      if link.endswith('*'):
        new.append(template % link)
        continue
            
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
      
      
      while False:
        if path[0] == '':
          if len(path) > 1:
            path[0:1] = []
          else:
            path = []
        else:
          path = list(page.path) + path
        
  #      while '..' in path:
  #        index = path.index('..')
  #        path[index-1:index+1] = []
          
        if path and path[-1] == '':  # '/' goes to root, 'foo/bar/baz/' strips off the '/'
          path = path[:-1]
        
        name = name if name else path[-1] if path else 'home'
        
        meta = findPage(loginRoot(), path)				
  
      link = template % (name) 
      if not meta or not meta.id:
        if '/' in link:
          link = template % (link + '*')
        new.append(link)
        continue
      new.append(link)
      
      if meta.id in knownIds:
        nameMapping[name] = knownIds[meta.id]
      else:
        nameMapping[name] = meta.descriptor
      
    content[1::2] = new 
    return ''.join(content), nameMapping

  def resolve(self, page, name):
    return self.links.get(name, None)
    
  def link(self, page, name, id):
    logging.getLogger('root.controller.http').debug("Linking %s %s", name, id)
    if 'links' not in dir(self):
      self.links = {}
  
    self.links[name] = id
    page.data = self

class CapRoot(Wiki, Login):
  def resolve(self, page, name):
    if name == '~hand':  # I don't like this
      return session['hand']
    return self.links.get(name, None)
  
class User(Wiki, Login):
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
    if name == '~hand':  # I don't like this
      return session['hand']
    return super(User, self).resolve(page, name)

class Raw(object):
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
    
metaTypes = dict((name, eval(name)) for name in ('Wiki', 'User', 'Presentation', 'CapRoot', 'Raw', 'Constructor'))

#import cPickle as pickle
#pickle.dump([(o.name, o.data, o.id) for o in db.Object.select()], open('db.dump', 'w'))

#for name, data, id in pickle.load(open('db.dump')):
#  print name
#  db.Object(name=name, data=data, ident=id)


