'''
Created on Sep 9, 2010

@author: broken
'''
from google.appengine.ext import db

class Pages(db.Model):
    '''
    classdocs
    '''
    name = db.StringProperty()
    templateType = db.StringProperty()
    startpage = db.BooleanProperty()
    sortIndex = db.IntegerProperty()
    parentKey = db.SelfReferenceProperty()
    
    @property
    def itemId(self):
        return self.key().id()