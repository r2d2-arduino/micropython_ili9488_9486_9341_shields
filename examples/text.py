from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT
import resources.LibreBodoni24 as bigFont
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

print( tft.controller_name, "display:", hex(tft.display_model),  tft.width, "x", tft.height )

tft.set_rotation(0)

COLOR_BLACK    = tft.rgb( 0, 0, 0 )
COLOR_BLUE     = tft.rgb( 0, 0, 0xFF )
COLOR_RED      = tft.rgb( 0xFF, 0, 0 )
COLOR_GREEN    = tft.rgb( 0, 0xFF, 0 )
COLOR_CYAN     = tft.rgb( 0, 0xFF, 0xFF )
COLOR_MAGENTA  = tft.rgb( 0xFF, 0, 0xFF )
COLOR_YELLOW   = tft.rgb( 0xFF, 0xFF, 0x00 )
COLOR_WHITE    = tft.rgb( 0xFF, 0xFF, 0xFF )
COLOR_GRAY     = tft.rgb( 112, 160, 112 )
COLOR_AMBER    = tft.rgb( 0xFF, 0x9F, 0 )
COLOR_PHOSPHOR = tft.rgb( 0x39, 0xFF, 0x14 )

tft.set_font(bigFont)

tft.fill(COLOR_BLACK) # Fill the screen with black color

start = ticks_ms()

text = " Lorem ipsum dolor sit amet,\n consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n\
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n Duis aute irure dolor\
in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n Excepteur sint occaecat cupidatat non proident, \
sunt in culpa qui officia deserunt mollit anim id est laborum."

tft.draw_text(text, 4, 4, COLOR_YELLOW)

print(ticks_ms()-start, 'ms')
#s3m8  big 74 ms
#pico  big 221
#esp32 big 178