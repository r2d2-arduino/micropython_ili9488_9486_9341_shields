from ili9xxx_8b_fb import ILI9XXX_8B_FB
from time import ticks_ms

# Set pins here or choose one of the sets
# tft = ILI9XXX_8B_DIRECT( data_pins [D0,D1,...D7], cs, dc, wr, rd, rst )

controller = ILI9XXX_8B_FB.read_controller_name()
if controller == 'ESP32':
    tft = ILI9XXX_8B_FB( [12, 13, 26, 25, 17, 16, 27, 14], 32, 15,  4,  2, 33 )
elif controller == 'RP2':
    tft = ILI9XXX_8B_FB( [8, 9, 2, 3, 4, 5, 6, 7], 29, 28, 27, 26, 24 )
elif controller == 'ESP32-S3':
    tft = ILI9XXX_8B_FB( [9, 8, 18, 17, 15, 16, 3, 14],  6,  7,  1,  2, 5 )
else:
    print("Unknown controller!")

print( tft.controller_name, "display:", hex(tft.display_model),  tft.width, "x", tft.height )

def file_exists(filename):
    import os
    try:
        os.stat(filename)
        return True
    except OSError:
        print("File not found:", filename)
        return False

tft.set_rotation(0)  # 0..3 - Rotates the screen
tft.fill(0x0000) # Fill the screen with black color


filename = 'resources/road240x320.raw'
isize = [240, 320]

if tft.display_model in (0x9486, 0x9488):
    filename = 'resources/rock320x480.raw'
    isize = [320, 480]
    
if file_exists(filename):

    start = ticks_ms()

    tft.draw_raw_image(filename, 0, 0, isize[0], isize[1])
    tft.show()
    print(ticks_ms()-start, 'ms')

#s3m8 big 315 ms
#s3m8 sma 215
#pico sma 95