'''
Created on Sep 15, 2010

@author: broken
'''
from google.appengine.ext import db
from DataFactory import dbPageModules

class NewsFeed(db.Model):
    title = db.StringProperty()
    content = db.TextProperty()
    lang = db.StringProperty()
    date = db.DateProperty(auto_now_add=True)
    pageModuleKey = db.ReferenceProperty(dbPageModules.PageModules)
    
    @property
    def itemId(self):
        return self.key().id()