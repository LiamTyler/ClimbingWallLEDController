import enum

WALL_ROWS = 18
WALL_COLS = 11

class HoldStatus( enum.IntEnum ):
    UNUSED = 0
    START = 1
    REGULAR = 2
    FINISH = 3
    
    COUNT = 4


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
        return chr( 64 + self.col ) + str( self.row )

    def __str__( self ):
        return self.GetStrCoord()

    def __repr__( self ):
        return self.__str__()


class Route:
    def __init__( self, name, difficulty = -1, holds = [], notes = "" ):
      self.name = name
      self.difficulty = difficulty
      self.holds = holds
      self.notes = notes

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
        
        s += "\tHolds: "
        s += "\t\tStart: " + str( startHolds ) + "\n"
        s += "\t\tRegular: " + str( regularHolds ) + "\n"
        s += "\t\tFinish: " + str( finishHolds ) + "\n"

        return s