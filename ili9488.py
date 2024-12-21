"""
ILI9488 display-shield v 0.2.6

Connection: 8-bit Data Bus
Colors: 16-bits, 18-bits, 24-bits
Controller: Esp32, Esp32-S3, Raspberry Pi Pico, Esp32-D1R32
 
Project path: https://github.com/r2d2-arduino/micropython_ili9488_9486_9341_shields

Author: Arthur Derkach 
"""
from machine import Pin
from time import sleep_ms

def controller_definition():
    """ Definition of current controller
    Return (string): Controller name """
    from os import uname
    info = uname()
    sysname = info.sysname
    
    controller = 'Undefined'
    if sysname == 'esp32':
        if 'ESP32S3' in info.machine:
            controller = 'ESP32-S3'
        elif 'ESP32C3' in info.machine:
            controller = 'ESP32-C3'
        else:
            controller = 'ESP32'
    elif sysname == 'rp2':
        controller = 'RP2'
        
    return controller
    
CONTROLLER = controller_definition()

if CONTROLLER == 'ESP32': 
    from ili9xxx_d1r32 import ILI9XXX_8B
else:
    from ili9xxx_8b import ILI9XXX_8B 

class ILI9488(ILI9XXX_8B):
    
    def __init__( self, data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin, pixel_format = 16, width = 320, height = 480 ):
        """ Constructor
        Args
        width   (int): Screen width
        height  (int): Screen height
        """
        super().__init__(data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin, CONTROLLER, pixel_format, width, height)

    def init_display(self):
        """ Main settings of display """
        self.reset()
        
        self.write_command(0x13) # Normal Display Mode ON
        
        self.write_command(0xE0)  # Positive Gamma Control
        self.write_multy_data([0x00, 0x03, 0x09, 0x08, 0x16, 0x0A, 0x3F, 0x78, 0x4C, 0x09, 0x0A, 0x08, 0x16, 0x1A, 0x0F])

        self.write_command(0xE1)  # Negative Gamma Control
        self.write_multy_data([0x00, 0x16, 0x19, 0x03, 0x0F, 0x05, 0x32, 0x45, 0x46, 0x04, 0x0E, 0x0D, 0x35, 0x37, 0x0F])

        self.write_command(0xC0)  # Power Control 1
        self.write_multy_data([0x17, 0x15])

        self.write_command(0xC1)  # Power Control 2
        self.write_data(0x41)

        self.write_command(0xC5)  # VCOM Control
        self.write_multy_data([0x00, 0x12, 0x80])
        
        
        self.write_command(0x36)  # Memory Access Control
        self.write_data(0x48)

        #self.write_command(0xB4) # Display Inversion Control, 2-dot inversion
        #self.write_data(0x02)
        
        #self.write_command(0x26)
        #self.write_data(0x01)  # Gamma curve selected        
        
        self.write_command(0x21) # Invert display - On

        self.write_command(0x3A)  # Pixel Format
        self.write_data(self.pixel_format)  
        
        self.write_command(0x11)  # Sleep Out
        sleep_ms(120)

        self.write_command(0x29)  # Display ON

    def set_rotation(self, rotation = 0):
        """ Set orientation of display
        Params
        rotation (int):  0 = 0 degree, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees
        """
        if rotation > 3 or rotation < 0:
            print("Incorrect rotation value")
            return False
        
        old_rotation = self.rotation
        self.rotation = rotation
        
        if self.rotation == 0: # 0 deg
            self.memory_access_control(0, 1, 0, 0, 1, 0)
        elif self.rotation == 1: # 90 deg
            self.memory_access_control(0, 0, 1, 0, 1, 0)
        elif self.rotation == 2: # 180 deg
            self.memory_access_control(1, 0, 0, 0, 1, 0)
        elif self.rotation == 3: # 270 deg
            self.memory_access_control(1, 1, 1, 0, 1, 0)
        
        # Change height <-> width for 90 and 270 degrees
        if (( rotation & 1) and not (old_rotation & 1)
            or not ( rotation & 1) and (old_rotation & 1) ):
            height = self.height
            self.height = self.width
            self.width = height
