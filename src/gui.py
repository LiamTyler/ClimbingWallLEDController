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


class CustomDialog( QDialog ):
    def __init__( self, title, msg, parent=None ):
        super().__init__( parent=parent )

        self.setWindowTitle( title )
        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox( QBtn )
        self.buttonBox.accepted.connect( self.accept )

        self.layout = QVBoxLayout()
        message = QLabel( msg )
        self.layout.addWidget( message )
        self.layout.addWidget( self.buttonBox )
        self.setLayout( self.layout )


class MainRouteViewer( QWidget ):
    def __init__( self, route, mainWindow ):
        super().__init__()
        self.route = route
        self.mainWindow = mainWindow
        self.viewWall = None # must be updated whenever route is edited
        mainWindow.setWindowTitle( "Route: " + route.name )
        vbox = QVBoxLayout()
        vbox.setAlignment( Qt.AlignTop )
        vbox.setSpacing( 20 )
        buttonGroup = QWidget()
        buttonGroup.setLayout( vbox )
        buttonGroup.setStyleSheet( "background-color: #292929" )
        self.buttons = []
        icons = [ "left-arrow.svg", "magnify.svg", "paper.svg", "edit.svg", "trash_2.svg" ]
        for i in range( len( icons ) ):
            b = QPushButton()
            b.setStyleSheet( "background-color: #FFFFFF" )
            b.setIcon( QIcon( "../icons/" + icons[i] ) )
            #b.setCheckable( True )
            self.buttons.append( b )
            vbox.addWidget( b )
        self.buttons[0].clicked.connect( mainWindow.MainMenu )
        self.buttons[1].clicked.connect( lambda: self.ChangePage( 0 ) )
        self.buttons[2].clicked.connect( lambda: self.ChangePage( 1 ) )
        self.buttons[3].clicked.connect( lambda: self.ChangePage( 2 ) )
        self.buttons[4].clicked.connect( lambda: self.ChangePage( 3 ) )
        #self.buttons[1].setChecked( True )
        
        self.viewRoutePage = QWidget()
        self.detailsPage = QWidget()
        self.editRoutePage = QWidget()
        self.deleteRoutePage = QWidget()
        self.SetupViewPage()
        self.SetupDetailsPage()
        self.SetupEditPage()
        self.SetupDeletePage()

        self.stack = QStackedWidget( self )
        self.stack.addWidget( self.viewRoutePage )
        self.stack.addWidget( self.detailsPage )
        self.stack.addWidget( self.editRoutePage )
        self.stack.addWidget( self.deleteRoutePage )

        hbox = QHBoxLayout( self )
        hbox.addWidget( buttonGroup )
        hbox.addWidget( self.stack )
        hbox.setSpacing( 0 )
        self.setLayout( hbox )
        hbox.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
    
    def SetupViewPage( self ):
        layout = QVBoxLayout()
        layout.setAlignment( Qt.AlignCenter )
        self.viewWall = WallWidget()
        self.viewWall.SetEditable( False )
        self.viewWall.DrawRoute( self.route )
        layout.addWidget( self.viewWall )
        self.viewRoutePage.setLayout( layout )

    def SetupDetailsPage( self ):
        layout = QVBoxLayout()
        layout.setAlignment( Qt.AlignCenter )
        layout.addWidget( QLabel( "Route Details Page" ) )
        self.detailsPage.setLayout( layout )

    def SetupEditPage( self ):
        layout = QVBoxLayout()
        layout.setAlignment( Qt.AlignCenter )
        wall = WallWidget()
        wall.SetEditable( True )
        wall.DrawRoute( self.route )

        hbox = QHBoxLayout()
        backButton = QPushButton( "Back" )
        backButton.clicked.connect( lambda: self.ChangePage( 0 ) )
        saveButton = QPushButton( "Save Changes" )
        saveButton.clicked.connect( lambda: self.SaveRouteChanges( wall ) )
        hbox.addWidget( backButton )
        hbox.addWidget( saveButton )
        layout.addWidget( wall )
        layout.addLayout( hbox )
        
        self.editRoutePage.setLayout( layout )

    def SetupDeletePage( self ):
        vbox = QVBoxLayout()
        vbox.setAlignment( Qt.AlignCenter )
        label = QLabel( "Are you sure you want to delete route '" + self.route.name + "'?" )
        label.setFont( STENCIL_FONT )
        vbox.addWidget( label )
        hbox = QHBoxLayout()
        yesButton = QPushButton( "Yes" )
        yesButton.clicked.connect( lambda: self.mainWindow.DeleteRoute( self.route ) )
        noButton = QPushButton( "No" )
        noButton.clicked.connect( lambda: self.ChangePage( 0 ) )
        hbox.addWidget( yesButton )
        hbox.addWidget( noButton )
        vbox.addLayout( hbox )
        self.deleteRoutePage.setLayout( vbox )

    def SaveRouteChanges( self, editWall ):
        # This route actually is a reference to actual stored route, so we just need to resave the DB
        self.route.holds = editWall.GetCurrentlyDrawnHolds()
        routeStore._UpdateRouteStore()
        self.viewWall.DrawRoute( self.route )
        self.ChangePage( 0 )
	
    def ChangePage( self,i ):
        #self.buttons[self.stack.currentIndex() + 1].setChecked( False )
        #self.buttons[i + 1].setChecked( True )
        self.stack.setCurrentIndex( i )


class MainWindow( QMainWindow ):
    def __init__( self ):
        super( MainWindow, self ).__init__()
        self.resize( WINDOW_SIZE[0], WINDOW_SIZE[1] )
        self.setStyleSheet( "background-color: lightGray;" )
        self._centralWidget = QWidget( self )
        self.setCentralWidget( self._centralWidget )
        self._verticalLayout = QVBoxLayout()
        self._verticalLayout.setSpacing( 0 )
        self._verticalLayout.setContentsMargins( QMargins( 0, 0, 0, 0 ) )
        self._centralWidget.setLayout( self._verticalLayout )
        self._centralWidget.setSizePolicy( QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed )
        self.MainMenu()
        self.show()

    def _clearLayout( self, layout ):
        if layout is not None:
            for i in reversed( range( layout.count() ) ): 
                item = layout.itemAt( i )
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self._clearLayout( item.layout() )

    def DeleteRoute( self, route ):
        routeStore.DeleteRoute( route )
        self.MainMenu()

    def ViewRoutePage( self, dispRoute ):
        self._clearLayout( self._verticalLayout )
        LED_DisplayRoute( dispRoute.route )
        self._verticalLayout.setSpacing( 0 )
        routeViewer = MainRouteViewer( dispRoute.route, self )
        self._verticalLayout.addWidget( routeViewer )

    def MainMenu( self ):
        self.setWindowTitle( "Home Wall App" )
        self._clearLayout( self._verticalLayout )
        #self._verticalLayout.addWidget( QLabel( "wut" ) )
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

    def AddRoutePage( self ):
        self._clearLayout( self._verticalLayout )
        wall = WallWidget()
        wall.SetEditable( True )
        
        addRouteButton = QPushButton( self )
        addRouteButton.setText( "Continue" )
        addRouteButton.setStyleSheet( "background-color : white" )
        addRouteButton.clicked.connect( lambda: self.AddRoute( wall.GetCurrentlyDrawnHolds() ) )

        backButton = QPushButton ( self )
        backButton.setText( "Back" )
        backButton.setStyleSheet( "background-color : white" )
        backButton.clicked.connect( self.MainMenu )

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget( backButton )
        buttonLayout.addWidget( addRouteButton )
        self._verticalLayout.addWidget( wall )
        self._verticalLayout.addLayout( buttonLayout )

    # TODO: Disallow invalid routes (0 holds, no starts, no finish, etc)
    def AddRoute( self, holds ):
        route = Route()
        route.holds = holds
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
