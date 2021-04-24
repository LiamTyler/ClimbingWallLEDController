import board
import neopixel
from routes import *

PIXEL_PIN = board.D18
ORDER = neopixel.GRB

pixels = None

def DisplayRoute( route ):
    global pixels
    if pixels == None:
        pixels = neopixel.NeoPixel(
            PIXEL_PIN, WALL_COLS * WALL_ROWS, brightness=0.5, auto_write=False, pixel_order=ORDER
        )
    pixels.fill((0,0,0))
    for hold in route.holds:
        if hold.status == HoldStatus.START:
            color = (255, 0, 0)
        elif hold.status == HoldStatus.REGULAR:
            color = (0, 0, 255)
        elif hold.status == HoldStatus.FINISH:
            color = (0, 255, 0)
        else:
            color = (0, 0, 0)
        pixels[hold.GetLEDCoord()] = color
    pixels.show()

