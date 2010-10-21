'''
Created on Sep 9, 2010

@author: broken
'''
from google.appengine.ext import db
from DataFactory import dbPageModules

class ContentModules(db.Model):
    name = db.StringProperty()
    content = db.TextProperty()
    pageModuleKey = db.ReferenceProperty(dbPageModules.PageModules)
    
    @property
    def itemId(self):
        return self.key().id()