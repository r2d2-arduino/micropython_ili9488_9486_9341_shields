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

from ili9341 import ILI9341

tft = ILI9341(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)

COLOR_BLACK   = tft.rgb( 0, 0, 0 )
COLOR_BLUE    = tft.rgb( 0, 0, 255 )
COLOR_RED     = tft.rgb( 255, 0, 0 )
COLOR_GREEN   = tft.rgb( 0, 255, 0 )
COLOR_CYAN    = tft.rgb( 0, 255, 255 )
COLOR_MAGENTA = tft.rgb( 255, 0, 255 )
COLOR_YELLOW  = tft.rgb( 255, 255, 0 )
COLOR_WHITE   = tft.rgb( 255, 255, 255 )
COLOR_GRAY    = tft.rgb( 112, 160, 112 )

tft.fill_screen(COLOR_BLACK) # Fill the screen with black color

sun = [0x0,0x80,0x2084,0x1888,0xc18,0x3c0,0x7e0,0x77ec,0x37ee,0x7e0,0x3c0,0xc18,0x1808,0x2084,0x80,0x0]
"""
sun = [
    b'0000000000000000',
    b'0000000010000000',
    b'0010000010000100',
    b'0001100010001000',
    b'0000110000011000',
    b'0000001111000000',
    b'0000011111100000',
    b'0111011111101100',
    b'0011011111101110',
    b'0000011111100000',
    b'0000001111000000',
    b'0000110000011000',
    b'0001100000001000',
    b'0010000010000100',
    b'0000000010000000',
    b'0000000000000000']
"""

size = 16
    
colors = [COLOR_WHITE, COLOR_CYAN, COLOR_MAGENTA, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW]

import time
start = time.ticks_ms()

for i in range(len(colors)):
    color = colors[i]
    for y in range(20):
        for x in range(15):
            tft.draw_bitmap_fast(sun, x * size, y * size, size, color, COLOR_BLACK)
              
print((time.ticks_ms()-start), 'ms')
