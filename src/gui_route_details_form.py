from PyQt5.QtWidgets import *
from routes import *

class RouteDetailsFormWidget( QWidget ):
    def __init__( self, route ):
        super().__init__()
        self.route = route
        formLayout = QFormLayout()
        self.routeNameInput = QLineEdit( self.route.name )

        self.routeDifficultyInput = QComboBox()
        self.routeStyleInput = QComboBox()
        self.routeRatingInput = QComboBox()
        self.routeNotesInput = QLineEdit()
        self.routeTagsInput = QLineEdit()

        self.routeDifficultyInput.addItems( [ str( i ) for i in range( 11 ) ] )  
        self.routeStyleInput.addItems( list( map( lambda rs: rs.name, RouteStyle ) ) )      
        self.routeRatingInput.addItems( [ str( i ) for i in range( 6 ) ] )
        self.SetFormDetails()
        
        formLayout.addRow( QLabel( "Route Name:" ), self.routeNameInput )
        formLayout.addRow( QLabel( "Difficulty:" ), self.routeDifficultyInput )
        formLayout.addRow( QLabel( "Route Style:" ), self.routeStyleInput )
        formLayout.addRow( QLabel( "Rating:" ), self.routeRatingInput )
        formLayout.addRow( QLabel( "Notes:" ), self.routeNotesInput )
        formLayout.addRow( QLabel( "Tags (Comma-Separated):" ), self.routeTagsInput )
        
        self.setLayout( formLayout )

    def SetFormDetails( self ):
        self.routeDifficultyInput.setCurrentText( str( self.route.difficulty ) )
        self.routeStyleInput.setCurrentText( self.route.style.name )
        self.routeRatingInput.setCurrentText( str( self.route.rating ) )
        self.routeNotesInput.setText( self.route.notes )
        self.routeTagsInput.setText( ", ".join( self.route.tags ) )

    def UpdateRouteDetails( self ):
        self.route.name = self.routeNameInput.text()
        self.route.difficulty = int( self.routeDifficultyInput.currentText() )
        self.route.style = RouteStyle[ self.routeStyleInput.currentText() ]
        self.route.rating = int( self.routeRatingInput.currentText() )
        self.route.notes = self.routeNotesInput.text()
        self.route.tags = list( map( lambda s: s.strip().lower(), self.routeTagsInput.text().split( ',' ) ) )