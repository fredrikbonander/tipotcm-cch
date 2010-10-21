'''
Created on Sep 9, 2010

@author: broken
'''
from PageService import PageTypes
from DataFactory import dbPageModules, dbNewsFeed
import Settings
import ImageStore
from google.appengine.api import blobstore

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