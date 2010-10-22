'''
Created on Sep 9, 2010

@author: broken
'''
from DataFactory import dbPages
from DataFactory import dbPageModules
from PageService import PageTemplates
import PageService
import Settings
import Utils
from google.appengine.api import memcache
import PageHandler
import Geo

class GetHandler:
    def __init__(self, path, *args):
        args[0].path = '/' + path[0]
        args[0].lang = path[0].split('/')[0]
        self.pageRefresh = False
        # If pagerefresh is present in query with value "true", skip memcache and reload the page from datastore
        if args[1].getvalue('pagerefresh') == 'true':
            self.pageRefresh = True
        self.preparePage(*args)
        self.renderPage(*args)
        
    def preparePage(self, view, query):
        # Get all pages and order by sort index
        pages = dbPages.Pages.gql('ORDER BY sortIndex').fetch(1000)
        # Get all published page modules to be match agaisnt pages
        pageModules = dbPageModules.PageModules.gql('WHERE lang = :lang AND published = :published', lang = view.lang, published = True).fetch(100)
        # Set up memcacheid based on language
        memcacheid = "mainView_pageTree_%s" % (view.lang)
        pageTree = memcache.get(memcacheid)
        # If pageTree is not in memcache, build pageTree and store it in memcache
        if pageTree is None or self.pageRefresh:
            pageTree = PageService.build_tree(pages, pageModules = pageModules) 
            memcache.set(memcacheid, pageTree, Settings.memcacheTimeout)
        
        # Set currentPage to None as a precaution
        view.currentPage = None
        # Bind pageTree to view
        view.pageTree = pageTree
        
        #How to get pagecontainer items
        footerPageContainer = dbPages.Pages.get_by_key_name('footermenu')
        if footerPageContainer:
            footerPages = dbPages.Pages.gql('WHERE parentKey = :parentKey', parentKey = footerPageContainer.key()).fetch(100)
            view.footerTree = PageService.build_tree(footerPages, pageRoot = footerPageContainer, pageModules = pageModules)[0]
        # Bind pages to view
        view.pages = pages
        
    def renderPage(self, view, query):
        # If we are at root page in URL
        if view.path == '/' + view.lang + '/':
            view.currentPage = dbPages.Pages.gql('WHERE startpage = True').get()
            # We need at least one page as startpage
            if view.currentPage is None:
                raise ValueError('Missing startpage. Select a start page under tab "Page Settings"')
            # Get page modules associated with startpage
            pageModule = dbPageModules.PageModules.gql('WHERE pageKey = :pageKey AND lang = :lang', pageKey = view.currentPage.key(), lang = view.lang).get()
        else:
            # Get page modules associated with url path
            pageModule = dbPageModules.PageModules.gql('WHERE path = :path', path = view.path).get()
        # We need atleast one pageModule to display any page
        if pageModule is None:
            raise ValueError('Missing pageModule')
        else:
            # If no current page is set, set pageModules's page as currentpage
            if not view.currentPage: 
                view.currentPage = dbPages.Pages.get(pageModule.pageKey.key())

            # templateType is stored with entire class path, we only need the last name 
            pageTemplateType = view.currentPage.templateType.split('.')[-1]
            
            # Set up memcacheid based on language
            memcacheid = "mainView_pageTemplate_%s" % (view.path)
            pageTemplate = memcache.get(memcacheid)
            # If pageTemplate is not in memcache
            if pageTemplate is None or self.pageRefresh:
                # Find pageTemplate class
                pageTemplateClass = getattr(PageTemplates, pageTemplateType, None)
                #invoke class and store it in memcache
                pageTemplate = pageTemplateClass(page = view.currentPage, query = query)
                pageTemplate.ParseImageListWithDescriptions()
                memcache.set(memcacheid, pageTemplate, Settings.memcacheTimeout)
            
            # Bind pageTemplate to view
            view.pageTemplate = pageTemplate
            view.pageType = pageTemplateType
            view.pageModule = view.pageTemplate.pageModules[view.lang]
            view.pageContent = view.pageTemplate.pageData[view.lang]            
            
class PostHandler:
    def __init__(self, path, *args):
        self.pathList = Utils.parsePath(path[0])
        func = getattr(self, self.pathList[1])
        func(*args)
        
    def AddSpot(self, view, post):
        view.StatusMessage = Geo.AddSpot(post)
        view.redirect = '/en-us/thankspage/' + '?spotId=' + str(view.StatusMessage['spotId'])
        
    def SendContactEmail(self, view, post):
        view.StatusMessage = PageHandler.SendContactMail(post)
        view.redirect = post.headers['Referer'] + '?status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']  