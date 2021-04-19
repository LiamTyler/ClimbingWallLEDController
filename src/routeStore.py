import base64, os, pickle, sqlite3

STORE_LOCATION = './routes.db'

class RouteStore:
    def __init__( self , storeLocation=STORE_LOCATION):
        # Check if DB exists yet
        isNew = not os.path.isfile( storeLocation )
        self.con = sqlite3.connect( storeLocation )
        
        # Create tables if the DB is new
        if isNew:
            # Right now enforcing name as a primary key, but we could change this
            self.con.cursor().execute( 'CREATE TABLE route (name TEXT PRIMARY KEY,  difficulty INTEGER, serialized TEXT)' )
            self.con.commit()

    def SerializeRoute( self, route ):
        # Pickle the object
        serialized = pickle.dumps( route )
        # Then return the base64-encoded string
        return base64.b64encode( serialized ).decode()

    def DeserializeRoute( self, route ):
        # Base64-decode bytes
        serialized = base64.b64decode( route.encode() )
        return pickle.loads( serialized )

    def AddRoute( self, route ):
        serialized = self.SerializeRoute( route )
        self.con.cursor().execute( 'INSERT INTO route VALUES(?,?,?)', (route.name, route.difficulty, serialized) )
        self.con.commit()

    def GetRouteByName( self, name ):
        cur = self.con.cursor()
        cur.execute( 'SELECT serialized FROM route WHERE name=?', (name,) )
        route = cur.fetchone()[0]
        return self.DeserializeRoute( route )

    def GetRoutesByDifficulty( self, difficulty ):
        cur = self.con.cursor()
        cur.execute( 'SELECT serialized FROM route WHERE difficulty=?', (difficulty,) )
        routes = cur.fetchall()
        return list( map( lambda r: self.DeserializeRoute( r[0] ), routes ) )
