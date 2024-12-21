"""
ILI9486 display-shield v 0.2.6

Connection: 8-bit Data Bus
Colors: 16-bits, 18-bits
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

class ILI9486(ILI9XXX_8B):
    
    def __init__( self, data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin, pixel_format = 16, width = 320, height = 480 ):
        """ Constructor
        Args
        width   (int): Screen width
        height  (int): Screen height
        """
        super().__init__(data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin, CONTROLLER, pixel_format, width, height)
       
    def init_display(self):
        """ Initial display settings """
        self.reset()
        
        self.write_command(0xF2) #?
        self.write_multy_data([0x18, 0xA3, 0x12, 0x02, 0XB2, 0x12, 0xFF, 0x10, 0x00])
        
        self.write_command(0xF8) #?
        self.write_multy_data([0x21, 0x04])
        
        self.write_command(0x13) # Normal Display Mode ON
        
        self.write_command(0x36) # Memory Access Control, BGR Order
        self.write_data(0x08)
            
        self.write_command(0xB4) # Display Inversion Control, 2-dot inversion
        self.write_data(0x02)
        
        self.write_command(0xB6) # Display Function Control, AGND, Normal scan
        self.write_multy_data([0x02, 0x22, 0x3B])
        
        self.write_command(0xC1) # Power Control 2
        self.write_data(0x41)
        
        self.write_command(0xC5) # VCOM Control 1
        self.write_multy_data([0x00, 0x18])
        
        self.write_command(0x3A) # Interface Pixel Format, 16bit
        self.write_data(self.pixel_format)        
        sleep_ms(50)         
        
        self.write_command(0xE0)  # Positive Gamma Correction
        #self.write_multy_data(bytearray([0x1F, 0x25, 0x22, 0x0B, 0x06, 0x0A, 0x4E, 0xC6, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
        #self.write_multy_data(bytearray([0x0F, 0x1F, 0x1C, 0x0C, 0x0F, 0x08, 0x48, 0x98, 0x37, 0x0A, 0x13, 0x04, 0x11, 0x0D, 0x00]))#ucglib
        self.write_multy_data([ 0x0f, 0x24, 0x1c, 0x0a, 0x0f, 0x08, 0x43, 0x88, 0x32, 0x0f, 0x10, 0x06, 0x0f, 0x07, 0x00 ])
        
        self.write_command(0xE1)  # Negative Gamma Correction
        #self.write_multy_data(bytearray([0x1F, 0x3F, 0x3F, 0x0F, 0x1F, 0x0F, 0x46, 0x49, 0x31, 0x05, 0x09, 0x03, 0x1C, 0x1A, 0x00]))
        #self.write_multy_data(bytearray([0x0F, 0x32, 0x2E, 0x0B, 0x0D, 0x05, 0x47, 0x75, 0x37, 0x06, 0x10, 0x03, 0x24, 0x20, 0x00]))#ucglib
        self.write_multy_data([ 0x0F, 0x38, 0x30, 0x09, 0x0f, 0x0f, 0x4e, 0x77, 0x3c, 0x07, 0x10, 0x05, 0x23, 0x1b, 0x00 ])
        
        self.write_command(0x11)  # Sleep OUT
        sleep_ms(120)
        self.write_command(0x29)  # Display ON
        
    def set_rotation(self, rotation = 0):
        """ Set orientation of display
        Params
        rotation (int): 0 = 0 degree, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees
        """
        if rotation > 3 or rotation < 0:
            print("Incorrect rotation value")
            return False
        
        old_rotation = self.rotation
        self.rotation = rotation
        if self.rotation == 0: # 0 deg
            self.memory_access_control(0, 0, 0, 0, 1, 0)
        elif self.rotation == 1: # 90 deg
            self.memory_access_control(0, 1, 1, 0, 1, 0)
        elif self.rotation == 2: # 180 deg
            self.memory_access_control(1, 1, 0, 0, 1, 0)
        elif self.rotation == 3: # 270 deg
            self.memory_access_control(1, 0, 1, 0, 1, 0)
        
        # Change height <-> width for 90 and 270 degrees
        if (( rotation & 1) and not (old_rotation & 1)
            or not ( rotation & 1) and (old_rotation & 1) ):
            height = self.height
            self.height = self.width
            self.width = height        
