from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT
import resources.LibreBodoni24 as bigFont
from resources.bitmaps import rain
from time import sleep_ms

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

print( tft.controller_name, "Display:", hex(tft.display_model),  tft.width, "x", tft.height )

delay = 10
bigdelay = 1000

SCREEN_WIDTH  = tft.width
SCREEN_HEIGHT = tft.height

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
tft.tearing_effect()
tft.fill(COLOR_BLACK)

#bitmap
sun    = [0x0,0x80,0x2084,0x1888,0xc18,0x3c0,0x7e0,0x77ec,0x37ee,0x7e0,0x3c0,0xc18,0x1808,0x2084,0x80,0x0]
colors = [COLOR_WHITE, COLOR_CYAN, COLOR_MAGENTA, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW]
size = rain[1]

def rainbow( ):
    thin = 4
    short = (tft.display_model == 0x9341)
    
    for i in range(12, 32):
        
        c = (i + 1) * 8 - 1
        red     = tft.rgb( c, 0, 0 )
        yellow  = tft.rgb( c, c, 0 )
        green   = tft.rgb( 0, c, 0 )
        cyan    = tft.rgb( 0, c, c )
        blue    = tft.rgb( 0, 0, c )
        magenta = tft.rgb( c, 0, c )
        
        tft.fill_rect(0, (i - 12) * thin +   0, SCREEN_WIDTH, thin, red) 
        tft.fill_rect(0, (i - 12) * thin +  80, SCREEN_WIDTH, thin, yellow) 
        tft.fill_rect(0, (i - 12) * thin + 160, SCREEN_WIDTH, thin, green)
        tft.fill_rect(0, (i - 12) * thin + 240, SCREEN_WIDTH, thin, blue) 
        
        if short:
            continue
        tft.fill_rect(0, (i - 12) * thin + 320, SCREEN_WIDTH, thin, cyan)
        tft.fill_rect(0, (i - 12) * thin + 400, SCREEN_WIDTH, thin, magenta) 


for i in range(len(colors)):
    color = colors[i]
    for y in range( SCREEN_HEIGHT // size ):
        for x in range( SCREEN_WIDTH // size ):
            tft.draw_bitmap(rain, x * size, y * size, color)
   
grows = 32
gstep = SCREEN_HEIGHT // grows
cstep = 256 // grows
#blue gradient
for i in range(grows):
    c = (i + 1) * cstep - 1
    tft.fill_rect(0, gstep * i, SCREEN_WIDTH, gstep, tft.rgb( 0, 0, c ))
sleep_ms(bigdelay)

#red gradient
for i in range(grows):
    c = (i + 1) * cstep - 1
    tft.fill_rect(0, gstep * i, SCREEN_WIDTH, gstep, tft.rgb( c, 0, 0 ))
sleep_ms(bigdelay)

#green gradient
for i in range(grows):
    c = (i + 1) * cstep - 1
    tft.fill_rect(0, gstep * i, SCREEN_WIDTH, gstep, tft.rgb( 0, c, 0 ))
sleep_ms(bigdelay)

text = "	Lorem ipsum dolor sit amet,\n consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n\
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n Duis aute irure dolor\
        in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n Excepteur sint occaecat cupidatat non proident, \
        sunt in culpa qui officia deserunt mollit anim id est laborum."

tft.set_rotation(1)
tft.fill(COLOR_RED)
tft.draw_text(text, 4, 8, COLOR_YELLOW)
sleep_ms(bigdelay)

tft.set_rotation(2)
tft.fill(COLOR_BLUE)
tft.draw_text(text, 4, 8, COLOR_WHITE)
sleep_ms(bigdelay)

tft.set_rotation(3)
tft.fill(COLOR_GREEN)
tft.draw_text(text, 4, 8, COLOR_MAGENTA)
sleep_ms(bigdelay)

tft.set_rotation(0)
tft.fill(COLOR_BLACK)
tft.draw_text(text, 4, 8, COLOR_YELLOW)
sleep_ms(bigdelay)

rainbow()
tft.draw_text(text, 4, 8, COLOR_WHITE)
sleep_ms(bigdelay)

tft.vert_scroll(0, tft.height, 0)
for _ in range(3):
    for line in range(SCREEN_HEIGHT):
        tft.vert_scroll_start_address(line + 1)
        sleep_ms(3) 
