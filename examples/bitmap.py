from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT
from resources.bitmaps import rain
from time import ticks_ms
# Set pins here or choose one of the sets
# tft = ILI9XXX_8B_DIRECT( data_pins [D0,D1,...D7], cs, dc, wr, rd, rst )

controller = ILI9XXX_8B_DIRECT.read_controller_name()
if controller == 'ESP32':
    tft = ILI9XXX_8B_DIRECT( [12, 13, 26, 25, 17, 16, 27, 14], 32, 15,  4,  2, 33 )
elif controller == 'RP2':
    tft = ILI9XXX_8B_DIRECT( [8, 9, 2, 3, 4, 5, 6, 7], 29, 28, 27, 26, 24 )
elif controller == 'ESP32-S3':
    tft = ILI9XXX_8B_DIRECT( [9, 8, 18, 17, 15, 16, 3, 14],  6,  7,  1,  2, 5 )
else:
    print("Unknown controller!")
    
print( controller, "display:", hex(tft.display_model),  tft.width, "x", tft.height )

COLOR_BLACK   = tft.rgb( 0, 0, 0 )
COLOR_BLUE    = tft.rgb( 0, 0, 255 )
COLOR_RED     = tft.rgb( 255, 0, 0 )
COLOR_GREEN   = tft.rgb( 0, 255, 0 )
COLOR_CYAN    = tft.rgb( 0, 255, 255 )
COLOR_MAGENTA = tft.rgb( 255, 0, 255 )
COLOR_YELLOW  = tft.rgb( 255, 255, 0 )
COLOR_WHITE   = tft.rgb( 255, 255, 255 )
COLOR_GRAY    = tft.rgb( 112, 160, 112 )

SCREEN_WIDTH  = tft.width
SCREEN_HEIGHT = tft.height

tft.fill(COLOR_BLACK) # Fill the screen with black color

size = rain[1]
    
colors = [COLOR_WHITE, COLOR_CYAN, COLOR_MAGENTA, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW]

start = ticks_ms()

tft.update_byte2gpio()
for i in range(len(colors)):
    color = colors[i]
    for y in range( SCREEN_HEIGHT // size ):
        for x in range( SCREEN_WIDTH // size ):
            tft.raw_bitmap(rain, x * size, y * size, color)
tft.cs.on()
print(ticks_ms()-start, 'ms')
#s3m8  big 637 ms
#pico  big 1,501 ms
#esp32 big 1,086