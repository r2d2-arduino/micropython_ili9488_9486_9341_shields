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
RD_PIN = RD_PIN
'''
# Plan B
YU_PIN = WR_PIN 
XL_PIN = DC_PIN
YD_PIN = DATA_PINS[7] 
XR_PIN = DATA_PINS[6]
RD_PIN = RD_PIN
'''

from ili9486 import ILI9486
from resist_touch import ResistiveTouchScreen
import LibreBodoni35 as bigFont
import time

button_radius = 40

col1 = button_radius + 20
col2 = button_radius * 3 + 40
col3 = button_radius * 5 + 60

row1 = 135
row2 = 235
row3 = 335
row4 = 435

tft = ILI9486(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)

SCREEN_WIDTH = tft.width
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

tft.fill_screen(COLOR_BLACK) # Black screen

tft.draw_rect(15, 15, 290, 60, COLOR_CYAN)

def button_state(num, state = 0):
    button_color = COLOR_YELLOW
    if state == 1:
        button_color = COLOR_CYAN
    
    if num == 1:
        tft.fill_circle(col1, row1, button_radius, button_color)
        tft.draw_text_fast("1", col1 - 8, row1 - 12, COLOR_BLACK, button_color)
    elif num == 2:
        tft.fill_circle(col2, row1, button_radius, button_color)
        tft.draw_text_fast("2", col2 - 8, row1 - 12, COLOR_BLACK, button_color)
    elif num == 3:
        tft.fill_circle(col3, row1, button_radius, button_color)
        tft.draw_text_fast("3", col3 - 8, row1 - 12, COLOR_BLACK, button_color)
    elif num == 4:
        tft.fill_circle(col1, row2, button_radius, button_color)
        tft.draw_text_fast("4", col1 - 8, row2 - 12, COLOR_BLACK, button_color)
    elif num == 5:
        tft.fill_circle(col2, row2, button_radius, button_color)
        tft.draw_text_fast("5", col2 - 8, row2 - 12, COLOR_BLACK, button_color)
    elif num == 6:
        tft.fill_circle(col3, row2, button_radius, button_color)
        tft.draw_text_fast("6", col3 - 8, row2 - 12, COLOR_BLACK, button_color)
    elif num == 7:
        tft.fill_circle(col1, row3, button_radius, button_color)
        tft.draw_text_fast("7", col1 - 8, row3 - 12, COLOR_BLACK, button_color)
    elif num == 8:
        tft.fill_circle(col2, row3, button_radius, button_color)
        tft.draw_text_fast("8", col2 - 8, row3 - 12, COLOR_BLACK, button_color)
    elif num == 9:
        tft.fill_circle(col3, row3, button_radius, button_color)
        tft.draw_text_fast("9", col3 - 8, row3 - 12, COLOR_BLACK, button_color)
    elif num == 10:
        tft.fill_circle(col1, row4, button_radius, button_color)
        tft.draw_text_fast("#", col1 - 8, row4 - 12, COLOR_BLACK, button_color)
    elif num == 0:
        tft.fill_circle(col2, row4, button_radius, button_color)
        tft.draw_text_fast("0", col2 - 8, row4 - 12, COLOR_BLACK, button_color)     
    elif num == 11:
        tft.fill_circle(col3, row4, button_radius, button_color)
        tft.draw_text_fast("*", col3 - 8, row4 - 8, COLOR_BLACK, button_color)
        
display_text = ""

def update_display():
    global display_text
    tft.draw_text_fast(display_text, 30, 30, COLOR_GREEN, COLOR_BLACK)
    

def is_point_in_circle(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2

def button_click(num, label):
    global display_text
    
    button_state(num, 1)
    
    display_text += label
    update_display()
    
    time.sleep_ms(300)
    button_state(num, 0)

for i in range(12):
    button_state(i, 0)

rts = ResistiveTouchScreen(YU_PIN, XL_PIN, YD_PIN, XR_PIN, RD_PIN, SCREEN_WIDTH, SCREEN_HEIGHT)

while True:
    x, y = rts.listening(30)       
        
    if is_point_in_circle(x, y, col1, row1, button_radius):
        button_click(1, "1")
        
    if is_point_in_circle(x, y, col2, row1, button_radius):
        button_click(2, "2")       
        
    if is_point_in_circle(x, y, col3, row1, button_radius):
        button_click(3, "3")       
        
    if is_point_in_circle(x, y, col1, row2, button_radius):
        button_click(4, "4")        
        
    if is_point_in_circle(x, y, col2, row2, button_radius):
        button_click(5, "5")       
        
    if is_point_in_circle(x, y, col3, row2, button_radius):
        button_click(6, "6")       
        
    if is_point_in_circle(x, y, col1, row3, button_radius):
        button_click(7, "7")       
        
    if is_point_in_circle(x, y, col2, row3, button_radius):
        button_click(8, "8")       
        
    if is_point_in_circle(x, y, col3, row3, button_radius):
        button_click(9, "9")        
        
    if is_point_in_circle(x, y, col1, row4, button_radius):
        button_click(10, "#")
        
    if is_point_in_circle(x, y, col2, row4, button_radius):
        button_click(0, "0")        
        
    if is_point_in_circle(x, y, col3, row4, button_radius):
        button_click(11, "*")
        
    if len(display_text) > 13:
        display_text = ""
        tft.fill_rect(20, 20, 280, 50, COLOR_BLACK)
                
