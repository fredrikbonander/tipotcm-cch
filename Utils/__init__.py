import inspect
from unicodedata import normalize
from re import sub

class dictObj(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

def parsePath(path):
    pathList = path.split('/')
    
    if pathList[-1] == '':
        pathList.pop()
   
    if len(pathList) == 0:
        pathList = ['main']
    
    return pathList

def getPageTemplates(module, clazz):
    return [ cls for name, cls in inspect.getmembers(module) if inspect.isclass(cls) and issubclass(cls, clazz) and cls is not clazz ]

def slugify(title):
    name = normalize('NFKD', title).encode('ascii', 'ignore').replace(' ', '-').lower()
    #remove `other` characters
    name = sub('[^a-zA-Z0-9_-]', '', name)
    #nomalize dashes
    name = sub('-+', '-', name)
    
    return name
