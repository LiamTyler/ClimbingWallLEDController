from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from gui_wall_widget import *
from gui_route_details_form import *
from gui_route_creator import CustomDialog


class RouteViewer( QWidget ):
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
        layout.setAlignment( Qt.AlignTop )

        hbox = QHBoxLayout()
        detailsForm = RouteDetailsFormWidget( self.route )
        def resetDetailsAndGoBack():
            detailsForm.SetFormDetails()
            self.ChangePage( 0 )
        backButton = QPushButton( "Back" )
        backButton.clicked.connect( lambda: resetDetailsAndGoBack() )
        saveButton = QPushButton( "Save Changes" )
        saveButton.clicked.connect( lambda: self.SaveDetailsChanges( detailsForm ) )
        hbox.addWidget( backButton )
        hbox.addWidget( saveButton )
        layout.addWidget( detailsForm )
        layout.addLayout( hbox )
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
        g_routeStore._UpdateRouteStore()
        self.viewWall.DrawRoute( self.route )
        self.ChangePage( 0 )

    def SaveDetailsChanges( self, detailsForm ):
        detailsForm.UpdateRouteDetails()
        g_routeStore._UpdateRouteStore()
        self.ChangePage( 0 )
	
    def ChangePage( self,i ):
        #self.buttons[self.stack.currentIndex() + 1].setChecked( False )
        #self.buttons[i + 1].setChecked( True )
        self.stack.setCurrentIndex( i )