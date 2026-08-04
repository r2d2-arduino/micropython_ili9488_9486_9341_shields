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
# Plan B
YU_PIN = tft.wr_pin 
XL_PIN = tft.dc_pin
YD_PIN = tft.data_pins[7] 
XR_PIN = tft.data_pins[6]
RD_PIN = tft.rd_pin
'''  
btn_height = 40
btn_width = 90

marg = 20

if tft.display_model in (0x9486, 0x9488):
    btn_height = btn_height * 3 // 2
    btn_width = btn_width * 3 // 2
    marg = marg * 3 // 2
    
row1 = 20
row2 = btn_height + 50
row3 = btn_height * 2 + 80

col1 = 20
col2 = btn_width + 40

messc = [40, 268]
succc = [40, 290]

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

tft.fill(COLOR_BLACK) # Black screen

def button(label, x, y, width, height, color, bg, state = 0):
    sh = 2
    
    if state == 0:
        tft.fill_rect(x, y, width, height, color)           
        tft.fill_rect(x + 1, y + height + 1, width + sh, sh, COLOR_GRAY) # __
        tft.fill_rect(x + width + 1, y + 1,  sh, height + sh, COLOR_GRAY) # |

        tft.draw_text(label, x + marg, y + marg // 2, bg)    
    else:
        tft.fill_rect(x + sh, y + sh, width + sh, height + sh, color)
        tft.fill_rect(x, y, width, sh,  COLOR_BLACK)
        tft.fill_rect(x, y, sh, height, COLOR_BLACK)
        tft.draw_text(label, x + marg + sh, y + marg // 2 + sh, bg)
    
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
    tft.fill_rect(succc[0], succc[1], SCREEN_WIDTH - messc[0], 30, COLOR_BLACK)
    tft.draw_text(name + ' clicked!', succc[0] + 5, succc[1] + 5, COLOR_GREEN)
    buttonGen(btn, 1)          
    time.sleep_ms(300)
    buttonGen(btn, 0)

for i in range(6):
    buttonGen(i, 0)

ADC_TYPE = 0
if tft.controller_name == 'RP2':
    ADC_TYPE = 1

rts = ResistiveTouchScreen(YU_PIN, XL_PIN, YD_PIN, XR_PIN, RD_PIN,
                           SCREEN_WIDTH, SCREEN_HEIGHT, ADC_TYPE)

while True:
    x, y = rts.listening(30)       
    
    tft.fill_rect(messc[0], messc[1], SCREEN_WIDTH - messc[0], 30, COLOR_BLACK) # clear test field
    tft.draw_text('X = ' + str(x) + '  Y = ' + str(y), messc[0] + 5, messc[1] + 5, COLOR_GREEN)
    
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
    else:
        tft.fill_rect(succc[0], succc[1], SCREEN_WIDTH - messc[0], 30, COLOR_BLACK)
        tft.draw_text('Miss', succc[0] + 5, succc[1] + 5, COLOR_YELLOW)



