from DataFactory import dbGeo, dbImageStore
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
import Settings

class AddUpdateSpot(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        if self.request.get('imagestore_key'):
            image = dbImageStore.ImageStore.get(self.request.get('imagestore_key'))
        else:
            image = dbImageStore.ImageStore()
            
        image.name = self.request.get('image_name')
        image.imageReferance = self.request.get('image_referance')
        
        upload_files =  self.get_uploads('image_file')
        
        if upload_files:
            image.imageUrl = images.get_serving_url(str(upload_files[0].key()))
        
        imageKey = db.put(image)
        
        saveSpot(description = self.request.get('spot_description'), imageList = imageKey.id(), lat = self.request.get('lng'), lng = self.request.get('lng'))
        
        #=======================================================================
        # for language in Settings.languages:
        #    description = self.request.get('image_description_' + language)
        #    if description:
        #        imageDescription = dbImageStore.ImageDescription.gql('WHERE imageEntry = :imageEntry AND lang = :lang', imageEntry = imageKey, lang = language).get()
        #        if imageDescription is None:
        #            imageDescription = dbImageStore.ImageDescription()
        #            imageDescription.imageEntry = imageKey
        #            imageDescription.lang = language
        #        
        #        imageDescription.description = description
        #        db.put(imageDescription)
        #=======================================================================
    
        self.redirect('/en-us/standardpage/')


def saveSpot(**kwargs):
    description = kwargs['description']
#    type = kwargs['type']
#    category = kwargs['category']
    imageList = kwargs['imageList']
    lat = kwargs['lat']
    lng = kwargs['lng']
    
    geo = dbGeo.Spots()
    geo.description = description
#    geo.type = '0'
#    geo.category = '0'
#    geo.imageList = '0'
    geo.lat = float(lat)
    geo.lng = float(lng)
    
    db.put(geo)
