#!/usr/bin/env python

import sqlite3
import cPickle as pickle

db = sqlite3.connect('sqlite.test')
db.execute('create table if not exists perm(source unique, permissions)')

print dict((k, pickle.loads(str(v))) for k, v in db.execute('select * from perm'))
#for row in 
#  pass
#    print row[0], pickle.loads(str(row[1]))

#  db.execute('replace into perm(source, permissions) values (?, ?)', ('test', pickle.dumps(([1,2,3], [8,9,10]))))
#  db.commit()
