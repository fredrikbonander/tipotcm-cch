'''
Created on Sep 9, 2010

@author: broken
'''
from DataFactory import dbPageModules
from DataFactory import dbImageStore
from DataFactory import dbContentModules
import Settings
# Parse page data so it can be reached in django templates based on name
def parsePageData(data):
    dataAsDict = {}
    if data:
        # Split data between lang dicts
        for lang in data:
            dataAsDict[lang] = {}
            for entry in data[lang]:
                # If entry is a ImageList slit content (containing ids) and get them from the datastore 
                if entry.name == 'ImageList':
                    ids = entry.content.split(',')
                    # Check if any ids is present
                    if len(ids) > 0 and ids[0] != '':
                        # Generator contains failsafe for entry.contents looking like "1,2,"
                        dataAsDict[lang][entry.name] = dbImageStore.ImageStore.get_by_id([int(id) for id in ids if id != ''])
                    else:
                        dataAsDict[lang][entry.name] = ''
                elif entry.content is None:
                    dataAsDict[lang][entry.name] = ''
                else:
                    dataAsDict[lang][entry.name] = entry.content
                    
    return dataAsDict

class PageType():
    def __init__(self, **kwargs):
        # Get page from kwargs
        page = kwargs['page']
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
        
        # Store all data 
        self.pageModules = pageModules
        self.pageKey = pageKey
        self.pageData = parsePageData(pageData)
        self.modules = []
    
    def addModules(self):
        pass
    
    def ParseImageListWithDescriptions(self):
        pass
    
    def renderEditPage(self):
        self.addModules()
    
def getStandardHeading(template, name):
    templateData = {}
    for lang in template.pageData:
        if name in template.pageData[lang]:
            templateData[lang] = template.pageData[lang][name]
        
    return { 'name' : name, 'type' : 'static', 'file' : 'modules/module_heading.html', 'data' : templateData }

def getStandardTextBox(template, name):
    templateData = {}
    for lang in template.pageData:
        if name in template.pageData[lang]:
            templateData[lang] = template.pageData[lang][name]
        
    return { 'name' : name, 'type' : 'static', 'file' : 'modules/module_textbox.html', 'data' : templateData }

def getNewsFeed(template, name):
    templateData = {}
    for lang in template.pageData:
        templateData[lang] = template.pageData[lang]
        
    return { 'name' : name, 'type' : 'newsfeed', 'file' : 'modules/module_newsfeed.html', 'data' : templateData }

def getImageListModule(template, name):
    templateData = {}
    imageList = dbImageStore.ImageStore.all() 
    for lang in template.pageData:
        if name in template.pageData[lang]:
            templateData[lang] = template.pageData[lang][name]
        
    return { 'name' : name, 'type' : 'imageList', 'file' : 'modules/module_imagelist.html', 'data' : templateData, 'imageList' : imageList }