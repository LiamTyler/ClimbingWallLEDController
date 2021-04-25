import enum

#WALL_ROWS = 18
#WALL_COLS = 11
WALL_ROWS=10
WALL_COLS=5

class HoldStatus( enum.IntEnum ):
    UNUSED = 0
    START = 1
    REGULAR = 2
    FINISH = 3
    
    COUNT = 4


class RouteStyle( enum.IntEnum ):
    NONE = 0
    JUGGY = 1
    CRIMPY = 2
    SLOPEY = 3
    DYNAMIC = 4
    COMPRESSION = 5

    COUNT = 6

def RouteStyleToString( style ):
    names = [ "NONE", "JUGGY", "CRIMPY", "SLOPEY", "DYNAMIC", "COMPRESSION" ]
    return names[int(style)]


class Hold:
    def __init__( self, row, col, status ):
        self.row = row
        self.col = col
        self.status = status

    # assumes wiring starts on A1 and goes up
    def GetLEDCoord( self ):
        coord = self.col * WALL_ROWS
        if self.col % 2 == 0:
            coord += self.row
        else:
            coord += WALL_ROWS - 1 - self.row
        return coord
    
    def GetStrCoord( self ):
        return chr( 65 + self.col ) + str( self.row + 1 )

    def __str__( self ):
        return self.GetStrCoord()

    def __repr__( self ):
        return self.__str__()


class Route:
    def __init__( self, name=None, difficulty=0, rating=0, style=RouteStyle.NONE, tags=None, notes=""):
      self.name = name
      self.difficulty = difficulty
      self.holds = []
      self.notes = notes
      self.rating = rating
      self.style = style
      self.tags = tags if tags != None else []

    def __str__( self ):
        s = self.name + ": V" + str( self.difficulty ) + "\n"
        s += "\tNotes: " + str( self.notes ) + "\n"
        
        startHolds = []
        regularHolds = []
        finishHolds = []
        for hold in self.holds:
            if hold.status == HoldStatus.START:
                startHolds.append( hold )
            elif hold.status == HoldStatus.REGULAR:
                regularHolds.append( hold )
            elif hold.status == HoldStatus.FINISH:
                finishHolds.append( hold )
        
        s += "\tHolds:\n"
        s += "\t\tStart: " + str( startHolds ) + "\n"
        s += "\t\tRegular: " + str( regularHolds ) + "\n"
        s += "\t\tFinish: " + str( finishHolds )

        return s
