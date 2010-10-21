#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os

from google.appengine.dist import use_library
import Geo

use_library('django', '1.1')

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from PageController import EditView
from PageController import MainView
from DataFactory import dbUser

import ImageStore
import Utils
import cgi
import md5

def render_template(file, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'templates', file)
    return template.render(path, template_vals)

class SetupHandler(webapp.RequestHandler):
    def get(self):
        users = dbUser.User.all()
        
        if users.count() > 0:
            self.response.out.write('Captain says no!')
        else:
            user = dbUser.User()
        
            m = md5.new()
            m.update('admin')
            
            user.username = 'admin'
            user.password = m.hexdigest()
            user.premissionLevel = 3
            
            db.put(user)
            
class EditHandler(webapp.RequestHandler):    
    def get(self, *path):
        view = Utils.dictObj()
        query = cgi.FieldStorage()
        EditView.GetHandler(path, view, query)
        
        self.response.out.write(render_template(view.templateFile, view))

    def post(self, *path):
        view = Utils.dictObj()
        
        EditView.PostHandler(path, view, self.request)
        
        self.redirect(view.redirect)

class MainHandler(webapp.RequestHandler):
    def get(self, *path):
        view = Utils.dictObj()
        query = cgi.FieldStorage()
        
        ## Set standard language
        if path[0] == '':
            self.redirect('/en-us/')
        else:    
            MainView.GetHandler(path, view, query)
            # Store entire path for share this
            view.fullPath = ''.join(('http://', self.request.headers['Host'], view.path))
            self.response.out.write(render_template(view.pageTemplate.templateFile, view))
    
    def head(self, *path):
        view = Utils.dictObj()
        query = cgi.FieldStorage()
        
        ## Set standard language
        if path[0] == '':
            self.redirect('/en-us/')
        else:    
            MainView.GetHandler(path, view, query)
            # Store entire path for share this
            view.fullPath = ''.join(('http://', self.request.headers['Host'], view.path))
            self.response.out.write(render_template(view.pageTemplate.templateFile, view))

    def post(self, *path):
        view = Utils.dictObj()
        
        MainView.PostHandler(path, view, self.request)
        
        self.redirect(view.redirect)

def main():
    application = webapp.WSGIApplication([('/edit/setup/', SetupHandler), 
                                          ('/edit/action/AddUpdateImageStore', ImageStore.AddUpdateImageStore),
                                          ('/action/addSpot', Geo.AddUpdateSpot),
                                          (r'/(?i)(Edit)/(.*)', EditHandler),
                                          (r'/(.*)', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

webapp.template.register_template_library('TemplateTags')


if __name__ == '__main__':
    main()
