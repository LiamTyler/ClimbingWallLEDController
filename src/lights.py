import board
import neopixel
from routes import *

PIXEL_PIN = board.D18
ORDER = neopixel.GRB

pixels = None

def DisplayRoute( route ):
    if pixels == None:
        pixels = neopixel.NeoPixel(
            PIXEL_PIN, routes.WALL_COLS * routes.WALL_ROWS, brightness=0.2, auto_write=False, pixel_order=ORDER
        )
    
    for hold in route.holds:
        if hold.status == HoldStatus.START:
            color = (255, 0, 0)
        elif hold.status == HoldStatus.REGULAR:
            color = (0, 255, 0)
        elif hold.status == HoldStatus.FINISH:
            color = (0, 0, 255)
        else:
            color = (0, 0, 0)
        pixels[hold.GetLEDCoord()] = color
        
    
