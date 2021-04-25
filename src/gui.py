from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from routes import *
from routeStore import *
from lights import *

STENCIL_FONT = QFont( QFont( 'Arial', 16 ) )
STENCIL_FONT.setBold( True )

WINDOW_SIZE = (600, 800)

routeStore = None

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
        

class RouteListItem( QListWidgetItem ):
    def __init__( self, route ):
        super().__init__()
        self.route = route
        showString = route.name + ": V" + str( route.difficulty ) + "\n    "
        if route.style != RouteStyle.NONE:
            showString += "Style: " + RouteStyleToString( route.style )
        showString += " Rating: " + str( route.rating ) + "/5" 
        self.setText( showString )
        self.setFont( STENCIL_FONT )


class MainWindow( QMainWindow ):
    def __init__( self ):
        super( MainWindow, self ).__init__()
        self.setWindowTitle( "Home Wall App" )
        self.resize( WINDOW_SIZE[0], WINDOW_SIZE[1] )
        self.setStyleSheet( "background-color: lightGray;" )
        self._centralWidget = QWidget()
        self.setCentralWidget( self._centralWidget )
        self._verticalLayout = QVBoxLayout()
        self._centralWidget.setLayout( self._verticalLayout )
        
        self.MainMenu()
        self.show()

    def _clearLayout( self ):
        for i in reversed( range( self._verticalLayout.count() ) ): 
            self._verticalLayout.itemAt( i ).widget().setParent( None )

    def ViewRoutePage( self, dispRoute ):
        print( dispRoute.route )
        LED_DisplayRoute( dispRoute.route )

    def MainMenu( self ):
        self._clearLayout()
        vlist = QListWidget( self )
        routes = routeStore.GetAllRoutes()
        for route in routes:
            vlist.addItem( RouteListItem( route ) )
        scrollBar = QScrollBar()
        vlist.setVerticalScrollBar( scrollBar )
        vlist.itemClicked.connect( self.ViewRoutePage )

        addRouteButton = QPushButton( self )
        addRouteButton.setText( "Add Route" )
        addRouteButton.setStyleSheet("background-color : white")
        addRouteButton.clicked.connect( self.AddRoutePage )
        self._verticalLayout.addWidget( vlist )
        self._verticalLayout.addWidget( addRouteButton )

    def AddRoutePage( self ):
        self._clearLayout()
        self.grid = QGridLayout()
        self.grid.setSpacing( 5 )

        # Add positions to the map
        for row in range( 0, WALL_ROWS + 1 ):
            for col in range( 0, WALL_COLS + 1 ):
                wallRow = WALL_ROWS + 1 - row
                w = None
                if row > 0 and col == 0:
                    w = WallStencil( str( wallRow ) )
                elif row == 0 and col > 0:
                    w = WallStencil( chr( 65 + col - 1 ) )
                elif row > 0 and col > 0:
                    w = WallHold( wallRow, col )
                
                if w != None:
                    self.grid.addWidget( w, row, col )
        
        addRouteButton = QPushButton( self )
        addRouteButton.setText( "Add Route" )
        addRouteButton.setStyleSheet( "background-color : white" )
        addRouteButton.clicked.connect( self.AddRoute )
        self._verticalLayout.addLayout( self.grid )
        self._verticalLayout.addWidget( addRouteButton )

    def AddRoute( self ):
        route = Route( "Test", 0 )
        for row in range( 1, WALL_ROWS + 1 ):
            for col in range( 1, WALL_COLS + 1 ):
                w = self.grid.itemAtPosition( row, col ).widget()
                if w.status != HoldStatus.UNUSED:
                    route.holds.append( Hold( w.row, w.col, w.status ) )

        routeStore.AddRoute( route )
        print( route )


# For ease of test route creation
def Hold_S( str ):
    return Hold( int( str[1:] ) - 1, ord( str[0] ) - 65, HoldStatus.START )

def Hold_R( str ):
    return Hold( int( str[1:] ) - 1, ord( str[0] ) - 65, HoldStatus.REGULAR )

def Hold_F( str ):
    return Hold( int( str[1:] ) - 1, ord( str[0] ) - 65, HoldStatus.FINISH )

if __name__ == '__main__':
    LED_InitializeController()
    routeStore = RouteStore()
    route1 = Route( "Route 1", 5, 4, RouteStyle.SLOPEY )
    route1.holds = [ Hold_S( "A1" ), Hold_S( "B3" ), Hold_R( "C6" ), Hold_R( "D7" ), Hold_F( "E9" ) ]
    route2 = Route( "Route 2", 3, 5, RouteStyle.CRIMPY )
    route2.holds = [ Hold_S( "A3" ), Hold_S( "B4" ), Hold_R( "B8" ), Hold_F( "C9" ) ]
    route3 = Route( "Route 3", 4, 2, RouteStyle.JUGGY )
    route3.holds = [ Hold_S( "E3" ), Hold_S( "D3" ), Hold_R( "D6" ), Hold_R( "C6" ), Hold_F( "B9" ) ]
    
    routeStore.AddRoute( route1 )
    routeStore.AddRoute( route2 )
    routeStore.AddRoute( route3 )
    app = QApplication( [] )
    window = MainWindow()
    app.exec_()
