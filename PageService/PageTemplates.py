'''
Created on Sep 9, 2010

@author: broken
'''
from PageService import PageTypes
from DataFactory import dbPageModules, dbNewsFeed, dbContentModules, dbGeo
import Settings
import ImageStore
from google.appengine.api import blobstore
from PageService.PageTypes import parsePageData

class StandardPage(PageTypes.PageType):
    # Display name in EDIT/new page
    templateName = 'StandardPage'
    templateFile = 'pages/standardpage.html'
    
    def addModules(self):
        self.modules.append(PageTypes.getStandardHeading(self, 'MainHeading'))
        self.modules.append(PageTypes.getStandardTextBox(self, 'MainTextBox'))
        self.modules.append(PageTypes.getImageListModule(self, 'ImageList'))
        
    def ParseImageListWithDescriptions(self):
        self.uploadUrl = blobstore.create_upload_url('/action/addSpot')
        for lang in self.pageData:
            list = self.pageData[lang]
            if 'ImageList' in list:
                self.pageData[lang]['ImageList'] = ImageStore.GetImageListDescriptions(self.pageData[lang]['ImageList'], lang)
                
class StartPage(PageTypes.PageType):
    templateName = 'StartPage'
    templateFile = 'pages/startpage.html'
    
    def addModules(self):
        self.modules.append(PageTypes.getStandardHeading(self, 'MainHeading'))
        self.modules.append(PageTypes.getStandardHeading(self, 'SubHeading'))
        self.modules.append(PageTypes.getStandardTextBox(self, 'MainTextBox'))
        self.modules.append(PageTypes.getImageListModule(self, 'ImageList'))

    def ParseImageListWithDescriptions(self):
        for lang in self.pageData:
            list = self.pageData[lang]
            if 'ImageList' in list:
                self.pageData[lang]['ImageList'] = ImageStore.GetImageListDescriptions(self.pageData[lang]['ImageList'], lang)


class ReportPage(PageTypes.PageType):
    templateName = 'ReportPage'
    templateFile = 'pages/reportpage.html'
    
    def __init__(self, **kwargs):
        # Get page from kwargs
        page = kwargs['page']
        query = kwargs['query']
        # Set reference to page.key() 
        pageKey = page.key()
        # Get pageModules associated with page
        pageModuleList = dbPageModules.PageModules.gql('WHERE pageKey = :pageKey', pageKey = pageKey).fetch(1000)
        pageData = {}
        pageModules = {}
        # Set up pageModules dict with lang as keys
        for lang in Settings.languages:
            pageModules[lang] = {}
        
        for pageModule in pageModuleList:
            pageModules[pageModule.lang] = pageModule
            # All content data in store in dbContentModules.ContentModules and not in the pageModules them self
            # Get dbContentModules.ContentModules for pageModule
            pageData[pageModule.lang] = dbContentModules.ContentModules.gql('WHERE pageModuleKey = :pageModuleKey', pageModuleKey = pageModule.key()).fetch(100)
        
        if query.getvalue('spotType'):
            self.spotType = query.getvalue('spotType')
        
        # Store all data 
        self.pageModules = pageModules
        self.pageKey = pageKey
        self.pageData = parsePageData(pageData)
        self.categories = dbGeo.Categories.all()
        self.modules = []
        
    def addModules(self):
        self.modules.append(PageTypes.getStandardHeading(self, 'MainHeading'))
        self.modules.append(PageTypes.getStandardTextBox(self, 'MainTextBox'))
        
class ThanksPage(PageTypes.PageType):
    templateName = 'ThanksPage'
    templateFile = 'pages/thanks.html'
    
    def __init__(self, **kwargs):
        # Get page from kwargs
        page = kwargs['page']
        query = kwargs['query']
        # Set reference to page.key() 
        pageKey = page.key()
        # Get pageModules associated with page
        pageModuleList = dbPageModules.PageModules.gql('WHERE pageKey = :pageKey', pageKey = pageKey).fetch(1000)
        pageData = {}
        pageModules = {}
        # Set up pageModules dict with lang as keys
        for lang in Settings.languages:
            pageModules[lang] = {}
        
        for pageModule in pageModuleList:
            pageModules[pageModule.lang] = pageModule
            # All content data in store in dbContentModules.ContentModules and not in the pageModules them self
            # Get dbContentModules.ContentModules for pageModule
            pageData[pageModule.lang] = dbContentModules.ContentModules.gql('WHERE pageModuleKey = :pageModuleKey', pageModuleKey = pageModule.key()).fetch(100)
        
        spotId = query.getvalue('spotId')
        
        if spotId:
            spotData = dbGeo.Spots.get_by_id(int(spotId))
            category = dbGeo.Categories.get(spotData.category)
            spot = { 'category' : category, 'dList' : [] }
            
            descriptions = dbGeo.SpotsDescription.gql('WHERE spotIdentity = :key', key = str(spotData.key())).fetch(1000)
            for d in descriptions:
                spot['dList'].append({ 'userid': d.userid, 'username': d.username, 'description' : d.description, 'mood': d.mood, 'creationDate' : d.creationDate })
        
            self.spot = spot
        
        # Store all data 
        self.pageModules = pageModules
        self.pageKey = pageKey
        self.pageData = parsePageData(pageData)
        self.modules = []
        
    def addModules(self):
        self.modules.append(PageTypes.getStandardHeading(self, 'MainHeading'))
        self.modules.append(PageTypes.getStandardTextBox(self, 'MainTextBox'))

      
class NewsFeedPage(PageTypes.PageType):
    templateName = 'NewsFeedPage'
    templateFile = 'pages/newspage.html'
    
    def __init__(self, **kwargs):
        # Get page from kwargs
        page = kwargs['page']
        query = kwargs['query']
        # Set reference to page.key() 
        pageKey = page.key()
        # Get pageModules associated with page
        pageModuleList = dbPageModules.PageModules.gql('WHERE pageKey = :pageKey', pageKey = pageKey).fetch(1000)
        pageData = {}
        pageModules = {}
        # Set up pageModules dict with lang as keys
        for lang in Settings.languages:
            pageModules[lang] = {}
        
        for pageModule in pageModuleList:
            pageModules[pageModule.lang] = pageModule
            # All content data in store in dbContentModules.ContentModules and not in the pageModules them self
            # Get dbContentModules.ContentModules for pageModule
            newsFeed = dbNewsFeed.NewsFeed.gql('WHERE pageModuleKey = :pageModuleKey ORDER BY date DESC', pageModuleKey = pageModule.key()).fetch(100)
            pageData[pageModule.lang] = newsFeed
        
        if query.getvalue('newsId'):
            self.pageDataByQuery = dbNewsFeed.NewsFeed.get_by_id(int(query.getvalue('newsId')))
            
        # Store all data 
        self.pageModules = pageModules
        self.pageKey = pageKey
        self.pageData = pageData
        self.modules = []
    
    def addModules(self):
        self.modules = PageTypes.getNewsFeed(self, 'NewsFeedEntry')
                
class ImageGallery(PageTypes.PageType):
    templateName = 'ImageGallery'
    templateFile = 'pages/imagegallery.html'
    
    def addModules(self):
        self.modules.append(PageTypes.getStandardHeading(self, 'NextImage'))
        self.modules.append(PageTypes.getStandardHeading(self, 'PreviousImage'))
        self.modules.append(PageTypes.getStandardHeading(self, 'ImageText'))
        self.modules.append(PageTypes.getImageListModule(self, 'ImageList'))

    def ParseImageListWithDescriptions(self):
        for lang in self.pageData:
            list = self.pageData[lang]
            if 'ImageList' in list:
                self.pageData[lang]['ImageList'] = ImageStore.GetImageListDescriptions(self.pageData[lang]['ImageList'], lang)
            
        
class PageContainer(PageTypes.PageType):
    templateName = 'PageContainer'
    
    def __init__(self):
        pass