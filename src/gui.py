from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from routes import *

STENCIL_FONT = QFont( QFont( 'Arial', 16 ) )
STENCIL_FONT.setBold( True )

class WallHold( QWidget ):
    def __init__( self, row, col ):
        super().__init__()
        self.setFixedSize( QSize( 40, 40 ) )
        self.row = row
        self.col = col
        self.status = HoldStatus.UNUSED

    def GetCoord( self ):
        return chr( 64 + self.col ) + str( self.row )
    
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
        

class MainWindow(QMainWindow):
    def __init__( self ):
        super( MainWindow, self ).__init__()
        self.setStyleSheet( "background-color: lightGray;" )
        centralWidget = QWidget()
        self.setCentralWidget( centralWidget )
        verticalLayout = QVBoxLayout()
        centralWidget.setLayout( verticalLayout )
        
        self.grid = QGridLayout()
        self.grid.setSpacing( 5 )
        
        self.CreateRouteSetup()
        addRouteButton = QPushButton( self )
        addRouteButton.setText( "Add Route" )
        addRouteButton.setStyleSheet("background-color : white")
        addRouteButton.clicked.connect( self.AddRoute )
        
        verticalLayout.addLayout( self.grid )
        verticalLayout.addWidget( addRouteButton )

        self.show()

    def CreateRouteSetup( self ):
        # Add positions to the map
        for row in range( 0, WALL_ROWS + 1 ):
            for col in range( 0, WALL_COLS + 1 ):
                wallRow = 19 - row
                w = None
                if row > 0 and col == 0:
                    w = WallStencil( str( wallRow ) )
                elif row == 0 and col > 0:
                    w = WallStencil( chr( 65 + col - 1 ) )
                elif row > 0 and col > 0:
                    w = WallHold( wallRow, col )
                
                if w != None:
                    self.grid.addWidget( w, row, col )

    def AddRoute( self ):
        route = Route( "Test", 0 )
        for row in range( 1, WALL_ROWS + 1 ):
            for col in range( 1, WALL_COLS + 1 ):
                w = self.grid.itemAtPosition( row, col ).widget()
                if w.status != HoldStatus.UNUSED:
                    route.holds.append( Hold( w.row, w.col, w.status ) )

        print( route )

if __name__ == '__main__':
    app = QApplication( [] )
    window = MainWindow()
    app.exec_()
