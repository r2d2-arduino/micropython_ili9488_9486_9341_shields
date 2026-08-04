from ili9xxx_8b_fb import ILI9XXX_8B_FB
import resources.LibreBodoni24 as bigFont
from resources.bitmaps import suncloud
from time import sleep_ms

# Set pins here or choose one of the sets
# tft = ILI9XXX_8B_DIRECT( data_pins [D0,D1,...D7], cs, dc, wr, rd, rst )

controller = ILI9XXX_8B_FB.read_controller_name()
if controller == 'ESP32':
    tft = ILI9XXX_8B_FB( [12, 13, 26, 25, 17, 16, 27, 14], 32, 15,  4,  2, 33 )
elif controller == 'RP2':
    tft = ILI9XXX_8B_FB( [8, 9, 2, 3, 4, 5, 6, 7], 29, 28, 27, 26, 24 )
elif controller == 'ESP32-S3':
    tft = ILI9XXX_8B_FB( [9, 8, 18, 17, 15, 16, 3, 14],  6,  7,  1,  2, 5 )
else:
    print("Unknown controller!")

print( tft.controller_name, "display:", hex(tft.display_model),  tft.width, "x", tft.height )

#tft.invert_display( True ) # If the display doesn't work correctly: Try to set inversion

delay = 500

SCREEN_WIDTH  = tft.width
SCREEN_HEIGHT = tft.height

COLOR_BLACK   = tft.color565( 0, 0, 0 )
COLOR_BLUE    = tft.color565( 0, 0, 255 )
COLOR_RED     = tft.color565( 255, 0, 0 )
COLOR_GREEN   = tft.color565( 0, 255, 0 )
COLOR_CYAN    = tft.color565( 0, 255, 255 )
COLOR_MAGENTA = tft.color565( 255, 0, 255 )
COLOR_YELLOW  = tft.color565( 255, 255, 0 )
COLOR_WHITE   = tft.color565( 255, 255, 255 )
COLOR_GRAY    = tft.color565( 112, 160, 112 )

tft.set_font(bigFont)
tft.tearing_effect()
tft.fill(COLOR_BLACK)
tft.show()

def rainbow( ):
    thin = 4
    short = (tft.display_model == 0x9341)
    
    for y in range(12, 32):
        
        c = (y + 1) * 8 - 1
        red     = tft.rgb( c, 0, 0 )
        yellow  = tft.rgb( c, c, 0 )
        green   = tft.rgb( 0, c, 0 )
        cyan    = tft.rgb( 0, c, c )
        blue    = tft.rgb( 0, 0, c )
        magenta = tft.rgb( c, 0, c )
        
        tft.rect(0, (y - 12) * thin +   0, SCREEN_WIDTH, thin, red, True) 
        tft.rect(0, (y - 12) * thin +  80, SCREEN_WIDTH, thin, yellow, True) 
        tft.rect(0, (y - 12) * thin + 160, SCREEN_WIDTH, thin, green, True)
        tft.rect(0, (y - 12) * thin + 240, SCREEN_WIDTH, thin, blue, True)
        if short:
            continue
        tft.rect(0, (y - 12) * thin + 320, SCREEN_WIDTH, thin, cyan, True) 
        tft.rect(0, (y - 12) * thin + 400, SCREEN_WIDTH, thin, magenta, True) 

    tft.show()


#bitmap
size = 16
for y in range( SCREEN_HEIGHT // size ):
    for x in range(  SCREEN_WIDTH // size ):
        tft.draw_bitmap(suncloud, x * size, y * size, COLOR_YELLOW)        
tft.show()
sleep_ms(delay)


grows = 32
gstep = SCREEN_HEIGHT // grows
cstep = 256 // grows
#blue gradient
for i in range(grows):
    c = (i + 1) * cstep - 1
    tft.rect(0, gstep * i, SCREEN_WIDTH, gstep, tft.rgb( 0, 0, c ), True)
tft.show()
sleep_ms(delay)

#red gradient
for i in range(grows):
    c = (i + 1) * cstep - 1
    tft.rect(0, gstep * i, SCREEN_WIDTH, gstep, tft.rgb( c, 0, 0 ), True)
tft.show()
sleep_ms(delay)

#green gradient
for i in range(grows):
    c = (i + 1) * cstep - 1
    tft.rect(0, gstep * i, SCREEN_WIDTH, gstep, tft.rgb( 0, c, 0 ), True)
tft.show()
sleep_ms(delay)

text = "	Lorem ipsum dolor sit amet,\n consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n\
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n Duis aute irure dolor\
        in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n Excepteur sint occaecat cupidatat non proident, \
        sunt in culpa qui officia deserunt mollit anim id est laborum."

tft.set_rotation(1)
tft.fill(COLOR_RED)
tft.draw_text(text, 4, 8, COLOR_YELLOW)
tft.show()
sleep_ms(delay)

tft.set_rotation(2)
tft.fill(COLOR_BLUE)
tft.draw_text(text, 4, 8, COLOR_WHITE)
tft.show()
sleep_ms(delay)

tft.set_rotation(3)
tft.fill(COLOR_GREEN)
tft.draw_text(text, 4, 8, COLOR_MAGENTA)
tft.show()
sleep_ms(delay)

tft.set_rotation(0)
rainbow()
tft.draw_text(text, 4, 8, COLOR_WHITE)
tft.show()
sleep_ms(delay)

tft.vert_scroll(0, tft.height, 0)
for _ in range(3):
    for line in range(SCREEN_HEIGHT):
        tft.vert_scroll_start_address(line + 1)
        sleep_ms(3) 
