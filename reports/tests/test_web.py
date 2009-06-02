from __future__ import absolute_import

import os
import re
import time
from urllib2 import urlopen, HTTPError

#from cherrypy import server, config
#import cherrypy

from nose.tools import *  

from reports import model
#from reports import web

TEST_PICKLES = "test/pickles.test"
TEST_TEMPLATE = "test/testTemplate.xml"

base = None

def catch(exc, func, *args, **kargs):
  result = None
  try:
    result = func(*args, **kargs)    
  except exc, e:
    return e
  assert False, "Expected %s raised, but %s was returned" % (exc, result)
    
TEST_STRING = "5461adfasdcf546asdcf"

def setup():
  global base
  base = model.createBase(TEST_PICKLES, TEST_TEMPLATE)  

def teardown():
  os.system('rm -rf "%s"' % TEST_PICKLES)

def test_simple():
  assert_true(base.data.show())
  
  content = base/'content'
  assert_true(content)
  
  content.data.save(TEST_STRING)
  
  assert_equal(TEST_STRING, content.data.show())
  assert_equal(TEST_STRING, (base/'content').data.show())
  

def test_linkEarly():
  assert_equal((base/'early').id, (base/'late').id)
  assert_equal((base/'early').data.show(), (base/'late').data.show())

def test_magic():
  assert_equal(base.data.early.show(), base.data.late.show())
  base.data.newobject = 123
  
  assert_equal(123, base.data.newobject.__value__())
  
  assert_equal(123, (base/'newobject').data.__value__())
  
#def test_XXX_deficiencies():
#  base.data.Capitalization = 123
#  
#  assert_equal(123, base.data.capitalization)
#  assert_raises(KeyError, lambda: (base/'Capitalization').data)


#def test_simpleRequests():  
#  assert_equal("OK", urlopen(address).msg)
#  assert_equal("OK", urlopen(address + '/').msg)

#def test_signedRequests():
#  name = '~test(abcdef)'
#  signature = cherrypy.root._signPath(('protected', name))
#  signed = '~test(abcdef-%s)' % signature 
#  print signed
#  assert_equal("OK", urlopen(address + '/%s/' % signed).msg)
#  assert_equal("OK", urlopen(address + '/%s/root' % signed).msg)
#  assert_equal("OK", urlopen(address + '/%s/root/' % signed).msg)

#def test_invalid():    
#  assert_equal(404, catch(HTTPError, urlopen, address + '/test/nonexisting/').code)  
#    
#  assert_equal("OK", urlopen(address + '/?op=save;data=[root]+[test]+qwerty12345678').msg)
#  assert "qwerty12345678" in urlopen(address + '/').read()
  
  
  
