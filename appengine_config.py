COOKIE_KEY = '24dc880a660eeac5c3f9a3021fc9b7fa'
from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
    #from google.appengine.ext.appstats import recording
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
    #app = recording.appstats_wsgi_middleware(app)
    return app