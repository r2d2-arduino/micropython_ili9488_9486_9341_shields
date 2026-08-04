from ili9xxx_8b_fb import ILI9XXX_8B_FB
from time import ticks_ms
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

start = ticks_ms()

tft.fill(COLOR_BLACK) # Fill the screen with black color

tft.ellipse(SCREEN_WIDTH >> 1, SCREEN_HEIGHT >> 1, (SCREEN_WIDTH >> 1) - 1, (SCREEN_WIDTH >> 1) - 1, COLOR_BLUE)

tft.ellipse(SCREEN_WIDTH >> 2, SCREEN_HEIGHT - (SCREEN_HEIGHT >> 2) + 16, SCREEN_WIDTH >> 2, SCREEN_WIDTH >> 2, COLOR_YELLOW, True)

tft.rect(10, 10, (SCREEN_WIDTH >> 1) - 20, SCREEN_HEIGHT >> 2, COLOR_RED)

tft.rect(10, SCREEN_HEIGHT // 3, (SCREEN_WIDTH >> 1) - 20, SCREEN_HEIGHT >> 2, COLOR_MAGENTA, True)

for y in range(SCREEN_HEIGHT // 8):
    tft.line(0, 0, SCREEN_WIDTH - 1, y * 8 , COLOR_GREEN)


tft.show()

print(ticks_ms()-start, 'ms') 

#s3m8 big 69 ms
#s3m8 sma 36
#pico sma 74