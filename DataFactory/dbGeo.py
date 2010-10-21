from google.appengine.ext import db

class Spots(db.Model):
    description = db.StringProperty()
    type = db.StringProperty()
    category = db.StringProperty()
    imageList = db.StringProperty()
    lat = db.FloatProperty()
    lng = db.FloatProperty()

    @property
    def itemId(self):
        return self.key().id()