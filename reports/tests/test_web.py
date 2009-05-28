from __future__ import absolute_import

import os
import re
import time
from urllib2 import urlopen, HTTPError

from cherrypy import server, config
import cherrypy

from nose.tools import *  

from reports import model
from reports import web

TEST_PICKLES = "test/pickles.test"
TEST_TEMPLATE = "test/testTemplate.xml"

host, port, address = None, None, None
originalBase = None

def catch(exc, func, *args, **kargs):
  result = None
  try:
    result = func(*args, **kargs)    
  except exc, e:
    return e
  assert False, "Expected %s raised, but %s was returned" % (exc, result)
    

def setup():
  global host, port, address, originalBase
  server.wait()
  
  originalBase = web.baseMeta
  web.baseMeta = model.createBase(TEST_PICKLES, TEST_TEMPLATE)/'web'
  
  host = config.get('server.socket_host') or '127.0.0.1'
  port = config.get('server.socket_port') or '80'  

  address = "http://%s:%s" % (host, port)

def teardown():
  web.baseMeta = originalBase
  os.system('rm -rf "%s"' % TEST_PICKLES)

def test_simpleRequests():    
  assert_equal("OK", urlopen(address).msg)
  assert_equal("OK", urlopen(address + '/').msg)

def test_signedRequests():
  name = '~test(abcdef)'
  signature = cherrypy.root._signPath(('protected', name))
  signed = '~test(abcdef-%s)' % signature 
  print signed
  assert_equal("OK", urlopen(address + '/%s/' % signed).msg)
  assert_equal("OK", urlopen(address + '/%s/root' % signed).msg)
  assert_equal("OK", urlopen(address + '/%s/root/' % signed).msg)

def test_invalid():    
  assert_equal(404, catch(HTTPError, urlopen, address + '/test/nonexisting/').code)  
    
  assert_equal("OK", urlopen(address + '/?op=save;data=[root]+[test]+qwerty12345678').msg)
  assert "qwerty12345678" in urlopen(address + '/').read()
  
def test_linkEarly():
  assert_equal((web.baseMeta/'root'/'early').id, (web.baseMeta/'root'/'late').id)
  
