from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT
import resources.LibreBodoni24 as bigFont
from resist_touch import ResistiveTouchScreen
import time
    
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
  
# Touchscreen pins
YU_PIN = tft.dc_pin 
XL_PIN = tft.data_pins[1]
YD_PIN = tft.data_pins[0] 
XR_PIN = tft.cs_pin
RD_PIN = tft.rd_pin
'''
# Plan B (not work with pico-uno)
YU_PIN = tft.wr_pin 
XL_PIN = tft.dc_pin
YD_PIN = tft.data_pins[7] 
XR_PIN = tft.data_pins[6]
RD_PIN = tft.rd_pin
'''
SCREEN_WIDTH  = tft.width
SCREEN_HEIGHT = tft.height

cbox = 40
if tft.display_model in ( 0x9486, 0x9488 ):
    cbox = cbox * 4 // 3
    
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
    tft.fill(COLOR_BLACK) 
    tft.fill_rect(0       , 0, cbox, cbox, COLOR_BLUE)
    tft.fill_rect(cbox    , 0, cbox, cbox, COLOR_RED)
    tft.fill_rect(cbox * 2, 0, cbox, cbox, COLOR_GREEN)
    tft.fill_rect(cbox * 3, 0, cbox, cbox, COLOR_MAGENTA)
    tft.fill_rect(cbox * 4, 0, cbox, cbox, COLOR_YELLOW)
    tft.fill_rect(cbox * 5, 0, cbox, cbox, COLOR_BLACK)

    
clearDisplay()

ADC_TYPE = 0
if tft.controller_name == 'RP2':
    ADC_TYPE = 1
    
rts = ResistiveTouchScreen(YU_PIN, XL_PIN, YD_PIN, XR_PIN, RD_PIN,
                           SCREEN_WIDTH, SCREEN_HEIGHT, ADC_TYPE )

current_color = COLOR_WHITE

while True:
    x, y = rts.listening(5) 
            
    if y <= cbox:
        if 0 <= x < cbox:
            current_color = COLOR_BLUE
        elif cbox <= x < cbox * 2:
            current_color = COLOR_RED
        elif cbox * 2 <= x < cbox * 3:
            current_color = COLOR_GREEN
        elif cbox * 3 <= x < cbox * 4:
            current_color = COLOR_MAGENTA
        elif cbox * 4 <= x < cbox * 5:
            current_color = COLOR_YELLOW
        else:
            clearDisplay()
            time.sleep_ms(500)
    else:
        tft.fill_circle(x, y, 4, current_color)
