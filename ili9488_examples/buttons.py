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

from ili9488 import ILI9488
from resist_touch import ResistiveTouchScreen
import LibreBodoni24 as bigFont
import time

btn_height = 60
btn_width = 120

row1 = 20
row2 = btn_height + 50
row3 = btn_height * 2 + 80

col1 = 20
col2 = btn_width + 50

tft = ILI9488(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)

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

def button(label, x, y, width, height, color, bg, state = 0):
    sh = 2
    if state == 0:
        tft.fill_rect(x, y, width, height, color)            
        tft.draw_text(label, x + 30, y + 20, bg)    
        
        tft.fill_rect(x + 1, y + height + 1, width + sh, sh, COLOR_GRAY) # __
        tft.fill_rect(x + width + 1, y + 1,  sh, height + sh, COLOR_GRAY) # |
    else:
        tft.fill_rect(x + sh, y + sh, width + sh, height + sh, color)
        tft.draw_text(label, x + 30 + sh, y + 20 + sh, bg)  

        tft.fill_rect(x, y, width, sh,  COLOR_BLACK)
        tft.fill_rect(x, y, sh, height, COLOR_BLACK)


def buttonGen(btn, state):
    if btn == 0:
        button("Start",  col1, row1, btn_width, btn_height, COLOR_RED, COLOR_YELLOW, state)
    if btn == 1:
        button("Stop",   col2, row1, btn_width, btn_height, COLOR_BLUE, COLOR_YELLOW, state)
    if btn == 2:
        button("Reset",  col1, row2, btn_width, btn_height, COLOR_GREEN, COLOR_BLUE, state)
    if btn == 3:
        button("Config", col2, row2, btn_width, btn_height, COLOR_CYAN, COLOR_RED, state)
    if btn == 4:
        button(" Run",   col1, row3, btn_width, btn_height, COLOR_MAGENTA, COLOR_WHITE, state)
    if btn == 5:
        button(" Set",   col2, row3, btn_width, btn_height, COLOR_YELLOW, COLOR_BLACK, state)


def buttonClick(btn, name):
    tft.draw_text(name + ' clicked!', 80, 340, COLOR_GREEN)
    buttonGen(btn, 1)          
    time.sleep_ms(300)
    buttonGen(btn, 0)


tft.set_font(bigFont)

tft.fill_screen(COLOR_BLACK) # Black screen

for i in range(6):
    buttonGen(i, 0)

rts = ResistiveTouchScreen(YU_PIN, XL_PIN, YD_PIN, XR_PIN, RD_PIN, SCREEN_WIDTH, SCREEN_HEIGHT)

while True:
    x, y = rts.listening(30)     
        
    tft.fill_rect(50, 300, 220, 80, COLOR_BLACK)
    tft.draw_text('X = ' + str(x) + '  Y = ' + str(y), 80, 300, COLOR_GREEN)
    
    if col1 < x < col1 + btn_width  and row1 < y < row1 + btn_height:
        buttonClick(0, "Start")
        
    elif col2 < x < col2 + btn_width  and row1 < y < row1 + btn_height:
        buttonClick(1, "Stop")
        
    elif col1 < x < col1 + btn_width  and row2 < y < row2 + btn_height:
        buttonClick(2, "Reset")
        
    elif col2 < x < col2 + btn_width  and row2 < y < row2 + btn_height:
        buttonClick(3, "Config")
        
    elif col1 < x < col1 + btn_width  and row3 < y < row3 + btn_height:
        buttonClick(4, "Run")
        
    elif col2 < x < col2 + btn_width  and row3 < y < row3 + btn_height:
        buttonClick(5, "Set")

