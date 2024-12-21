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

# Touchscreen pins
YU_PIN = DC_PIN 
XL_PIN = DATA_PINS[1]
YD_PIN = DATA_PINS[0] 
XR_PIN = CS_PIN
'''
# Plan B
YU_PIN = WR_PIN 
XL_PIN = DC_PIN
YD_PIN = DATA_PINS[7] 
XR_PIN = DATA_PINS[6]
'''
from ili9486 import ILI9486
from sys import platform
if platform == 'rp2':
    from resist_touch_rp2 import ResistiveTouchScreen
else:
    from resist_touch import ResistiveTouchScreen
import time

tft = ILI9486(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)

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

def clearDisplay():
    tft.fill_screen(COLOR_BLACK) 
    tft.fill_rect(0,   0, 40,  40, COLOR_BLUE)
    tft.fill_rect(40,  0, 40,  40, COLOR_RED)
    tft.fill_rect(80,  0, 40, 40, COLOR_GREEN)
    tft.fill_rect(120, 0, 40, 40, COLOR_CYAN)
    tft.fill_rect(160, 0, 40, 40, COLOR_MAGENTA)
    tft.fill_rect(200, 0, 40, 40, COLOR_YELLOW)
    tft.fill_rect(240, 0, 40, 40, COLOR_WHITE)
    tft.fill_rect(280, 0, 40, 40, COLOR_BLACK)

clearDisplay()

rts = ResistiveTouchScreen(YU_PIN, XL_PIN, YD_PIN, XR_PIN, RD_PIN, SCREEN_WIDTH, SCREEN_HEIGHT)

current_color = COLOR_GRAY

while True:
    x, y = rts.listening(1) 
            
    if y < 41:
        if 0 <= x < 40:
            current_color = COLOR_BLUE
        elif 40 <= x < 80:
            current_color = COLOR_RED
        elif 80 <= x < 120:
            current_color = COLOR_GREEN
        elif 120 <= x < 160:
            current_color = COLOR_CYAN
        elif 160 <= x < 200:
            current_color = COLOR_MAGENTA
        elif 200 <= x < 240:
            current_color = COLOR_YELLOW
        elif 240 <= x < 280:
            current_color = COLOR_WHITE
        else:
            clearDisplay()
            time.sleep_ms(500)
    else:
        tft.fill_circle(x, y, 5, current_color) 

