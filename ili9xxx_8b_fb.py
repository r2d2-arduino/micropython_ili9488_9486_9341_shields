"""
ILI9XXX_8B_FB display-shield v 0.2.2

Displays: ILI9341, ILI9486, ILI9488
Connection: 8-bit Data Bus
Colors: 16-bit, 18-bit, 24-bit
Controllers: Esp32, Esp32-S3, Raspberry Pi Pico
DRAW: Framebuffer

Project path: https://github.com/r2d2-arduino/micropython_ili9488_9486_9341_shields
MIT License

Author: Arthur Derkach 
"""
from ili9xxx_8b import ILI9XXX_8B
from tft_draw.draw_fb_c16 import DRAW_FB_C16 as DRAW_FB
from time import sleep_ms

class ILI9XXX_8B_FB( ILI9XXX_8B, DRAW_FB ):
    
    def __init__( self, data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin,
                  width = 0, height = 0, display_model = 0 ):
        """ Constructor
        Args
        data_pins (list): List of data bus pin numbers (D0, D1, ..., D7), example: [12, 13, 26, 25, 17, 16, 27, 14]
        cs_pin  (int): CS pin number (Chip Select)
        dc_pin  (int): DC pin number (command/parameter mode)
        wr_pin  (int): WR pin number (Write data signal)
        rd_pin  (int): RD pin number (Read data signal)
        rst_pin (int): RST pin number (Reset)
        width   (int): Screen width in pixels (less)
        height  (int): Screen height in pixels
        display_model (hex): 0x9341, 0x9486 or 0x9488     
        """

        super().__init__( data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin,
                         width, height, DRAW_FB.BITS_PER_PIXEL, display_model )

        DRAW_FB.__init__( self, self.width, self.height )
   
    @micropython.viper
    def show(self):
        ''' Displays the contents of the buffer on the screen '''
        self.update_byte2gpio()
        
        self.set_window(0, 0, int(self.width) - 1, int(self.height) - 1)
        
        wr_bit     = int(self.wr_bit)

        buffsize   = int(self.buffsize)
        buffer     = ptr8(self.buffer) 
        byte2gpio  = ptr32(self.BYTE2GPIO)   
        GPIO_OUT   = ptr32(self.GPIO_OUT_REG)
        GPIO_OUT_S = ptr32(self.GPIO_OUT_SET)
        
        buffsize = buffsize // 2
        
        pos = 0
        while pos < buffsize:
            GPIO_OUT[0] = byte2gpio[ buffer[ pos * 2  ] ]
            GPIO_OUT_S[0] = wr_bit
            
            GPIO_OUT[0] = byte2gpio[ buffer[ pos * 2 + 1 ] ]
            GPIO_OUT_S[0] = wr_bit
            pos += 1             
        
        self.cs.value(1)