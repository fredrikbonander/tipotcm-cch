from DataFactory import dbPages, dbNewsFeed
from DataFactory import dbContentModules
from DataFactory import dbPageModules
from google.appengine.ext import db
import Utils

def AddOrUpdate(params):
    if params.get('page_templateType') == 'PageService.PageTemplates.PageContainer':
        keyName = Utils.slugify(unicode(params.get('page_name')))
        page = dbPages.Pages(key_name=keyName)
        page.sortIndex = 1000
    else:
        keyName = ''
        page = dbPages.Pages()
        page.sortIndex = 10
        
    page.name = params.get('page_name')
    page.templateType = params.get('page_templateType')
    
    parentKey = None
        
    if params.get('page_parent') != '0' and params.get('page_templateType') != 'PageService.PageTemplates.PageContainer':
        parentKey = db.Key(params.get('page_parent'))
    
    page.parentKey = parentKey
    
    pageKey = db.put(page)
    
    return { 'status' : 1, 'message' : 'Page added/updated', 'pageId' : str(pageKey.id()), 'pageName' : keyName }

def GetPath(page, lang, path):
    if page.parentKey == None:
        return '/' + lang + '/' + path
    else:
        page = dbPages.Pages.get(page.parentKey.key())
        if page.templateType == 'PageService.PageTemplates.PageContainer':
            return '/' + lang + '/' + path
        
        pageModule = dbPageModules.PageModules.gql('WHERE published = True AND pageKey = :pageKey AND lang = :lang', pageKey = page.key(), lang = lang).get()
        
        if pageModule is None:
            return False
        
        return pageModule.path + path

def AddUpdateContent(params):
    args = params.arguments()
    #isModule = re.compile("^(module_)") 
    #isDynamicModuel = re.compile("^(dynamic_)") 
    pageKey = db.Key(params.get('pageKey'))
    pageModuleName = params.get('page_module_name')
    lang = params.get('lang')
        
    if params.get('publish') == "on":
        publish = True 
    else: 
        publish = False
    
    page = dbPages.Pages.get(pageKey)
    pageModule = dbPageModules.PageModules.gql('WHERE pageKey = :pageKey AND lang = :lang', pageKey = pageKey, lang = lang).get()
    
    if pageModule is None:
        pageModule = dbPageModules.PageModules() 
        pageModule.pageKey = pageKey
        pageModule.lang = lang
        
    pageModule.name = pageModuleName
    stringPath = Utils.slugify(unicode(pageModuleName)) + '/'
    path = GetPath(page, lang, stringPath)
    
    ## If path is False, parent page in GetPath method has not been saved.
    if not path:
        return { 'status' : -1, 'message' : 'Parent page is not published', 'pageId' : str(page.key().id()) }
    
    pageModule.path = path
    pageModule.published = publish
    
    pageModuleKey = db.put(pageModule)
        
    for arg in args:
        argList = arg.split('|')
        if len(argList) > 1:
            # Save only static modules
            if argList[1] == 'static' or argList[1] == 'imageList':
                contentModule = dbContentModules.ContentModules.gql('WHERE pageModuleKey = :pageModuleKey AND name = :name', pageModuleKey = pageModuleKey, name = argList[0]).get()
                
                if contentModule is None:
                    contentModule = dbContentModules.ContentModules()
                    contentModule.pageModuleKey = pageModuleKey
                    contentModule.name = argList[0]
                    
                contentModule.content = params.get(arg)
                    
                db.put(contentModule)
            elif argList[1] == 'newsfeed' and params.get(arg) != '':
                if params.get('news_id'):
                    newsFeedModule = dbNewsFeed.NewsFeed.get_by_id(int(params.get('news_id')))
                else:
                    newsFeedModule = dbNewsFeed.NewsFeed()
                    newsFeedModule.pageModuleKey = pageModuleKey
                    newsFeedModule.lang = lang

                newsFeedModule.title = params.get(arg)
                newsFeedModule.content = params.get('module_news_content')
                
                db.put(newsFeedModule)
            
    return { 'status' : 1, 'message' : 'Content added/updated', 'pageId' : str(page.key().id()) }

def AddUpdatePageSettings(params):
    if params.get('startpage') == "on":
        startpage = True 
    else: 
        startpage = False
    
    if startpage:
        pages = dbPages.Pages.all()
        for page in pages:
            page.startpage = False
            page.put()
        
    currentPage = dbPages.Pages.get_by_id(int(params.get('page_id')))
    currentPage.startpage = startpage
    currentPage.sortIndex = int(params.get('sort_index'))
    
    db.put(currentPage)
    
    if startpage:
        return { 'status' : 1, 'message' : 'Updated page settings.', 'pageId' : params.get('page_id') }
    else:
        return { 'status' : -1, 'message' : 'Remember to set a page as startpage', 'pageId' : params.get('page_id') }
    
def DeletePage(params):
    currentPage = dbPages.Pages.get_by_id(int(params.get('page_id')))
    childPages = dbPages.Pages.gql('WHERE parentKey = :parentKey', parentKey = currentPage.key()).fetch(100)
    
    if len(childPages) == 0:
        pageModules = dbPageModules.PageModules.gql('WHERE pageKey = :pageKey', pageKey = currentPage.key()).fetch(100)
        
        for pageModule in pageModules:
            contentModules = dbContentModules.ContentModules.gql('WHERE pageModuleKey = :pageModuleKey', pageModuleKey = pageModule.key()).fetch(100)
            db.delete(contentModules)
        
        db.delete(pageModules)
        db.delete(currentPage)
        return { 'status' : 1, 'message' : 'Page deleted', 'pageId' : '0' }
    else:
        return { 'status' : -1, 'message' : 'Page has child pages, delete these first', 'pageId' : params.get('page_id') }
    
