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
btn_radius = 30
if tft.display_model in ( 0x9486, 0x9488 ):
    btn_radius = btn_radius * 4 // 3
    
col1 = btn_radius + btn_radius // 2
col2 = btn_radius * 4
col3 = btn_radius * 6 + btn_radius // 2

row1 = btn_radius * 2 + btn_radius // 2
row2 = row1 + btn_radius * 2 + btn_radius // 3
row3 = row2 + btn_radius * 2 + btn_radius // 3
row4 = row3 + btn_radius * 2 + btn_radius // 3

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
tft.draw_rect(10, 0, SCREEN_WIDTH - 20, 40, COLOR_CYAN)


NCONF = [[ col2, row4, "0", col2 - 6, row4 - 10 ],
         [ col1, row1, "1", col1 - 6, row1 - 10 ],
         [ col2, row1, "2", col2 - 6, row1 - 10 ],
         [ col3, row1, "3", col3 - 6, row1 - 10 ],
         [ col1, row2, "4", col1 - 6, row2 - 10 ],
         [ col2, row2, "5", col2 - 6, row2 - 10 ],
         [ col3, row2, "6", col3 - 6, row2 - 10 ],
         [ col1, row3, "7", col1 - 6, row3 - 10 ],
         [ col2, row3, "8", col2 - 6, row3 - 10 ],
         [ col3, row3, "9", col3 - 6, row3 - 10 ],
         [ col1, row4, "#", col1 - 6, row4 - 10 ],
         [ col3, row4, "*", col3 - 6, row4 - 4  ]]

def btn_state(num, state = 0):
    btn_color = COLOR_YELLOW
    if state == 1:
        btn_color = COLOR_CYAN
    
    tft.fill_circle( NCONF[num][0], NCONF[num][1], btn_radius, btn_color)
    tft.draw_text( NCONF[num][2], NCONF[num][3], NCONF[num][4], COLOR_BLACK)
       
        
display_text = ""

def update_display():
    global display_text
    tft.draw_text( display_text, 20, 10, COLOR_GREEN )

def is_point_in_circle(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2

def btn_default():
    for i in range(12):
        btn_state(i, 0)

def btn_click(num, label):
    global display_text
    btn_state(num, 1)
    display_text += label
    update_display()
    time.sleep_ms(200)
    btn_state(num, 0)

btn_default()

ADC_TYPE = 0
if tft.controller_name == 'RP2':
    ADC_TYPE = 1
    
rts = ResistiveTouchScreen(YU_PIN, XL_PIN, YD_PIN, XR_PIN, RD_PIN,
                           SCREEN_WIDTH, SCREEN_HEIGHT, ADC_TYPE)

while True:
    x, y = rts.listening(20)      
    #print(x, y)
    #for btn in NCONF:
    #    if is_point_in_circle(x, y, btn[0], btn[1], btn_radius):
    #        btn_click(int(btn[2]), btn[2]) 
    
    if is_point_in_circle(x, y, col1, row1, btn_radius):
        btn_click(1, "1")
        
    if is_point_in_circle(x, y, col2, row1, btn_radius):
        btn_click(2, "2")       
        
    if is_point_in_circle(x, y, col3, row1, btn_radius):
        btn_click(3, "3")       
        
    if is_point_in_circle(x, y, col1, row2, btn_radius):
        btn_click(4, "4")        
        
    if is_point_in_circle(x, y, col2, row2, btn_radius):
        btn_click(5, "5")       
        
    if is_point_in_circle(x, y, col3, row2, btn_radius):
        btn_click(6, "6")       
        
    if is_point_in_circle(x, y, col1, row3, btn_radius):
        btn_click(7, "7")       
        
    if is_point_in_circle(x, y, col2, row3, btn_radius):
        btn_click(8, "8")       
        
    if is_point_in_circle(x, y, col3, row3, btn_radius):
        btn_click(9, "9")        
        
    if is_point_in_circle(x, y, col1, row4, btn_radius):
        btn_click(10, "#")
        
    if is_point_in_circle(x, y, col2, row4, btn_radius):
        btn_click(0, "0")        
        
    if is_point_in_circle(x, y, col3, row4, btn_radius):
        btn_click(11, "*")
        
    if len(display_text) > 15:
        display_text = ""
        tft.fill_rect(20, 10, SCREEN_WIDTH - 32, 25, COLOR_BLACK)
                