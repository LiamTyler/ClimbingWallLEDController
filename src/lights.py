from routes import *
try:
    import board
    import neopixel
    g_IsRunningOnRaspberryPi = True
except:
    g_IsRunningOnRaspberryPi = False

g_ledPixels = None

def LED_InitializeController():
    global g_ledPixels
    if g_IsRunningOnRaspberryPi:
        g_ledPixels = neopixel.NeoPixel( board.D18, WALL_COLS * WALL_ROWS, brightness=0.5, auto_write=False, pixel_order=neopixel.GRB )


def LED_DisplayRoute( route ):
    if not g_ledPixels:
        print( "Can't display route because not connected to LEDs" )
        return
    
    g_ledPixels.fill((0,0,0))
    for hold in route.holds:
        if hold.status == HoldStatus.START:
            color = (255, 0, 0)
        elif hold.status == HoldStatus.REGULAR:
            color = (0, 0, 255)
        elif hold.status == HoldStatus.FINISH:
            color = (0, 255, 0)
        else:
            color = (0, 0, 0)
        g_ledPixels[hold.GetLEDCoord()] = color
    g_ledPixels.show()