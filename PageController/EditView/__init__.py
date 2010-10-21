'''
Created on Sep 9, 2010

@author: broken
'''

from google.appengine.api import blobstore
from DataFactory import dbPages
from DataFactory import dbImageStore
from DataFactory import  dbUser
from PageService import PageTemplates
from PageService import Page
from PageService.PageTypes import PageType

import Users
import Utils
import PageService
import Settings
import ImageStore
import logging

class GetHandler:
    def __init__(self, path, *args):
        self.pathList = Utils.parsePath(path[1])
        
        args[0].statusCode = args[1].getvalue('status')
        args[0].statusMessage = args[1].getvalue('message')
        
        if not Users.isUserAuthenticated():
            if not args[1].getvalue('status'):
                args[0].statusCode = '-1'
                args[0].statusMessage = 'You don\' have access to this page'
            args[0].templateFile = 'edit/login.html'
        else:
            self.preparePage(*args)
            func = getattr(self, self.pathList[0])
            func(*args)
    
    def preparePage(self, view, query):
        pages = dbPages.Pages.gql('ORDER BY sortIndex').fetch(1000)
        view.currentUser = Users.getCurrentUser()
        view.currentPage = None
        
        view.pageTree = PageService.build_tree(pages)
        view.pages = pages
        view.settings = Settings

    def getPageData(self, view, query):
        if view.currentPage.templateType == 'PageService.PageTemplates.PageContainer':
            self.pathList[0] = 'pagecontainer'
        else:
            pageTemplateType = view.currentPage.templateType.split('.')[-1]
            pageTemplate = getattr(PageTemplates, pageTemplateType, None)
            
            view.pageTemplate = pageTemplate(page = view.currentPage, query = query)
            view.pageTemplate.addModules()
            view.imageList = dbImageStore.ImageStore.all()
    
    def main(self, view, query):
        view.templateTypes = Utils.getPageTemplates(PageTemplates, PageType)
        view.templateFile = 'edit/' + self.pathList[0] + '.html'
    
    def imageStore(self, view, query):
        if query.getvalue('imageId'):
            view.currentImage = dbImageStore.ImageStore.get_by_id(int(query.getvalue('imageId')))
            view.currentImageDescription = dbImageStore.ImageDescription.gql('WHERE imageEntry = :imageEntry', imageEntry = view.currentImage.key())
        
        view.uploadUrl = blobstore.create_upload_url('/edit/action/AddUpdateImageStore')
        view.imageList = dbImageStore.ImageStore.all()
        view.templateFile = 'edit/' + self.pathList[0] + '.html'
    
    def users(self, view, query):
        if Users.hasPremission(view, 3):
            if query.getvalue('userId'):
                view.currentUser = dbUser.User.get_by_id(int(query.getvalue('userId')))
       
            view.userList = dbUser.User.all()
            view.templateFile = 'edit/' + self.pathList[0] + '.html'
            
            
    def page(self, view, query):
        if query.getvalue('pageId'):
            view.currentPage = dbPages.Pages.get_by_id(int(query.getvalue('pageId')))
            self.getPageData(view, query)
        if query.getvalue('pageName'):
            view.currentPage = dbPages.Pages.get_by_key_name(query.getvalue('pageName'))
            self.getPageData(view, query)
            
        view.templateFile = 'edit/' + self.pathList[0] + '.html'
        
    def logout(self, view, query):
        Users.doLogout()
        
        view.statusCode = '1'
        view.statusMessage = 'User has been logged out.'
        view.templateFile = 'edit/login.html'
        
class PostHandler:
    def __init__(self, path, *args):
        self.pathList = Utils.parsePath(path[1])
        func = getattr(self, self.pathList[1])
        func(*args)        

    def login(self, view, post):
        view.StatusMessage = Users.doLogin(post.get('username'), post.get('password'))
        view.redirect = '/edit/?status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']
      
    def AddUpdatePage(self, view, post):
        view.StatusMessage = Page.AddOrUpdate(post)
        if view.StatusMessage['pageId'] == 'None':
            view.redirect = '/edit/page/?pageName=' + view.StatusMessage['pageName'] + '&status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']
        else:
            view.redirect = '/edit/page/?pageId=' + view.StatusMessage['pageId'] + '&status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']
            
    def AddUpdateContent(self, view, post):
        view.StatusMessage = Page.AddUpdateContent(post)
        view.redirect = '/edit/page/?pageId=' + view.StatusMessage['pageId'] + '&status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']
     
    def AddUpdatePageSettings(self, view, post):
        view.StatusMessage = Page.AddUpdatePageSettings(post)
        view.redirect = '/edit/page/?pageId=' + view.StatusMessage['pageId'] + '&status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']
    
    def AddOrUpdateUser(self, view, post):
        view.StatusMessage = Users.AddOrUpdate(post)
        view.redirect = '/edit/users/?status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']
    
    def DeleteUser(self, view, post):
        view.StatusMessage = Users.DeleteUser(post)
        view.redirect = '/edit/users/?status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']
   
    def DeleteImage(self, view, post):
        view.StatusMessage = ImageStore.DeleteImage(post) 
        view.redirect = '/edit/imageStore/?status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']   
        
    def DeletePage(self, view, post):
        view.StatusMessage = Page.DeletePage(post)
        
        if view.StatusMessage['pageId'] == '0':
            view.redirect = '/edit/?status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']
        else:
            view.redirect = '/edit/page/?pageId=' + view.StatusMessage['pageId'] + '&status=' + str(view.StatusMessage['status'])  + '&message=' + view.StatusMessage['message']