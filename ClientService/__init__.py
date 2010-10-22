from django.utils import simplejson as json
from google.appengine.ext import webapp
import Geo

class RPCHandler(webapp.RequestHandler):
    """ Allows the functions defined in the RPCMethods class to be RPCed."""
    def __init__(self):
        webapp.RequestHandler.__init__(self)
        self.methods = RPCMethods()

    def get(self):
        func = None

        action = self.request.get('action')
        if action:
            if action[0] == '_':
                self.error(403) # access denied
                return
            else:
                func = getattr(self.methods, action, None)

        if not func:
            self.error(404) # file not found
            return

        args = ()
        while True:
            key = 'arg%d' % len(args)
            val = self.request.get(key)
            if val:
                args += (json.loads(val),)
            else:
                break
        result = func(*args)
        self.response.out.write(json.dumps(result))

    def post(self):
        args = json.loads(self.request.body)
        func = 'request'
        args = args['request']['Commands']

        if func[0] == '_':
            self.error(403) # access denied
            return

        func = getattr(self.methods, func, None)
        if not func:
            self.error(404) # file not found
            return

        result = func(*args)
        self.response.out.write(json.dumps({ 'd': { 'ResponseStatus' : 200, 'ResponseData': result }}))

class RPCMethods:
    """ Defines the methods that can be RPCed.
    NOTE: Do not allow remote callers access to private/protected "_*" methods.
    """

    def Add(self, *args):
        # The JSON encoding may have encoded integers as strings.
        # Be sure to convert args to any mandatory type(s).
        ints = [int(arg) for arg in args]
        return sum(ints)

    def request(self, *args):
        #j = simplejson.loads(args[0])
        result = []
        for arg in args:
            func, jsonargs = arg['Name'], arg['Params']
            func = getattr(self, func, None)
            if not func:
                self.error(404) # file not found
                return
    
            result.append(func(*jsonargs))
            
        return result
    
    def GetCloseBySpots(self, *args):
        
        #spotList = []
        
        #=======================================================================
        # for spot in spots:
        #    spotList.append({ 'lat' : spot.lat, 'lng' : spot.lng })
        #=======================================================================
         
        return { 'CommandName': 'GetCloseBySpots', 'Value' : Geo.getCloseBySpots(args[0]['Value'], args[1]['Value']) }
    