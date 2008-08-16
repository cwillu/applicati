from __future__ import absolute_import

import thread
import cPickle as pickle
import sqlite3
import uuid
from Crypto.Hash import SHA256
import os
import subprocess

import re
import logging

import inspect

from . import builtins

actions = {}

def _assertId(id):  #XXX change to assert
  logging.getLogger('root.model.descriptors').debug("ASSERTING %s", id)
  if not isinstance(id, tuple): 
    assert len(str(id)) > 10 or id == '1' or id == (1, ), (id, type(id)) #XXX fix root id
    logging.getLogger('root.model.descriptors').warn("old-style descriptor in use: %s (%s)", id, type(id))
    return (id, )
  return id

def _modPermissions(source, cap):
  if cap[0] == 0:
    return source[0] if source else 0, set()
  
  mask = set(cap[0]) | set(cap[1])    
  if 'override' in cap[0]:
    return cap[1], mask
  if source == 0 or source[0] == 0:
    return set(['override']) | set(cap[1]) - set(cap[0]), mask
    
  return set(source[0]) - set(cap[0]) | set(cap[1]) , mask

def _digest(descriptor, salt, secret): 
  logging.getLogger('root.model.descriptors').debug("Creating digest: %s", descriptor)
  id = _assertId(descriptor)
  hash = SHA256.new(str(id[-1]) + str(salt) + str(secret)).hexdigest()
  logging.getLogger('root.model.descriptors').debug("Digest: %s", hash)
  return hash

def _sign(descriptor, secret):
  salt = uuid.uuid4()
  descriptor = _assertId(descriptor)
  digest = _digest(descriptor, salt, secret)
  return (descriptor, salt, digest)

def _checkSignature(signedDescriptor, secret):  
  descriptor, salt, digest = signedDescriptor
  logging.getLogger('root.model.descriptors').debug("Checking signature: %s", digest)
  trialDigest = _digest(descriptor, salt, secret)
  return trialDigest == digest

class PermissionError(Exception): 
  def __init__(self, *args, **kargs):
    self.flash = kargs.get('flash', None)
    Exception.__init__(self, *args)

def logger(func):
  name = func.__name__
  if name[0] == '_':
    return func
  
  def log(*args, **kargs):
    print ">", name, args, kargs 
    result = func(*args, **kargs)
    print "<", name, result
    return result    
  return log
  
def with_methods(obj, decorator):
  try:
    for name, method in inspect.getmembers(obj, inspect.ismethod):
      setattr(obj, name, decorator(method))
  except PermissionError:
    pass
  
def BaseComponent(rootFolder, componentPath=()):
  assert rootFolder, "No root folder supplied (%s)" % rootFolder
  
  try:
    componentSecret = eval(open(os.path.join(rootFolder, 'secret')).read())
  except IOError:
    componentSecret = uuid.uuid4()
    print >>open(os.path.join(rootFolder, 'secret'), 'w'), "uuid.%s" % `componentSecret`
    
  
  """        
  return Object(descriptor=id[0], path=path)

  def create(self, data=None, onReify=None, path=[]):
    return Object(data=data, onReify=onReify, path=path)

  return Object(descriptor=1)
  """
  
  class Object(object):
    def __init__(self, descriptor=None, data=None, onReify=None, sourceId=None, path=[], permissions=None):      
      assert not (descriptor and data), "Invalid state: descriptor and data specified"
      assert not (descriptor and onReify), "Invalid state: descriptor and onReify specified"
      assert permissions is not None
      self.path = path
      self.onReify = onReify
      self._descriptor = descriptor
      self._data = data
      
      if sourceId:
        perms = self._getPerms()        
        print "\033[1;31m" + str(perms) + "\033[0m"
        print "\033[1;31m" + str(sourceId) + "\033[0m"
        
        if sourceId not in perms:
          print "\033[1;31m" + 'new' + "\033[0m"
          perms[sourceId] = path, 0
          self._setPerms(perms)
          
        logging.getLogger('root.model').debug("Caps: %s", perms)
          
        capPermissions = perms[sourceId][1:]                 
        permissions = _modPermissions(permissions, capPermissions)        

      self.permissions = permissions
      
      if self._descriptor and not isinstance(self._descriptor, tuple):
        logging.getLogger('root.model').warn("Old style descriptor, updating in place (%s)" % self._descriptor)
        assert False, self._descriptor
        self._descriptor = (self._descriptor,)
      
      if self._descriptor and not (self._descriptor == (1,) or self._descriptor[0] == (1,)):
        assert not set(map(type, self._descriptor)) - set([str]), self._descriptor
        
      if self._descriptor == ((1, ), ):
        raise Exception(self._descriptor, descriptor)

      # with_methods(self, logger) #debugging aid

    def _connect(self, id=None):
      db = sqlite3.connect(self._filename('permissions.db', id=id))
      db.execute('create table if not exists perm(source unique, permissions)')
      return db

    def _query(self, op):
      logging.getLogger('root.model').debug("Effective Permissions: %s", self.permissions)
      if self.permissions == 0 or self.permissions[0] == 0:
        return True
      if op in self.permissions[0]:
        return True
      if 'override' in self.permissions[0]:
        return True
      return False
    def _check(self, op):      
      if not self._query(op):
        raise PermissionError(op, self.permissions)
        
    @property
    def name(self):
      if self.path:
        return self.path[-1]
      return self.id
          
    def getData(self):
      self._check('read')
      return self._getData()
    def _getData(self):    
      if self._data is not None:
        return self._data

      if not self._descriptor:
        return None
        
      try:
        return pickle.load(file( self._filename()))
      except IOError, err:
        if self.id in [1, (1,)] and err.errno == 2:
          logging.getLogger('root.model').error("Recreating root page!!")
          try: 
            os.makedirs(self._filename(''))
          except OSError, err:
            if err.errno is not 17:  #path already exists (which is an error for a recursive create why exactly?)
              print self._filename(''), self._filename()
              raise err            
          return None
        if err.errno == 2 and 'data' not in self._filename(): #file not found
          return None
        logging.getLogger('root.model').error("Error retrieving page %s, %s, %s", self.id, err.errno, dir(err))
        raise err  
    def write(self, obj):
      self._check('replace')
      self._setData(obj)
    def _selfGetData(self):
      self._check('cross')
      return self._getData()      
    def _selfSetData(self, obj):
      self._check('modify')
      self._setData(obj)      
    def _setData(self, obj):
      self._data = None
      if not self._descriptor:
        logging.getLogger('root.model').info("Saving new descriptor")
        self._descriptor = (str(uuid.uuid4()),)
        self.onReify and self.onReify(self)
        
      logging.getLogger('root.model').debug("Saving %s (%s)", self.name, self.id)

      folder, name = self._filename().rsplit('/', 1)
      folder =  folder

      logging.getLogger('root.model').debug("%s %s", folder, name)
      if not os.access(folder, os.F_OK):
        os.makedirs(folder)
      result = pickle.dump(obj, file( self._filename(), 'w'))  
    
      return result
     
    data = property(getData, _selfSetData)   
    
    def _filename(self, selector="data", id=None):              
      if id is None:
        id = self.id

      if isinstance(id, (basestring, int, uuid.UUID)):
        return os.path.join(rootFolder, str(id), selector)

      if isinstance(id, tuple):
        return os.path.join(rootFolder, str(id[0]), selector)

      assert not set(map(type, id)) - set([str]), ( id)      
      return os.path.join(rootFolder, *id)
    
    @property
    def id(self):
      return self._descriptor
          
    @property
    def descriptor(self):
      if not self.id:
        return None
      return _sign(componentPath + self.id, componentSecret)
              
    def getPerms(self):
      self._check('read')

      return self._getPerms()            

    def _getPerms(self):
      if not self._descriptor:
        raise PermissionError()
        assert False
        return {}
        
      try:                
        perms = pickle.load(file(self._filename('permissions')))
        print "Rewriting old permissions format"
        db = self._connect()
        db.executemany('replace into perm(source, permissions) values (?, ?)', ((k, pickle.dumps(perms[k])) for k in perms))
        print self._filename('permissions')
        os.rename(self._filename('permissions'), '%s~' % self._filename('permissions'))
        db.commit()
      except IOError, err:
        pass
      
      db = self._connect()    
      perms = dict((k, pickle.loads(str(v))) for k, v in db.execute('select source, permissions from perm'))
      return perms
      
    def setPerms(self, links):
      self._check('permissions')  
      self._setPerms(links)
      
    def _setPerms(self, links):
      if not self._descriptor:
        assert False, "Unimplemented, setting permissions on unreified object"

      db = self._connect()
      db.executemany('replace into perm(source, permissions) values (?, ?)', ((k, pickle.dumps(links[k])) for k in links))
      db.commit()

    def changePermission(self, link, permission, value):
      #XXX locking required, or a better reworking
      logging.getLogger('root.model').debug("Setting permission %s on %s to %s", permission, link, value)

      links = self.links
      permissions = links[link][1:]

      if permissions[0] == 0:
        links[link] = (links[link][0], [], [])
        permissions = links[link][1:]

      while permission in permissions[0]:
        permissions[0].remove(permission)
      while permission in permissions[1]:
        permissions[1].remove(permission)
      if value is not None:
        permissions[1 if value else 0].append(permission)

      logging.getLogger('root.model').debug("Resulting permissions:" % links)

      self.links = links
    links = property(getPerms, setPerms)   
    
    def __div__(self, name):
      '''syntax abuse :p  foo/'bar'/'baz' '''
      return self.get(self.resolve(name), name)
      
    def resolve(self, name):
      data = self._selfGetData()
      return data.resolve(self, name)

    def get(self, descriptor, segment=None, path=None):
#      self._check('read')   #XXX ideally would be 'traverse', but current resolving requires reading the actual object anyway
      assert isinstance(descriptor, tuple), descriptor    
      id = _assertId(descriptor[0])
      if id == ((1,),):
        id = (1,)
      
      if not path:
        path = self.path + [segment]
      
      if not _checkSignature(descriptor, componentSecret):
        for cut in reversed(range(len(id)-1)):
          trial = id[cut:]
          print "Trial:", trial
          segment = trial[0]
          
          metaComponent = self.get(segment)
          print metaComponent        
          ## get(None, segment) because I'm still on the fence about auto wrapping data objects with their meta object        
          component = metaComponent.data.get(None, componentPath + (segment,))          
          trialDescriptor = (trial[1:], ) + descriptor[1:]
          result = component.get(trialDescriptor, path=path)
          if result:
            return result
        else:
          logging.getLogger('root.model').warn("Invalid signature on %s", descriptor)
          raise PermissionError("Access")
      
      id = id[-1:] # signature checked out: it's ours, so strip off the component path

      return Object(descriptor=id, path=path, sourceId=self._descriptor[0], permissions=self.permissions)

    def create(self, data=None, onReify=None, path=[]):
      return Object(data=data, onReify=onReify, path=path, permissions=self.permissions)  
  
  
  return Object(descriptor=(1,), path=[], permissions=0)
  
class Component(object):
  def __init__(self, path):
    self.path = path
  
  def get(self, meta, componentPath):
    return BaseComponent(self.path, componentPath)

def createBase(baseDir, template='reports/webTemplate.xml'):
  import xml
  spec = xml.dom.minidom.parse(template)
  
  root = BaseComponent(baseDir)
  
  def walk(path):
    path = path.strip('/').split('/')
    if path == ['']:
      path = []
    
    node = root
    for segment in path:      
      node /= segment         
    return node
  
  def construct(spec, node):
    nodeType = spec.tagName
    if nodeType == 'Link':
      print 
      print spec.getAttribute('path')
      descriptor = walk(spec.getAttribute('path')).descriptor
      print descriptor
      return descriptor
    elif nodeType == 'Component':
      path = spec.getAttribute('file')
      node.data = Component(path)
      return node.descriptor
    elif nodeType == 'Reference':
      descriptor = eval(spec.getAttribute('descriptor')) #XXX
      component = walk(spec.getAttribute('component'))
      return ((component.descriptor,) + descriptor[0],) + descriptor[1:]
      

    node.data = builtins.metaTypes[nodeType]()
    content = ''    
    
    for detail in spec.childNodes:
      if detail.nodeType is not spec.ELEMENT_NODE:
        continue
      
      descriptor = construct(detail, node.create())
      name = detail.getAttribute('name')
      permissions = detail.getAttribute('permissions') if detail.hasAttribute('permissions') else None

      content += '[%s]\n' % name
      node.data.link(node, name, descriptor)      
    
    node.data.save(node, content)
    return node.descriptor     

  construct(spec.childNodes[0], root)
  return root   
  
def test():
  createBase('test.pickles')  
  
test()
