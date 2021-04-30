from gui_route_viewer import *
from gui_main_menu import *
from gui_route_creator import *
from gui_route_details_form import *
from routes import *
from routeStore import *
from lights import *

STENCIL_FONT = QFont( QFont( 'Arial', 16 ) )
STENCIL_FONT.setBold( True )

WINDOW_SIZE = (600, 800)

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
        g_routeStore.DeleteRoute( route )
        self.MainMenu()

    def ViewRoutePage( self, dispRoute ):
        self._clearLayout( self._verticalLayout )
        LED_DisplayRoute( dispRoute.route )
        self._verticalLayout.setSpacing( 0 )
        routeViewer = RouteViewer( dispRoute.route, self )
        self._verticalLayout.addWidget( routeViewer )

    def CreateRoutePage( self ):
        self._clearLayout( self._verticalLayout )
        self._verticalLayout.addWidget( CreateRouteView( self ) )

    def MainMenu( self ):
        self.setWindowTitle( "Home Wall App" )
        self._clearLayout( self._verticalLayout )

        topBarWidget = QWidget()
        #topBarWidget.setFixedHeight( 40 )
        topBarWidget.setStyleSheet( "background-color: #292929" )
        topBarHBox = QHBoxLayout()
        topBarWidget.setLayout( topBarHBox )
        filterButton = QPushButton()
        filterButton.setStyleSheet( "background-color: #FFFFFF" )
        filterButton.setIcon( QIcon( "../icons/menu.svg" ) )
        #filterButton.clicked.connect(  )
        topBarHBox.setAlignment( Qt.AlignRight )
        topBarHBox.addWidget( filterButton )

        vlist = QListWidget( self )
        routes = g_routeStore.GetAllRoutes()
        for route in routes:
            vlist.addItem( RouteListItem( route ) )
        scrollBar = QScrollBar()
        vlist.setVerticalScrollBar( scrollBar )
        vlist.itemClicked.connect( self.ViewRoutePage )

        addRouteButton = QPushButton( self )
        addRouteButton.setText( "Add Route" )
        addRouteButton.setStyleSheet( "background-color : white" )
        addRouteButton.clicked.connect( self.CreateRoutePage )
        self._verticalLayout.addWidget( topBarWidget )
        self._verticalLayout.addWidget( vlist )
        self._verticalLayout.addWidget( addRouteButton )

# For ease of test route creation
def Hold_S( str ):
    return Hold( int( str[1:] ) - 1, ord( str[0] ) - 65, HoldStatus.START )

def Hold_R( str ):
    return Hold( int( str[1:] ) - 1, ord( str[0] ) - 65, HoldStatus.REGULAR )

def Hold_F( str ):
    return Hold( int( str[1:] ) - 1, ord( str[0] ) - 65, HoldStatus.FINISH )

if __name__ == '__main__':
    LED_InitializeController()
    g_routeStore = RouteStore()
    route1 = Route( "Route 1", 5, 4, RouteStyle.SLOPEY )
    route1.holds = [ Hold_S( "A1" ), Hold_S( "B3" ), Hold_R( "C6" ), Hold_R( "D7" ), Hold_F( "E9" ) ]
    route2 = Route( "Route 2", 3, 5, RouteStyle.CRIMPY )
    route2.holds = [ Hold_S( "A3" ), Hold_S( "B4" ), Hold_R( "B8" ), Hold_F( "C9" ) ]
    route3 = Route( "Route 3", 4, 2, RouteStyle.JUGGY )
    route3.holds = [ Hold_S( "E3" ), Hold_S( "D3" ), Hold_R( "D6" ), Hold_R( "C6" ), Hold_F( "B9" ) ]
    
    g_routeStore.AddRoute( route1 )
    g_routeStore.AddRoute( route2 )
    g_routeStore.AddRoute( route3 )
    app = QApplication( [] )
    window = MainWindow()
    app.exec_()
