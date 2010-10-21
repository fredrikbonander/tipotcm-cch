'''
Created on Sep 13, 2010

@author: broken
'''
from google.appengine.ext import db

class ImageStore(db.Model):
    name = db.StringProperty()
    imageUrl = db.StringProperty()
    imageReferance = db.StringProperty()
    
    @property
    def itemId(self):
        return self.key().id()

class ImageDescription(db.Model):
    lang = db.StringProperty()
    description = db.TextProperty()
    imageEntry = db.ReferenceProperty(ImageStore)
    
    @property
    def itemId(self):
        return self.key().id()