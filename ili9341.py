"""
ILI9341 display-shield v 0.2.6

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


class ILI9341(ILI9XXX_8B):
    
    def __init__( self, data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin, pixel_format = 16, width = 240, height = 320 ):
        """ Constructor
        Args
        data_pins (list): List of data bus pin numbers (D0, D1, ..., D7), example: [12, 13, 26, 25, 17, 16, 27, 14]
        cs_pin  (int): CS pin number (Chip Select)
        dc_pin  (int): DC pin number (command/parameter mode)
        wr_pin  (int): WR pin number (Write data signal)
        rd_pin  (int): RD pin number (Read data signal)
        rst_pin (int): RST pin number (Reset)
        pixel_format (int): Pixel format in bits: 16 or 18
        width   (int): Screen width in pixels (less)
        height  (int): Screen height in pixels
        """
        
        super().__init__(data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin, CONTROLLER, pixel_format, width, height)
        
    def init_display(self):
        self.reset()
        
        self.write_command(0x28)  # Display OFF

        # Power Control A
        self.write_command(0xCB)
        self.write_multy_data([0x39, 0x2C, 0x00, 0x34, 0x02])

        # Power Control B
        self.write_command(0xCF)
        self.write_multy_data([0x00, 0xC1, 0x30])

        # Driver timing control A
        self.write_command(0xE8)
        self.write_multy_data([0x85, 0x00, 0x78])

        # Driver timing control B
        self.write_command(0xEA)
        self.write_multy_data([0x00, 0x00])

        # Power on sequence control
        self.write_command(0xED)
        self.write_multy_data([0x64, 0x03, 0x12, 0x81])

        # Pump ratio control
        self.write_command(0xF7)
        self.write_data(0x20)

        # Power Control 1
        self.write_command(0xC0)
        self.write_data(0x23)

        # Power Control 2
        self.write_command(0xC1)
        self.write_data(0x10)

        # VCOM Control 1
        self.write_command(0xC5)
        self.write_multy_data([0x3E, 0x28])

        # VCOM Control 2
        self.write_command(0xC7)
        self.write_data(0x86)

        # Memory Access Control
        self.write_command(0x36)
        self.write_data(0x48)  # MADCTL: BGR

        # Pixel Format Set
        self.write_command(0x3A)
        self.write_data(self.pixel_format) 

        # Frame Rate Control
        self.write_command(0xB1)
        self.write_multy_data([0x00, 0x18])

        # Display Function Control
        self.write_command(0xB6)
        self.write_multy_data([0x08, 0x82, 0x27])

        # Enable 3G
        self.write_command(0xF2)
        self.write_data(0x00)

        # Gamma Set
        self.write_command(0x26)
        self.write_data(0x01)
        #self.write_data(0x02)

        # Positive Gamma Correction
        self.write_command(0xE0)
        self.write_multy_data([0x0F, 0x31, 0x2B, 0x0C, 0x0E, 0x08, 0x4E, 0xF1, 0x37, 0x07, 0x10, 0x03, 0x0E, 0x09, 0x00])

        # Negative Gamma Correction
        self.write_command(0xE1)
        self.write_multy_data([0x00, 0x0E, 0x14, 0x03, 0x11, 0x07, 0x31, 0xC1, 0x48, 0x08, 0x0F, 0x0C, 0x31, 0x36, 0x0F])

        # Display ON
        self.write_command(0x11)  # Sleep OUT
        sleep_ms(120)
        self.write_command(0x29)  # Display ON
        
    def set_rotation(self, rotation = 0):
        """
        Set orientation of Display
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
