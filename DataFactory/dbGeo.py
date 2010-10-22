from google.appengine.ext import db

class Spots(db.Model):
    type = db.IntegerProperty()
    category = db.StringListProperty()
    imageList = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()

    @property
    def itemId(self):
        return self.key().id()

class SpotsDescription(db.Model):
    username = db.StringProperty()
    userid = db.StringProperty()
    description = db.StringProperty(multiline=True)
    spotIdentity = db.StringProperty()
    creationDate = db.DateTimeProperty(auto_now_add=True)
    mood = db.IntegerProperty()
    
class Categories(db.Model):
    name = db.StringProperty()
    categoryId = db.StringProperty()
    
    @property
    def itemId(self):
        return self.key().id()
