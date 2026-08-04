from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT
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

tft.draw_circle(SCREEN_WIDTH >> 1, SCREEN_HEIGHT >> 1, (SCREEN_WIDTH >> 1) - 4, COLOR_BLUE, 4)

tft.fill_circle(SCREEN_WIDTH >> 2, SCREEN_HEIGHT - (SCREEN_HEIGHT >> 2) + 20, SCREEN_WIDTH >> 2, COLOR_YELLOW)

tft.draw_rect(10, 10, (SCREEN_WIDTH >> 1) - 20, SCREEN_HEIGHT >> 2, COLOR_RED, 2)

tft.fill_rect(10, SCREEN_HEIGHT // 3, (SCREEN_WIDTH >> 1) - 20, SCREEN_HEIGHT >> 2, COLOR_MAGENTA)

for y in range(SCREEN_HEIGHT // 8):
    tft.draw_line(0, 0, SCREEN_WIDTH, y * 8 , COLOR_GREEN)

print(ticks_ms()-start, 'ms')

#s3m8  big 110 ms
#pico  big 221
#esp32 big 156