from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT
from time import ticks_ms

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

tft.set_rotation(2) # Rotates the screen 180 degrees
tft.fill( 0 ) # Fill the screen with black color
tft.set_buffer_multiply(1) # Speed up image loading, but needs more memory

def file_exists(filename):
    import os
    try:
        os.stat(filename)
        return True
    except OSError:
        print("File not found:", filename)
        return False

filename = 'resources/grass240x320.bmp'
if tft.display_model in (0x9486, 0x9488):
    filename = 'resources/road320x480.bmp'    

if file_exists(filename):
    start = ticks_ms()

    tft.draw_bmp(filename, 0, 0)

    print(ticks_ms()-start, 'ms')

#s3m8  big 452 ms
#esp32 big 536
#pico  big 302