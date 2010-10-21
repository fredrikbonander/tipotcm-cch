'''
Created on Sep 9, 2010

@author: broken

For interactive console
import md5
from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty()
    password = db.StringProperty()
    premissionLevel = db.IntegerProperty()

m = md5.new()
m.update('admin')
user = User()
user.username = 'admin'
user.password = m.hexdigest()
user.premissionLevel = 3
    
db.put(user)


'''

from google.appengine.ext import db

class User(db.Model):
    '''
    Containing users for administator and edit pages
    '''
    username = db.StringProperty()
    password = db.StringProperty()
    premissionLevel = db.IntegerProperty()
    
    @property
    def itemId(self):
        return self.key().id()