from turbogears.database import PackageHub
hub = PackageHub('reports')
__connection__ = hub

import thread
import cPickle as pickle
import uuid
from Crypto.Hash import SHA256
import os
import subprocess

import weakref
import re
import logging

actions = {}
#actions = weakref.WeakValueDictionary()
#actionCollections = weakref.WeakKeyDictionary()

def _assertId(id):  #XXX change to assert
  logging.getLogger('root.model.descriptors').info("ASSERTING %s", id)
#  if not isinstance(id, tuple) or id == (1, ): 
  if id == (1, ):
    id = (id, )
  if not isinstance(id, tuple): 
    assert len(str(id)) > 10 or id == '1' or id == (1, ), (id, type(id)) #XXX fix root id
#    assert False, "WARNING: old-style descriptor in use: %s (%s)" % (id, type(id))
    logging.getLogger('root.model.descriptors').warn("old-style descriptor in use: %s (%s)", id, type(id))
    return (id, )
  return id

def resolveComponent(name):
  if name == "Object":
    return Object
    
  assert False, "Unknown component (%s)" % name


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
  digest = _digest(descriptor, salt, secret)
  return (descriptor, salt, digest)

def _checkSignature(signedDescriptor, secret):  
  descriptor, salt, digest = signedDescriptor
  trialDigest = _digest(descriptor, salt, secret)
  logging.getLogger('root.model.descriptors').debug("Checking signature: %s", digest)
  return trialDigest == digest

class PermissionError(Exception): pass

def BaseComponent():
  componentSecret = uuid.UUID("01ec9bf6-78ad-4996-912a-6b673992f877")
  
  """        
  return Object(descriptor=id[0], path=path)

  def create(self, data=None, onReify=None, path=[]):
    return Object(data=data, onReify=onReify, path=path)

  return Object(descriptor=1)
  """
  
  class Object(object):
    def __init__(self, descriptor=None, data=None, onReify=None, path=[], permissions=None):
      assert not (descriptor and data), "Invalid state: descriptor and data specified"
#      assert descriptor or data, "Invalid state: neither descriptor nor data specified"
      assert not (descriptor and onReify), "Invalid state: descriptor and onReify specified"
      assert permissions is not None
      self.path = path
      self.onReify = onReify
      self._descriptor = descriptor
      self._data = data
      self.permissions = permissions

      if self._descriptor and not (self._descriptor == (1,) or self._descriptor[0] == (1,)):
        assert not set(map(type, self._descriptor)) - set([str]), self._descriptor

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

    def watch(self, func):      
      possible = set()
      actionList = actions.setdefault(self._descriptor, possible)
      actionList.add(func)
#      actionCollections[func] = actionList
      logging.getLogger('root.model.watches').debug("Outstanding watches: %s", len(actionList))

    def removeWatch(self, func):
      actionList = actions.get(self._descriptor, set())
      actionList.discard(func)
      if not actionList:
        del actions[self._descriptor]
      
    def _fireWatchEvent(self):
      logging.getLogger('root.model.watches').debug("Firing watch event (%s outstanding)", len(actions))
      actionList = actions.get(self._descriptor, set())      
      for action in actionList:
        logging.getLogger('root.model.watches').debug("Firing %s", action)
        action()
        
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
        return pickle.load(file('pickles/%s' % self._filename()))
      except IOError, err:
        if self.id == 1 and err.errno == 2:
          logging.getLogger('root.model').error("Recreating root page!!")
          return None
        if err.errno == 2 and 'data' not in self._filename(): #file not found
          return None
        logging.getLogger('root.model').error("Error retrieving page %s, %s", err.errno, dir(err))
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
        self._descriptor = str(uuid.uuid4())
        self.onReify and self.onReify(self)
      logging.getLogger('root.model').debug("Saving %s (%s)", self.name, self.id)

      folder, name = self._filename().rsplit('/', 1)
      folder = 'pickles/%s' % folder

      logging.getLogger('root.model').debug("%s %s", folder, name)
      if not os.access(folder, os.F_OK):
        os.makedirs(folder)
      result = pickle.dump(obj, file('pickles/%s' % self._filename(), 'w'))  
    
      thread.start_new_thread(self._fireWatchEvent, tuple())
      return result
     
    data = property(getData, _selfSetData)   
    
    def _filename(self, selector="data", id=None):
      if id is None:
        id = self.id

      if isinstance(id, (basestring, int, uuid.UUID)):
        return '%s/%s' % (id, selector)


      if id == (1,):
        return "1/%s" % selector

      if id[0] == (1,):
        id = ('1', ) + id[1:]        

      assert not set(map(type, id)) - set([str]), ( id)      
      return '/'.join(id)
    
    @property
    def id(self):
      return self._descriptor
    
    @property
    def descriptor(self):
      return _sign(self.id, componentSecret)
              
    def getPerms(self):
#      self._check('permissions')
            
      if not self._descriptor:
#        assert False
        return {}
#      if self._data is not None:
#        return self._data
        
      try:
        perms = pickle.load(file('pickles/%s' % self._filename('permissions')))
        assert perms
        return perms
      except IOError, err:
        raise err
        assert False      
        return {}
      
    def setPerms(self, links):
      self._check('permissions')  
      if not self._descriptor:
        assert False, "Unimplemented, setting permissions on unreified object"
#        print "create"
#        self._descriptor = str(uuid.uuid4())
#        self.onReify and self.onReify(self)
        
      return pickle.dump(links, file('pickles/%s' % self._filename('permissions'), 'w'))        

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
      
    def resolve(self, name):
      data = self._selfGetData()
#      if not data:  
#        return None
      return data.resolve(self, name)

#    @classmethod
    def get(self, descriptor, segment=None, path=None):
#      self._check('read')   #XXX ideally would be 'traverse', but current resolving requires reading the actual object anyway
      assert isinstance(descriptor, tuple), descriptor    
#      id = _assertId(descriptor[0])
      id = descriptor[0]
      
      if not path:
        path = self.path + [segment]
      
      if len(id) > 1:
        segment = id[0]
        component = resolveComponent(segment)
        descriptor = (id[1:], ) + descriptor[1:]
        return component.get(descriptor, path=path)

      if not _checkSignature(descriptor, componentSecret):
        logging.getLogger('root.model').warn("Invalid signature on %s", descriptor)
        return False                
    
      capId = str(descriptor[1])  #XXX salt            

      if os.access('pickles/%s' % (self._filename('permissions', id[0])), os.F_OK):
        perms = pickle.load(file('pickles/%s' % (self._filename('permissions', id[0]))))
      else:
        perms = {}

      if capId not in perms:
#        assert False
        perms[capId] = path, 0
        pickle.dump(perms, file('pickles/%s' % (self._filename('permissions', id[0])), 'w'))
      
      logging.getLogger('root.model').debug("Caps: %s", perms)
        
      capPermissions = perms[capId][1:]
      
#      capNode = Object(descriptor= _assertId(id[0]) + (capId, ), path=[], permissions=0, data=0)
#      capPermissions = capNode.data
#      if capPermissions is None:
#        capNode.data = 0
#        capPermissions = 0
        
      targetPermissions = _modPermissions(self.permissions, capPermissions)

      return Object(descriptor=id[0], path=path, permissions=targetPermissions)

    def create(self, data=None, onReify=None, path=[]):
      return Object(data=data, onReify=onReify, path=path, permissions=self.permissions)

  return Object(descriptor="1", path=[], permissions=0)
  
      

