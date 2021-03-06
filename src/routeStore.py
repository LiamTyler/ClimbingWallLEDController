import base64, os, pickle

STORE_LOCATION = './routes.db'

g_routeStore = None

class RouteStore:
    def __init__( self , storeLocation=STORE_LOCATION ):
        self.fileLocation = storeLocation
        self.LoadRouteStore()

    def _UpdateRouteStore( self ):
        pickle.dump( self.routes, open( self.fileLocation, "wb" ) )

    def LoadRouteStore( self ):
        try:
            with open( self.fileLocation, "rb" ) as file:
                self.routes = pickle.load( file )
        except:
            self.routes = []
        self.routes = [] # for testing purposes right now

    def AddRoute( self, route ):
        names = list( map( lambda r: r.name, self.routes ) )
        if route.name in names:
            raise Exception( "Route name already exists" )
        else:
            self.routes.append( route )
            self._UpdateRouteStore()

    def DeleteRoute( self, route ):
        numRoutes = len( self.routes )
        for i in range( numRoutes ):
            if route.name == self.routes[i].name:
                self.routes = self.routes[0:i] + self.routes[i+1:]
                break

    # TODO: Cant change the name with this
    def UpdateRoute( self, route ):
        numRoutes = len( self.routes )
        for i in range( numRoutes ):
            if route.name == self.routes[i].name:
                self.routes[i] = route
                return
        raise Exception( "No route found with name '" + route.name + "'" )

    def GetRouteByName( self, name ):
        for route in self.routes:
            if route.name == name:
                return route
        return None

    def GetRoutesByDifficulty( self, difficulty ):
        return list( filter( lambda r: r.difficulty == difficulty, self.routes ) )

    def GetAllRoutes( self ):
        return self.routes