# Set pins here or choose one of the sets

#for ESP32 D1R32
DATA_PINS = [12, 13, 26, 25, 17, 16, 27, 14]
CS_PIN = 32
DC_PIN = 15 #rs/dc
WR_PIN = 4
RD_PIN = 2
RST_PIN = 33
'''
#for RP2
DATA_PINS = [8, 9, 2, 3, 4, 5, 6, 7]
CS_PIN  = 29
DC_PIN  = 28 # rs/dc
WR_PIN  = 27
RD_PIN  = 26
RST_PIN = 24

# for Esp32-S3
DATA_PINS = [9, 8, 18, 17, 15, 16, 3, 14] #D0..D7
CS_PIN  = 6
DC_PIN  = 7 # = RS_PIN
WR_PIN  = 1
RD_PIN  = 2
RST_PIN = 5
'''

from ili9341 import ILI9341
import LibreBodoni24 as bigFont
from bitmaps import rain
import time

delay = 10

tft = ILI9341(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)

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
tft.fill_screen(COLOR_BLACK)

#bitmap
sun    = [0x0,0x80,0x2084,0x1888,0xc18,0x3c0,0x7e0,0x77ec,0x37ee,0x7e0,0x3c0,0xc18,0x1808,0x2084,0x80,0x0]
colors = [COLOR_WHITE, COLOR_CYAN, COLOR_MAGENTA, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW]
size = 16


for i in range(len(colors)):
    color = colors[i]
    for y in range(20):
        for x in range(15):
            tft.draw_bitmap_fast(rain, x * size, y * size, color, COLOR_BLACK)

#blue gradient
for y in range(32):
    tft.fill_rect(0, y * 15, SCREEN_WIDTH, 15, y)
    time.sleep_ms(delay)
time.sleep_ms(500)

#red gradient
for y in range(32):
    tft.fill_rect(0, y * 15, SCREEN_WIDTH, 15, y << 11)
    time.sleep_ms(delay)
time.sleep_ms(500)

#green gradient
for y in range(32):
    tft.fill_rect(0, y * 15, SCREEN_WIDTH, 15, y << 6)
    time.sleep_ms(delay)
time.sleep_ms(500)


def rainbow():
    #red
    for y in range(12, 32):
        color = ((y << 11) & 0xF800)
        tft.fill_rect(0, (y - 12) * 4, SCREEN_WIDTH, 4, color)
        time.sleep_ms(delay)
        
    #red-green
    for y in range(12, 32):
        color = ((y << 11) & 0xF800) | ((y << 5) & 0x07E0)
        tft.fill_rect(0, (y - 12) * 4 + 80, SCREEN_WIDTH, 4, color)
        time.sleep_ms(delay)

    #green
    for y in range(12, 32):
        color = ((y << 5) & 0x07E0)
        tft.fill_rect(0, (y - 12) * 4 + 160, SCREEN_WIDTH, 4, color)
        time.sleep_ms(delay)

    #green-blue
    for y in range(12, 32):
        color = ((y << 5) & 0x07E0) | (y & 0x001F)
        tft.fill_rect(0, (y - 12) * 4 + 240, SCREEN_WIDTH, 4, color)
        time.sleep_ms(delay)
   

rainbow()

text = "	Lorem ipsum dolor sit amet,\n consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n\
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n Duis aute irure dolor\
        in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n Excepteur sint occaecat cupidatat non proident, \
        sunt in culpa qui officia deserunt mollit anim id est laborum."

tft.draw_text(text, 10, 20, COLOR_WHITE)

tft.set_rotation(1)
tft.fill_screen(COLOR_RED)
tft.draw_text_fast(text, 10, 20, COLOR_YELLOW, COLOR_RED)
time.sleep_ms(500)

tft.set_rotation(2)
tft.fill_screen(COLOR_BLUE)
tft.draw_text_fast(text, 10, 20, COLOR_WHITE, COLOR_BLUE)
time.sleep_ms(500)

tft.set_rotation(3)
tft.fill_screen(COLOR_GREEN)
tft.draw_text_fast(text, 10, 20, COLOR_MAGENTA, COLOR_GREEN)
time.sleep_ms(500)

tft.set_rotation(0)
tft.fill_screen(COLOR_BLACK)
tft.draw_text_fast(text, 10, 20, COLOR_WHITE, COLOR_BLACK)
time.sleep_ms(500)

rainbow()
tft.vert_scroll(0, tft.height, 0)
for _ in range(3):
    for line in range(SCREEN_HEIGHT):
        tft.vert_scroll_start_address(line + 1)
        time.sleep_ms(3) 
