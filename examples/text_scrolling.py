from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT
import resources.LibreBodoni24 as bigFont

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

COLOR_BLACK   = tft.rgb( 0, 0, 0 )
COLOR_BLUE    = tft.rgb( 0, 0, 255 )
COLOR_RED     = tft.rgb( 255, 0, 0 )
COLOR_GREEN   = tft.rgb( 0, 255, 0 )
COLOR_CYAN    = tft.rgb( 0, 255, 255 )
COLOR_MAGENTA = tft.rgb( 255, 0, 255 )
COLOR_YELLOW  = tft.rgb( 255, 255, 0 )
COLOR_WHITE   = tft.rgb( 255, 255, 255 )
COLOR_GRAY    = tft.rgb( 112, 160, 112 )

tft.set_font(bigFont)

tft.fill(COLOR_BLACK) # Fill the screen with black color

text = "Lorem ipsum dolor sit amet,\n consectetur adipiscing elit, sed do eiusmod tempor incididunt\
ut labore et dolore magna aliqua.\n Ut enim ad minim veniam, quis nostrud exercitation ullamco\
laboris nisi ut aliquip ex ea commodo consequat.\n Duis aute irure dolor in reprehenderit in \
voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n Excepteur sint occaecat \
cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

if tft.display_model in (0x9486, 0x9488):
    text = text * 2
    
tft.scroll_text( text, 4, 4, COLOR_WHITE, COLOR_BLACK, delay = 10 )
