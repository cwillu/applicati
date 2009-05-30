#!/usr/bin/python
import pkg_resources
pkg_resources.require("TurboGears")

from turbogears import config, update_config, start_server
import cherrypy
cherrypy.lowercase_api = True
from os.path import *

import os, sys
import thread

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    update_config(configfile=sys.argv[1],
        modulename="reports.config")
elif exists(join(dirname(__file__), "setup.py")):
    update_config(configfile="dev.cfg",modulename="reports.config")
else:
    update_config(configfile="prod.cfg",modulename="reports.config")
config.update(dict(package="reports"))

from reports.web import Root

#if __name__ != "__main__":
#  gitPid = True
#  gitPid = os.fork()
#  if not gitPid:
#    exit = os.system('git add .')
#    if exit: sys.exit(1)
#    exit = os.system('git commit -a -m "$(date)"')
#    if exit: sys.exit(2)
#    sys.exit(0)

#  def checkGitStatus(pid):
#    import os #???
#    exit = os.waitpid(pid, 0)
#    if exit[1]:
#      print "\nCommit failed (%s)\n" % (exit,)
#      thread.interrupt_main()
#    
#  thread.start_new_thread(checkGitStatus, (gitPid,))

start_server(Root())

assert False, "got here"
