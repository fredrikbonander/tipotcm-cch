from DataFactory import dbGeo, dbImageStore
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
import Settings
import logging
import math
import Utils

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


def AddSpot(params):
    cl = params.get_all('checkbox-a')
    categoryList = []
    spotId = 0
    
    for l in cl:
        categoryList.append(str(l))
    
    if params.get('closeby-spots'):
        saveSpotDescription(description = params.get('spot_description'), userid = params.get('userid'), username = params.get('username'), mood = params.get('mood'), spotKey = params.get('closeby-spots'))
        spotId = db.Key(params.get('closeby-spots')).id()
    else:
        spotId = saveSpot(description = params.get('spot_description'), type = params.get("type"), lat = params.get('lat'), lng = params.get('lng'), mood = params.get('mood'), category = categoryList, userid = params.get('userid'), username = params.get('username'))
        
    #saveSpot(description = params.get('spot_description'), lat = params.get('lat'), lng = params.get('lng'), category = categoryList, username = params.get('username'))
    
    return { 'status' : 1, 'message' : 'Spot saved', 'spotId' : spotId }

def saveSpotDescription(**kwargs):
    spotKey = kwargs['spotKey']
    description = kwargs['description']
    mood = kwargs['mood']
    #===========================================================================
    # Add spot description
    #===========================================================================
    spotDescription = dbGeo.SpotsDescription()
    
    if 'username' in kwargs:
        spotDescription.username = kwargs['username']
    
    if 'userid' in kwargs:
        spotDescription.userid = kwargs['userid']
        
    spotDescription.description = description
    spotDescription.spotIdentity = str(spotKey)
    spotDescription.mood = int(mood)
    
    db.put(spotDescription)
    
def saveSpot(**kwargs):
    description = kwargs['description']
    type = kwargs['type']
    category = kwargs['category']
#    imageList = kwargs['imageList']
    lat = kwargs['lat']
    lng = kwargs['lng']
    mood = kwargs['mood']
    username = None
    userid = None
    
    if 'username' in kwargs:
        username = kwargs['username']
    
    if 'userid' in kwargs:
        userid = kwargs['userid']
    
    
    geo = dbGeo.Spots()
    geo.type = int(type)
    geo.category = category
#    geo.imageList = '0'
    if lat:
        geo.lat = float(lat)
        geo.lng = float(lng)
    
    spotKey = db.put(geo)
    
    saveSpotDescription(description = description, username = username, userid = userid, spotKey = spotKey, mood = mood)

    return spotKey.id()

def AddOrUpdate(params):
    category = None
    if params.get('category_id'):
        category = dbGeo.Categories.get_by_id(int(params.get('category_id')))
    if category is None:
        category = dbGeo.Categories()
        
    category.name = params.get('category_name')
    category.categoryId = params.get('category_str_id')
    
    db.put(category)
    
    return { 'status' : 1, 'message' : 'category updated.' }

def calulateDistance(p1, p2):
    R = 6371000 # Radius of the Earth in m
    dLat = (p2.lat - p1.lat) * math.pi / 180
    dLon = (p2.lng - p1.lng) * math.pi / 180
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(p1.lat * math.pi / 180) * math.cos(p2.lat * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c

    return math.floor(d)

def getCloseBySpots(lat, lng):
    spotList = []
    diff = 0.1
    rndPoint = Utils.dictObj() #Lab.randomSingelPoint(latBase = 59.1, latUpper = 59.4, lngBase = 17.4, lngUpper = 19.0)
    rndPoint.lat = float(lat)
    rndPoint.lng = float(lng)
    ## 59.1
    latNE = rndPoint['lat'] + diff
    lngNE = rndPoint['lng'] + diff
    
    latSW = rndPoint['lat'] - diff
    lngSW = rndPoint['lng'] - diff
    
    spots = dbGeo.Spots.all()
    
    for spot in spots:
        if spot.lat < latNE and spot.lat > latSW and spot.lng < lngNE  and spot.lng > lngSW:
            descriptions = dbGeo.SpotsDescription.gql('WHERE spotIdentity = :key', key = str(spot.key())).fetch(1000)
            dList = []
            for d in descriptions:
                dList.append({ 'username': d.username, 'description' : d.description, 'mood' : d.mood })
            
            spotList.append({ 'lat' : spot.lat, 'lng' : spot.lng, 'dList' : dList, 'distance' :str(calulateDistance(spot, rndPoint)) + 'm', 'key' : str(spot.key())})
            
    return spotList