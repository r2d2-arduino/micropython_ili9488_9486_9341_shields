# Set pins here or choose one of the sets
# for Esp32-S3
DATA_PINS = [9, 8, 18, 17, 15, 16, 3, 14] #D0..D7
CS_PIN  = 6
DC_PIN  = 7 # = RS_PIN
WR_PIN  = 1
RD_PIN  = 2
RST_PIN = 5
'''
#for RP2
DATA_PINS = [2, 1, 8, 7, 6, 5, 4, 3]
CS_PIN  = 26
DC_PIN  = 27 # rs/dc
WR_PIN  = 28
RD_PIN  = 22 
RST_PIN = 21
#for ESP32 D1R32
DATA_PINS = [12, 13, 26, 25, 17, 16, 27, 14]
CS_PIN = 32
DC_PIN = 15 #rs/dc
WR_PIN = 4
RD_PIN = 2
RST_PIN = 33
'''

from ili9486 import ILI9486
import LibreBodoni24 as bigFont

text = "Lorem ipsum dolor sit amet,\n consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna \
aliqua.\n Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\n Duis aute irure \
dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n Excepteur sint occaecat cupidatat non proident, \
sunt in culpa qui officia deserunt mollit anim id est laborum."

tft = ILI9486(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)

COLOR_BLACK   = tft.rgb( 0, 0, 0 )
COLOR_BLUE    = tft.rgb( 0, 0, 255 )
COLOR_RED     = tft.rgb( 255, 0, 0 )
COLOR_GREEN   = tft.rgb( 0, 255, 0 )
COLOR_CYAN    = tft.rgb( 0, 255, 255 )
COLOR_MAGENTA = tft.rgb( 255, 0, 255 )
COLOR_YELLOW  = tft.rgb( 255, 255, 0 )
COLOR_WHITE   = tft.rgb( 255, 255, 255 )
COLOR_GRAY    = tft.rgb( 112, 160, 112 )

tft.set_rotation(0) # 0..3 = 0..270 degrees

tft.set_font(bigFont)

tft.fill_screen(COLOR_BLACK)

import time
start = time.ticks_ms()

tft.draw_text_fast(text, 0, 0, COLOR_WHITE, COLOR_BLACK)
#tft.draw_text(text, 0, 0, COLOR_WHITE)

print(time.ticks_diff(time.ticks_ms(), start), 'ms')


