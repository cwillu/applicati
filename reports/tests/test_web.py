import re
import time
from urllib2 import urlopen, HTTPError

from cherrypy import server, config
import cherrypy

from nose.tools import *  

host, port, address = None, None, None

def catch(exc, func, *args, **kargs):
  result = None
  try:
    result = func(*args, **kargs)    
  except exc, e:
    return e
  assert False, "Expected %s raised, but %s was returned" % (exc, result)
    

def setup():
  global host, port, address
  server.wait()
  
  host = config.get('server.socket_host') or '127.0.0.1'
  port = config.get('server.socket_port') or '80'  

  address = "http://%s:%s" % (host, port)

def test_simpleRequests():    
  assert "OK" == urlopen(address).msg 
  assert "OK" == urlopen(address + '/').msg 
  assert "OK" == urlopen(address + '/root/users/cwillu/Bugs').msg
  assert "OK" == urlopen(address + '/root/users/cwillu/Bugs/').msg

def test_signedRequests():
  name = '~test(abcdef)'
  signature = cherrypy.root._signPath(('protected', name))
  signed = '~test(abcdef-%s)' % signature 
  print signed
  assert "OK" == urlopen(address + '/%s/' % signed).msg
  assert "OK" == urlopen(address + '/%s/root' % signed).msg
  assert "OK" == urlopen(address + '/%s/root/' % signed).msg

def test_invalid():    
  assert_equal(404, catch(HTTPError, urlopen, address + '/test/nonexisting/').code)
  assert_equal(404, catch(HTTPError, urlopen, address + '/test/invalid/').code)
    
  assert_equal("OK", urlopen(address + '/?op=save;data=[root]+[test]+qwerty12345678').msg)
  assert "qwerty12345678" in urlopen(address + '/').read()
