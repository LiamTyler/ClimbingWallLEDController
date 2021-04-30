from gui_wall_widget import *
from gui_route_details_form import *
from routeStore import *

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

# TODO: Disallow invalid routes (0 holds, no starts, no finish, etc)
class CreateRouteView( QWidget ):
    def __init__( self, mainWindow ):
        super().__init__()
        self.mainWindow = mainWindow
        self.mainWindow.setWindowTitle( "Create Route" )

        self.route = Route()
        self.stack = QStackedWidget()
        self.stack.addWidget( self.SetupAddHoldsPage() )
        self.stack.addWidget( self.SetupAddDetailsPage() )
        self.stack.setCurrentIndex( 0 )

        vbox = QVBoxLayout()
        vbox.addWidget( self.stack )
        self.setLayout ( vbox )
    
    def SetupAddHoldsPage( self ):
        wall = WallWidget()
        wall.SetEditable( True )
        wall.DrawRoute( self.route )

        wallBox = QVBoxLayout()
        wallBox.setAlignment( Qt.AlignCenter )
        wallBox.addWidget( wall )
        
        def getHoldsAndContinue():
            self.route.holds = wall.GetCurrentlyDrawnHolds()
            self.stack.setCurrentIndex( 1 )
        continueButton = QPushButton( self )
        continueButton.setText( "Continue" )
        continueButton.setStyleSheet( "background-color : white" )
        continueButton.clicked.connect( lambda: getHoldsAndContinue() )

        backButton = QPushButton ( self )
        backButton.setText( "Back" )
        backButton.setStyleSheet( "background-color : white" )
        backButton.clicked.connect( self.mainWindow.MainMenu )

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget( backButton )
        buttonLayout.addWidget( continueButton )

        vbox = QVBoxLayout()
        vbox.addLayout( wallBox )
        vbox.addLayout( buttonLayout )
        w = QWidget()
        w.setLayout( vbox )
        return w

    def SetupAddDetailsPage( self ):
        global g_routeStore
        self.route = Route()
        detailsForm = RouteDetailsFormWidget( self.route )
        vbox = QVBoxLayout()
        vbox.addWidget( detailsForm )

        def setDetailsAndGoBack():
            detailsForm.UpdateRouteDetails()
            self.stack.setCurrentIndex( 0 )
        buttonLayout = QHBoxLayout()
        backButton = QPushButton()
        backButton.setText( "Back" )
        backButton.setStyleSheet( "background-color : white" )
        backButton.clicked.connect( setDetailsAndGoBack )
        buttonLayout.addWidget( backButton )

        def setDetailsAndCreateRoute():
            detailsForm.UpdateRouteDetails()
            try:
                g_routeStore.AddRoute( self.route )
                self.mainWindow.MainMenu()
            except Exception as err:
                errorDialog = CustomDialog( "Exception Occurred", "Failed to create route: " + err.args[0] )
                errorDialog.exec_()
        createRouteButton = QPushButton()
        createRouteButton.setText( "Create Route" )
        createRouteButton.setStyleSheet( "background-color : white" )
        createRouteButton.clicked.connect( setDetailsAndCreateRoute )
        buttonLayout.addWidget( createRouteButton )
        
        vbox.addLayout( buttonLayout )
        w = QWidget()
        w.setLayout( vbox )
        return w
