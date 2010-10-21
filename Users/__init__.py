from DataFactory import dbUser
from gaesessions import get_current_session

from google.appengine.ext import db
import md5

def doLogin(username, password):
    user = dbUser.User.gql('WHERE username = :username', username = username).get()
        
    if user is None:
        return { 'status' : -1, 'message' : 'The username or password you provided does not match our records.' }
    
    m = md5.new()
    m.update(password)
    ## Passwords in dbUser is stored as MD5
    passwordAsMD5 = m.hexdigest()
    
    ## Match passed password as MD5 with dbUser password
    if user.password != passwordAsMD5:
        return { 'status' : -1, 'message' : 'The username or password you provided does not match our records.' }
    
    session = get_current_session()
    session['user'] = { 'authenticated' : True, 'premissionLevel' : user.premissionLevel }
    # Let's try save a dict
    #session['user_premissionLevel'] = user.premissionLevel
    
    return { 'status' : 1, 'message' : 'User logged in' }

def doLogout():
    session = get_current_session()
    del session['user']
    #del session['user_premissionLevel']
    
    return { 'status' : 1, 'message' : 'User logged out' }

def isUserAuthenticated():
    session = get_current_session()
    if session and 'user' in session and session['user']['authenticated'] == True:
        return True
    else:
        return False

def hasPremission(view, lvl_required):
    session = get_current_session()
    
    if lvl_required <= session['user']['premissionLevel']:
        return True
    else:
        view.statusCode = '-1'
        view.statusMessage = 'You don\'t have access to this page!'
        view.templateFile = 'edit/noaccess.html'
        return False

def AddOrUpdate(params):
    user = None
    if params.get('user_id'):
        user = dbUser.User.get_by_id(int(params.get('user_id')))
    if user is None:
        user = dbUser.User()
        
    m = md5.new()
    m.update(params.get('password'))
    
    user.username = params.get('username')
    user.password = m.hexdigest()
    user.premissionLevel = int(params.get('premission_level'))
    
    db.put(user)
    
    return { 'status' : 1, 'message' : 'User updated.' }

def getCurrentUser():
    session = get_current_session()
    return session
  
def DeleteUser(params):
    user = dbUser.User.get_by_id(int(params.get('user_id')))
    
    if user.premissionLevel == 3:
        #Need to secure that at least on superuser remains
        superUsers = dbUser.User.gql('WHERE premissionLevel = 3').fetch(100)
        if len(superUsers) < 2:
            return { 'status' : -1, 'message' : 'Can\'t remove user. At least one superuser need to remain.' }
    
    db.delete(user)

    return { 'status' : 1, 'message' : 'User removed.' }