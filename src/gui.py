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
        showString = route.name + ": V" + str( route.difficulty ) + "\n    "
        if route.style != RouteStyle.NONE:
            showString += "Style: " + RouteStyleToString( route.style )
        showString += " Rating: " + str( route.rating ) + "/5" 
        self.setText( showString )
        self.setFont( STENCIL_FONT )

class CustomDialog(QDialog):
    def __init__(self, title, msg, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle( title )
        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox( QBtn )
        self.buttonBox.accepted.connect( self.accept )

        self.layout = QVBoxLayout()
        message = QLabel( msg )
        self.layout.addWidget( message )
        self.layout.addWidget( self.buttonBox )
        self.setLayout( self.layout )

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

    def _clearLayout( self, layout):
        for i in reversed( range( layout.count() ) ): 
            item = layout.itemAt( i )
            widget = item.widget()
            if widget:
                widget.setParent( None )
            else:
                self._clearLayout( item.layout() )

    def ViewRoutePage( self, dispRoute ):
        print( dispRoute.route )
        LED_DisplayRoute( dispRoute.route )

    def MainMenu( self ):
        self._clearLayout( self._verticalLayout )
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
        addRouteButton.clicked.connect( lambda: self.AddRoutePage() )
        self._verticalLayout.addWidget( vlist )
        self._verticalLayout.addWidget( addRouteButton )

    def AddRoutePage( self, route=None ):
        route = route if route != None else Route()
        self._clearLayout( self._verticalLayout )
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
                    for hold in route.holds:
                        if ( WALL_ROWS - hold.row + 1 ) == row and hold.col == col:
                            w.status = hold.status
                if w != None:
                    self.grid.addWidget( w, row, col )
        
        addRouteButton = QPushButton( self )
        addRouteButton.setText( "Continue" )
        addRouteButton.setStyleSheet( "background-color : white" )
        addRouteButton.clicked.connect( lambda: self.AddRoute( route ) )

        backButton = QPushButton ( self )
        backButton.setText( "Back" )
        backButton.setStyleSheet( "background-color : white" )
        backButton.clicked.connect( self.MainMenu )

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget( backButton )
        buttonLayout.addWidget( addRouteButton )
        self._verticalLayout.addLayout( self.grid )
        self._verticalLayout.addLayout( buttonLayout )

    def AddRoute( self, route ):
        for row in range( 1, WALL_ROWS + 1 ):
            for col in range( 1, WALL_COLS + 1 ):
                w = self.grid.itemAtPosition( row, col ).widget()
                if w.status != HoldStatus.UNUSED:
                    route.holds.append( Hold( w.row, w.col, w.status ) )

        self.AddRoutePageTwo( route )

    def AddRoutePageTwo( self, route ):
        self._clearLayout( self._verticalLayout )
        vlist = QListWidget( self )

        formLayout = QFormLayout()
        self.routeNameInput = QLineEdit( route.name )
        formLayout.addRow( QLabel( "Route Name:" ), self.routeNameInput )
        self.routeDifficultyInput = QComboBox()
        self.routeDifficultyInput.addItems( [ str( i ) for i in range( 11 ) ] )
        self.routeDifficultyInput.setCurrentText( str( route.difficulty ) )
        formLayout.addRow( QLabel( "Difficulty:" ), self.routeDifficultyInput )
        self.routeStyleInput = QComboBox()
        self.routeStyleInput.addItems( list( map( lambda rs: rs.name, RouteStyle ) ) )
        self.routeStyleInput.setCurrentText( route.style.name )
        formLayout.addRow( QLabel( "Route Style:" ), self.routeStyleInput )
        self.routeRatingInput = QComboBox()
        self.routeRatingInput.addItems( [ str( i ) for i in range( 6 ) ] )
        self.routeRatingInput.setCurrentText( str( route.rating ) )
        formLayout.addRow( QLabel( "Rating:" ), self.routeRatingInput )
        self.routeNotesInput = QLineEdit( route.notes )
        formLayout.addRow( QLabel( "Notes:" ), self.routeNotesInput )
        self.routeTagsInput = QLineEdit( ", ".join( route.tags ) )
        formLayout.addRow( QLabel( "Tags (Comma-Separated):" ), self.routeTagsInput )
        self._verticalLayout.addLayout( formLayout )

        buttonLayout = QHBoxLayout()
        backButton = QPushButton()
        backButton.setText( "Back" )
        def setDetailsAndGoBack():
            self.SetRouteDetails( route )
            self.AddRoutePage( route )
        backButton.clicked.connect( setDetailsAndGoBack )
        buttonLayout.addWidget( backButton )
        createRouteButton = QPushButton()
        createRouteButton.setText( "Create Route" )
        def setDetailsAndCreateRoute():
            self.SetRouteDetails( route )
            try:
                routeStore.AddRoute( route )
                self.MainMenu()
            except Exception as err:
                errorDialog = CustomDialog( "Exception Occurred", "Failed to create route: " + err.args[0] )
                errorDialog.exec_()
        createRouteButton.clicked.connect( setDetailsAndCreateRoute )
        buttonLayout.addWidget( createRouteButton )
        self._verticalLayout.addLayout( buttonLayout )

    def SetRouteDetails( self, route ):
        route.name = self.routeNameInput.text()
        route.difficulty = int( self.routeDifficultyInput.currentText() )
        route.style = RouteStyle[ self.routeStyleInput.currentText() ]
        route.rating = int( self.routeRatingInput.currentText() )
        route.notes = self.routeNotesInput.text()
        route.tags = list( map( lambda s: s.strip().lower(), self.routeTagsInput.text().split( ',' ) ) )

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
