import base64, os, pickle

STORE_LOCATION = './routes.db'

class RouteStore:
    def __init__( self , storeLocation=STORE_LOCATION ):
        self.fileLocation = storeLocation
        self.LoadRouteStore()

    def UpdateRouteStore( self ):
        pickle.dump( self.routes, open( self.fileLocation, 'wb' ) )

    def LoadRouteStore( self ):
        if os.path.isfile(self.fileLocation):
            self.routes = pickle.load( open( self.fileLocation, 'rb') )
        else:
            self.routes = []

    def AddRoute( self, route ):
        names = list( map( lambda r: r.name, self.routes ) )
        if route.name in names:
            raise Exception( 'Route name already exists' )
        else:
            self.routes.append( route )
            self.UpdateRouteStore()

    def GetRouteByName( self, name ):
        for route in self.routes:
            if route.name == name:
                return route
        return None

    def GetRoutesByDifficulty( self, difficulty ):
        return list( filter( lambda r: r.difficulty == difficulty, self.routes ) )
