from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from routes import *

STENCIL_FONT = QFont( QFont( 'Arial', 16 ) )
STENCIL_FONT.setBold( True )

class WallHold( QWidget ):
    def __init__( self, row, col, editable = False ):
        super().__init__()
        self.setFixedSize( QSize( 40, 40 ) )
        self.row = row
        self.col = col
        self.status = HoldStatus.UNUSED
        self.editable = editable

    def GetCoord( self ):
        return chr( 65 + self.col ) + str( self.row + 1 )
    
    def paintEvent( self, event ):
        p = QPainter( self )
        rect = event.rect()
        color = Qt.white
        if self.status == HoldStatus.START:
            color = Qt.green
        elif self.status == HoldStatus.REGULAR:
            color = Qt.blue
        elif self.status == HoldStatus.FINISH:
            color = Qt.red

        p.fillRect( rect, QBrush( color ) )
        pen = QPen( color )
        pen.setWidth( 0 )
        p.setPen( pen )
        p.drawRect( rect )

    def mouseReleaseEvent( self, e ):
        if self.editable:
            self.status = (self.status + 1) % HoldStatus.COUNT
            self.update()


class WallStencil( QWidget ):
    def __init__( self, text ):
        super().__init__()
        self.text = text
        self.setFixedSize( QSize( 40, 40 ) )

    def paintEvent(self, event):
        qp = QPainter( self )
        qp.setRenderHint( QPainter.Antialiasing )
        qp.setPen( Qt.black )
        qp.setFont( STENCIL_FONT )
        qp.drawText( event.rect(), Qt.AlignCenter, self.text )


class WallWidget( QWidget ):
    def __init__( self ):
        super().__init__()
        self.gridLayout = QGridLayout()
        self.setLayout( self.gridLayout )
        self.setSizePolicy( QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed )
        #self.setSpacing( 5 )

        # grid starts in upper left corner, but wall starts in lower left
        for row in range( 0, WALL_ROWS + 1 ):
            for col in range( 0, WALL_COLS + 1 ):
                wallRow = WALL_ROWS - row
                w = None
                if row > 0 and col == 0:
                    w = WallStencil( str( wallRow + 1 ) )
                elif row == 0 and col > 0:
                    w = WallStencil( chr( 65 + col - 1 ) )
                elif row > 0 and col > 0:
                    w = WallHold( wallRow, col - 1, False )
                
                if w != None:
                    self.gridLayout.addWidget( w, row, col )

    def SetEditable( self, isEditable ):
        for row in range( 0, WALL_ROWS ):
            for col in range( 0, WALL_COLS ):
                self.gridLayout.itemAtPosition( row + 1, col + 1 ).widget().editable = isEditable

    def DrawRoute( self, route ):
        for row in range( 0, WALL_ROWS ):
            for col in range( 0, WALL_COLS ):
                self.gridLayout.itemAtPosition( row + 1, col + 1 ).widget().status = HoldStatus.UNUSED
        for hold in route.holds:
            wallRow = WALL_ROWS - hold.row
            self.gridLayout.itemAtPosition( wallRow, hold.col + 1 ).widget().status = hold.status

    def GetCurrentlyDrawnHolds( self ):
        holds = []
        for row in range( 0, WALL_ROWS ):
            for col in range( 0, WALL_COLS ):
                w = self.gridLayout.itemAtPosition( row + 1, col + 1 ).widget()
                if w.status != HoldStatus.UNUSED:
                    holds.append( Hold( w.row, w.col, w.status ) )
        return holds