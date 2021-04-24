import time
from lights import *
from routes import *

exampleStartHold1 = Hold( 5, 1, HoldStatus.START )
exampleRegularHold1 = Hold( 3, 0, HoldStatus.REGULAR )
exampleFinishHold1 = Hold( 2, 3, HoldStatus.FINISH )
exampleRoute1 = Route( 'Route1', 16, [exampleStartHold1, exampleRegularHold1, exampleFinishHold1], 'First route!' )
exampleRoute2 = Route( 'Route2', 17, [exampleFinishHold1], 'Woah that\'s hard.' )

DisplayRoute(exampleRoute1)
time.sleep(2)
DisplayRoute(exampleRoute2)
