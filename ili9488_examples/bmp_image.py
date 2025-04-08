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

def file_exists(filename):
    import os
    try:
        os.stat(filename)
        return True
    except OSError:
        print("File not found:", filename)
        return False
    
from ili9488 import ILI9488

tft = ILI9488(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)

tft.set_rotation(2) # 0 = 0 degree, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

tft.fill_screen(0) # Fill the screen with black color

import time
filename = 'road320x480.bmp'
if file_exists(filename):
    start = time.ticks_ms()
    
    tft.draw_bmp(filename, 0, 0)
    
    print(time.ticks_diff(time.ticks_ms(), start), 'ms')
    