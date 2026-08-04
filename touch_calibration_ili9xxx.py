"""
touch_calibration v 0.2.1
"""
from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT  
import resources.font10 as font10
from resist_touch import ResistiveTouchScreen
from time import sleep_ms

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

sq_size = 9
square = [0, 1, 2, 3, 4, 5, 6, 7, 8]

square[0] = [0, 0]
square[1] = [(SCREEN_WIDTH >> 1) - 5, 0]
square[2] = [SCREEN_WIDTH - sq_size, 0]
square[3] = [0, (SCREEN_HEIGHT >> 1) - 5]
square[4] = [(SCREEN_WIDTH >> 1) - 5, (SCREEN_HEIGHT >> 1) - 5]
square[5] = [SCREEN_WIDTH - sq_size, (SCREEN_HEIGHT >> 1) - 5]
square[6] = [0, SCREEN_HEIGHT - sq_size, 5]
square[7] = [(SCREEN_WIDTH >> 1) - sq_size, SCREEN_HEIGHT - sq_size]
square[8] = [SCREEN_WIDTH - sq_size, SCREEN_HEIGHT - sq_size]

targetX = [0, 1, 2, 3, 4, 5, 6, 7, 8]
targetY = [0, 1, 2, 3, 4, 5, 6, 7, 8]

checked_square = 0x00

main_bg = COLOR_BLACK
text_color = COLOR_GREEN

target_color = COLOR_RED
target_bg = COLOR_GREEN

wait_color = COLOR_GRAY
wait_bg = COLOR_WHITE

check_color = COLOR_BLACK
check_bg = COLOR_MAGENTA

x_text = 10
y_text = SCREEN_HEIGHT // 6

def draw_square(square, color, bg):
    tft.fill_rect(square[0], square[1], 9, 9, bg)
    tft.draw_vline(square[0] + 4, square[1], 9, color)
    tft.draw_hline(square[0], square[1] + 4, 9, color)
    
def touch(x, y):
    global checked_square, targetX, targetY, square
    targetX[checked_square] = x
    targetY[checked_square] = y
    
    draw_square(square[checked_square], check_color, check_bg)
    
    checked_square += 1
    if checked_square < 9:
        tft.fill_rect(x_text, y_text, SCREEN_WIDTH - x_text * 2, 18, main_bg)
        tft.draw_text('Touch on green square ' + str(checked_square + 1), x_text, y_text, text_color)
        draw_square(square[checked_square], target_color, target_bg)
    else:
        x_min, x_max, x_dir, y_min, y_max, y_dir = calibrate_touch()
        show_result(x_min, x_max, x_dir, y_min, y_max, y_dir)
        
        rts.X_CALIB = [x_min, x_max, x_dir]
        rts.Y_CALIB = [y_min, y_max, y_dir]
        
        print('Replace the code below in resist_touch.py :')
        print('self.X_CALIB = [' + str(x_min) + ', ' + str(x_max) + ', ' + str(x_dir) + ']')
        print('self.Y_CALIB = [' + str(y_min) + ', ' + str(y_max) + ', ' + str(y_dir) + ']')
        
    sleep_ms(1000)

run_calibration = True

def find_direct(target):
    up    = (target[0] + target[1] + target[2]) // 3
    down  = (target[6] + target[7] + target[8]) // 3
    left  = (target[0] + target[3] + target[6]) // 3
    right = (target[2] + target[5] + target[8]) // 3
    
    maxd = max(up, down, left, right)
    
    if maxd == up:
        return 0
    if maxd == right:
        return 1
    if maxd == down:
        return 2
    if maxd == left:
        return 3
    
def get_min_max(target, direct):
    #print(target)
    if direct == 0: #up
        mint = min(target[6], target[7], target[8])
        maxt = max(target[0], target[1], target[2])
    if direct == 1: #right
        mint = min(target[0], target[3], target[6])
        maxt = max(target[2], target[5], target[8])
    if direct == 2: #down
        mint = min(target[0], target[1], target[2])
        maxt = max(target[6], target[7], target[8])
    if direct == 3: #left
        mint = min(target[2], target[5], target[8])
        maxt = max(target[0], target[3], target[6])
        
    return mint, maxt
        
def calibrate_touch():
    x_dir = find_direct(targetX)
    y_dir = find_direct(targetY)
    
    x_min, x_max = get_min_max(targetX, x_dir)
    y_min, y_max = get_min_max(targetY, y_dir)
    
    return x_min, x_max, x_dir, y_min, y_max, y_dir


def show_result(x_min, x_max, x_dir, y_min, y_max, y_dir):
    global run_calibration
    
    tft.fill_rect(10, y_text, SCREEN_WIDTH - 20, 120, main_bg)
    tft.draw_text('Calibration finished!', x_text, y_text, text_color)
    tft.draw_text('Touch to test', x_text, y_text + 20, text_color)
    tft.draw_text('Replace the code below', x_text, y_text + 60, text_color)
    tft.draw_text('in resist_touch.py :', x_text, y_text + 80, text_color)
    tft.draw_text('self.X_CALIB=[' + str(x_min) + ',' + str(x_max) + ',' + str(x_dir) + ']', x_text, y_text + 100, text_color)
    tft.draw_text('self.Y_CALIB=[' + str(y_min) + ',' + str(y_max) + ',' + str(y_dir) + ']', x_text, y_text + 120, text_color)
    run_calibration = False
    

tft.set_font(font10)
tft.fill(main_bg)
tft.draw_text('Touch on green square 1', x_text, y_text, text_color)

for i in range(9):
    if i == 0:
        draw_square(square[0], target_color, target_bg)
    else:
        draw_square(square[i], wait_color, wait_bg)

ADC_TYPE = 0
if tft.controller_name == 'RP2':
    ADC_TYPE = 1
    
rts = ResistiveTouchScreen( YU_PIN, XL_PIN, YD_PIN, XR_PIN, RD_PIN,
                            SCREEN_WIDTH, SCREEN_HEIGHT, ADC_TYPE )

while run_calibration:
    x, y = rts.read_touch()
    if x > 0 and y > 0:
        touch(x, y)
    sleep_ms(30)
 
while not run_calibration:
    x, y = rts.listening(5)
    print(x, y)
    tft.fill_rect(0, SCREEN_HEIGHT  * 3 // 4, SCREEN_WIDTH, 20, main_bg)
    tft.draw_text('x = ' + str(x) + ' y = ' + str(y), SCREEN_WIDTH // 4, SCREEN_HEIGHT * 3 // 4 , text_color)


