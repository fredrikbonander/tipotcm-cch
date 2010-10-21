import os
from django.template import Library, Node, TemplateSyntaxError
from google.appengine.ext import webapp
import logging

register = webapp.template.create_template_register()

def PageTree(pages, currentPage):
    return  { 'pageTree' : pages, 'currentPage': currentPage }

path = os.path.join(os.path.dirname(__file__), '../templates/edit/pageTree.html')
register.inclusion_tag(path)(PageTree)

def SitePageTree(pages, currentPage):
    return  { 'pageTree' : pages, 'currentPage': currentPage }

path = os.path.join(os.path.dirname(__file__), '../templates/pages/modules/sitePageTree.html')
register.inclusion_tag(path)(SitePageTree)

def Module(module, language, loopCount):
    data = ''
        
    if module['data'].has_key(language):
        data = module['data'][language]
    return  { 'module' : module, 'data' : data, 'language' : language, 'loopCount' : loopCount }

path = os.path.join(os.path.dirname(__file__), '../templates/edit/modules/module.html')
register.inclusion_tag(path)(Module)

def ifIn(value, list):
    if value in list:
        return True
    else:
        return False
    
register.filter('ifIn', ifIn)