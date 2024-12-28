"""
ILI9XXX_8B display-shield v 0.2.7

Displays: ILI9341, ILI9486, ILI9488
Connection: 8-bit Data Bus
Colors: 16-bit, 18-bit, 24-bit
Controllers: Esp32, Esp32-S3, Raspberry Pi Pico
 
Project path: https://github.com/r2d2-arduino/micropython_ili9488_9486_9341_shields

Author: Arthur Derkach 
"""
from machine import Pin
from time import sleep_ms

class ILI9XXX_8B():
    
    def __init__(self, data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin, controller='ESP32', pixel_format=16, width=320, height=480):
        """ Constructor
        Args
        data_pins (list): List of data bus pin numbers (D0, D1, ..., D7), example: [12, 13, 26, 25, 17, 16, 27, 14]
        cs_pin  (int): CS pin number (Chip Select)
        dc_pin  (int): DC pin number (command/parameter mode)
        wr_pin  (int): WR pin number (Write data signal)
        rd_pin  (int): RD pin number (Read data signal)
        rst_pin (int): RST pin number (Reset)
        controller (string): Controller name: ESP32, ESP32-S3, ESP32-C3, RP2
        pixel_format (int): Pixel format in bits: 16, 18 or 24
        width   (int): Screen width in pixels (less)
        height  (int): Screen height in pixels
        """        

        self.data_pins = data_pins
        self.db0 = Pin(data_pins[0], Pin.OUT, value = 0)
        self.db1 = Pin(data_pins[1], Pin.OUT, value = 0)
        self.db2 = Pin(data_pins[2], Pin.OUT, value = 0)
        self.db3 = Pin(data_pins[3], Pin.OUT, value = 0)
        self.db4 = Pin(data_pins[4], Pin.OUT, value = 0)
        self.db5 = Pin(data_pins[5], Pin.OUT, value = 0)
        self.db6 = Pin(data_pins[6], Pin.OUT, value = 0)
        self.db7 = Pin(data_pins[7], Pin.OUT, value = 0)
               
        self.cs = Pin(cs_pin, Pin.OUT, value = 1)
        self.dc = Pin(dc_pin, Pin.OUT, value = 1)
        self.wr = Pin(wr_pin, Pin.OUT, value = 0)
        self.rst= Pin(rst_pin,Pin.OUT, value = 1)
        self.rd = Pin(rd_pin, Pin.OUT, value = 1)
        
        self.width  = width
        self.height = height
        
        if pixel_format == 24:
            self.pixel_format = 0x77
        elif pixel_format == 18:
            self.pixel_format = 0x66
        else: # pixel_format == 16:
            self.pixel_format = 0x55
            
        self.rotation = 0
        
        self.font = None
        
        self.wr_bit = 1 << wr_pin
        self.dc_bit = 1 << dc_pin
        self.cs_bit = 1 << cs_pin
        
        if controller in ('ESP32-S3', 'ESP32-C3'): 
            self.GPIO_OUT_REG  = 0x60004004 # 00-31 pin-output registers
            self.GPIO_OUT_SET  = 0x60004008 # + bit
        elif controller == 'RP2': #Raspberry Pi Pico
            self.GPIO_OUT_REG = 0xD0000010 
            self.GPIO_OUT_SET = 0xD0000014            
        else: # ESP32
            self.GPIO_OUT_REG = 0x3FF44004 
            self.GPIO_OUT_SET = 0x3FF44008 
        
        self.BYTE2GPIO = self.generate_byte2gpio()

        self.init_display()
        
    def reinit_pins(self):
        """ Reinit most important pins.
        Most often used in combination with another devices. 
        """
        self.cs.init(Pin.OUT,  value = 1)
        self.dc.init(Pin.OUT,  value = 1)
        self.wr.init(Pin.OUT,  value = 0)
        self.rst.init(Pin.OUT, value = 1)
        self.rd.init(Pin.OUT,  value = 1)
        
    def reset(self):
        """ Resets display settings to default. """        
        self.rst.value(0) 
        sleep_ms(10)   
        self.rst.value(1) 
        sleep_ms(120)    
        self.write_command(0x01)  # Software Reset
        sleep_ms(120)        

    def write_command(self, cmd):
        """ Sending a command to the display
        Args
        cmd (int): Command number, example: 0x2E
        """
        self.cs.value(0)  # Selecting a device
        self.dc.value(0)  # Command Mode
        self.set_data_pins(cmd)
        self.wr.off()
        self.wr.on()        
        self.cs.value(1)  # Deselect device
        
    def write_data(self, data):
        """ Sending data to the display
        Args
        data (int): Data byte, example: 0xF8
        """        
        self.cs.value(0)  # Selecting a device
        self.dc.value(1)  # Data mode
        self.set_data_pins(data)
        self.wr.off()
        self.wr.on()         
        self.cs.value(1)  # Deselect device
        
    def write_multy_data(self, multy_data):
        """ Sending array of data bytes to the display
        Params
        multy_data (bytearray): Data array, example: bytearray([0x18, 0xA3, 0x2E])
        """
        self.cs.value(0)  # Selecting a device
        self.dc.value(1)  # Data mode        
        for data in multy_data:
            self.set_data_pins(data)
            self.wr.off()
            self.wr.on()  
        self.cs.value(1)  # Deselect device
                
    @micropython.viper
    def set_data_pins(self, value : int):        
        self.db0.value(value & 1)
        self.db1.value((value >> 1) & 1)
        self.db2.value((value >> 2) & 1)
        self.db3.value((value >> 3) & 1)
        self.db4.value((value >> 4) & 1)
        self.db5.value((value >> 5) & 1)
        self.db6.value((value >> 6) & 1)
        self.db7.value((value >> 7) & 1)
        
    def generate_byte2gpio(self):
        """ Generate to memory all 256 states of data gpio
        Return (bytearray): All 256 x 32-bit states """
        
        self.cs.value(0)
        self.dc.value(1)
        self.wr.value(0)
        self.set_data_pins(0)

        empty_mask = self.current_gpio_state()
        self.cs.value(1)
        
        # Current GPIO values ​​excluding mask related bits
        byte2gpio32 = bytearray()

        for byte in range(256):
            gpio = self.convert_byte2gpio(byte) | empty_mask
            gpio4 = gpio.to_bytes( 4, 'little' )
            for i in range(4):
                byte2gpio32.append(gpio4[i])
                
        return byte2gpio32
                
    @micropython.viper
    def convert_byte2gpio(self, byte: int) -> int:
        """
        Convert byte to gpio setting
        Params
        byte (int): Byte, example 0x27
        Return (int): gpio state, example 234889216 = '0b1110000000000010000000000000'
        """
        dpins = self.data_pins
        bit_pins = ((byte & 1) << int(dpins[0]))
        bit_pins |= (((byte >> 1) & 1) << int(dpins[1]))
        bit_pins |= (((byte >> 2) & 1) << int(dpins[2]))
        bit_pins |= (((byte >> 3) & 1) << int(dpins[3]))
        bit_pins |= (((byte >> 4) & 1) << int(dpins[4]))
        bit_pins |= (((byte >> 5) & 1) << int(dpins[5]))
        bit_pins |= (((byte >> 6) & 1) << int(dpins[6]))
        bit_pins |= (((byte >> 7) & 1) << int(dpins[7]))
        return bit_pins
    
    @micropython.viper
    def current_gpio_state(self)->int:
        """ Current state of gpio registers
            Return (int): 32-bit state """
        GPIO_OUT = ptr32(self.GPIO_OUT_REG)
        return GPIO_OUT[0]    

    def memory_access_control(self, my = 0, mx = 0, mv = 0, ml = 0, bgr = 0, mh = 0):
        """ MADCTL. This command defines read/write scanning direction of frame memory. """
        self.write_command(0x36)
        data =  0
        data += mh << 2 # Horizontal order
        data += bgr<< 3 # RGB-BGR Order: 0 - RGB, 1 - BGR
        data += ml << 4 # Vertical refresh order
        data += mv << 5 # Row/Column exchange
        data += mx << 6 # Column address order
        data += my << 7 # Row address order
        #print(data)
        self.write_data(data)

    def init_display(self):
        """ Initial display settings """
        self.reset()
        
        self.write_command(0x28)  # Display OFF

        # Memory Access Control
        self.write_command(0x36)
        self.write_data(0x48)  # MADCTL: BGR

        # Pixel Format Set
        self.write_command(0x3A)
        self.write_data(self.pixel_format) 

        # Display ON
        self.write_command(0x11)  # Sleep OUT
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

    def invert_display(self, on = True):
        """ Enables or disables color inversion on the display.
        Args
        on (bool): True = Enable inversion, False = Disable inversion
        """
        if on:
            self.write_command(0x21)  
        else:
            self.write_command(0x20)

    def idle_mode(self, on = True):
        """ Enables or disables idle mode on the display.
        Args
        on (bool): True = Enable idle mode, False = Disable idle mode
        """
        if on:
            self.write_command(0x39)
        else:
            self.write_command(0x38)

    def set_adaptive_brightness(self, mode = 0):
        """ Set adaptive brightness
        Args
        mode (int):
            0 - CABC OFF
            1 - User Interface Image
            2 - Still Picture
            3 - Moving Image
        """
        if 0 <= mode < 4:
            self.write_command(0x55)
            self.write_data(mode)
            
        else:
            print('Error value in def set_adaptive_brightness')
            
    def vert_scroll(self, top_fix: int, scroll_height: int, bot_fix: int):
        """ Vertical scroll settings
        Args
        top_fix (int): Top fixed rows
        scroll_height (int): Scrolling height rows
        bot_fix (int): Bottom fixed rows
        
        top_fix + bot_fix + scroll_height - must be  equal height of screen
        """
        screen_height = self.height
        if self.rotation & 1:
            screen_height = self.width
            
        sum = top_fix + bot_fix + scroll_height
        
        if sum == screen_height:
            self.write_command(0x33)
            #Top fixed rows
            self.write_data((top_fix >> 8) & 0xFF)
            self.write_data(top_fix & 0xFF)
            #Scrolling height rows
            self.write_data((scroll_height >> 8) & 0xFF)
            self.write_data(scroll_height & 0xFF)
            #Bottom fixed rows
            self.write_data((bot_fix >> 8) & 0xFF)
            self.write_data(bot_fix & 0xFF)
            
        else:
            print('Incorrect sum in vertical scroll ', sum, ' <> ', screen_height)
            
    def vert_scroll_start_address(self, start = 0):
        """ Set vertical scroll start address, and run scrolling
        Args
        start (int): start row        
        """
        self.write_command(0x37)
        self.write_data((start >> 8) & 0xFF)
        self.write_data(start & 0xFF)
        
    def scroll(self, delay = 5):
        """ Scrolling on the screen at a given speed.
        Args
        delay (int): Delay between scrolling actions
        """
        height = self.height
        if self.rotation & 1:
            height = self.width
            
        for y in range(height):
            self.vert_scroll_start_address(y + 1)
            sleep_ms(delay)        
        
    def tearing_effect(self, on = True):
        """ Activate "Tearing effect"
        Args
        on (bool): True = Enable effect, False = Disable effect
        """        
        if on:
            self.write_command(0x35)
        else:
            self.write_command(0x34)
            
    """
    *** Draw area ***
    """

    @micropython.viper
    def set_window(self, x0:int, y0:int, x1:int, y1:int):
        """ Sets the starting position and the area of drawing on the display
        Args
        x0 (int): Start X position  ________
        y0 (int): Start Y position  |s---> |
        x1 (int): End X position    ||     |    
        y1 (int): End Y position    |v____e|  
        """
        dc_bit = int(self.dc_bit)
        wr_bit = int(self.wr_bit)
        
        byte2gpio = ptr32(self.BYTE2GPIO)   
        
        #Getting pointers to registers
        GPIO_OUT   = ptr32(self.GPIO_OUT_REG)  # 0 - 31  pins
        GPIO_OUT_S = ptr32(self.GPIO_OUT_SET) # + bit

        # Column address sending        
        GPIO_OUT[0] = byte2gpio[0x2A] - dc_bit
        GPIO_OUT_S[0] = wr_bit
        
        # Sending Start and End X coordinates       
        GPIO_OUT[0] = byte2gpio[(x0 >> 8) & 0xFF] # x hi 
        GPIO_OUT_S[0] = wr_bit        
        GPIO_OUT[0] = byte2gpio[x0 & 0xFF] # x low
        GPIO_OUT_S[0] = wr_bit
        
        GPIO_OUT[0] = byte2gpio[(x1 >> 8) & 0xFF] # x end hi 
        GPIO_OUT_S[0] = wr_bit
        GPIO_OUT[0] = byte2gpio[x1 & 0xFF] # x end low  
        GPIO_OUT_S[0] = wr_bit

        # Page address sending
        GPIO_OUT[0] = byte2gpio[0x2B] - dc_bit       
        GPIO_OUT_S[0] = wr_bit
        
        # Sending Start and End Y coordinates       
        GPIO_OUT[0] = byte2gpio[(y0 >> 8) & 0xFF] # y hi 
        GPIO_OUT_S[0] = wr_bit
        GPIO_OUT[0] = byte2gpio[y0 & 0xFF] # y low 
        GPIO_OUT_S[0] = wr_bit
        
        GPIO_OUT[0] = byte2gpio[(y1 >> 8) & 0xFF] # y end hi 
        GPIO_OUT_S[0] = wr_bit
        GPIO_OUT[0] = byte2gpio[y1 & 0xFF] # y end low 
        GPIO_OUT_S[0] = wr_bit

        # Memory write for addresses
        GPIO_OUT[0] = byte2gpio[0x2C] - dc_bit        
        GPIO_OUT_S[0] = wr_bit
     

    @micropython.viper
    def draw_pixel(self, x:int, y:int, color: int):
        """ Draw one pixel on display
        Args
        x (int): X position on dispaly, example 100
        y (int): Y position on dispaly, example 200
        color (int): RGB color
        """
        # Gpio preparation
        byte2gpio = ptr32(self.BYTE2GPIO)
        
      
        #coordinats
        x_hi  = byte2gpio[(x >> 8) & 0xFF]
        x_low = byte2gpio[x & 0xFF]
        y_hi  = byte2gpio[(y >> 8) & 0xFF]
        y_low = byte2gpio[y & 0xFF]
        
        #cs_bit = int(self.cs_bit)
        dc_bit = int(self.dc_bit)
        wr_bit = int(self.wr_bit)
        pxlf   = int(self.pixel_format)
        
        #Getting pointers to registers
        GPIO_OUT   = ptr32(self.GPIO_OUT_REG)  # 0 - 31  pins
        GPIO_OUT_S = ptr32(self.GPIO_OUT_SET) # + bit

        # Column address sending        
        GPIO_OUT[0] = byte2gpio[0x2A] - dc_bit
        GPIO_OUT_S[0] = wr_bit
        
        # Sending Start and End X coordinates       
        GPIO_OUT[0] = x_hi 
        GPIO_OUT_S[0] = wr_bit        
        GPIO_OUT[0] = x_low
        GPIO_OUT_S[0] = wr_bit
        
        GPIO_OUT[0] = x_hi
        GPIO_OUT_S[0] = wr_bit
        GPIO_OUT[0] = x_low
        GPIO_OUT_S[0] = wr_bit

        # Page address sending
        GPIO_OUT[0] = byte2gpio[0x2B] - dc_bit
        GPIO_OUT_S[0] = wr_bit
        
        # Sending Start and End Y coordinates       
        GPIO_OUT[0] = y_hi
        GPIO_OUT_S[0] = wr_bit
        GPIO_OUT[0] = y_low
        GPIO_OUT_S[0] = wr_bit
        
        GPIO_OUT[0] = y_hi
        GPIO_OUT_S[0] = wr_bit
        GPIO_OUT[0] = y_low
        GPIO_OUT_S[0] = wr_bit

        # Memory write for addresses
        GPIO_OUT[0] = byte2gpio[0x2C] - dc_bit
        GPIO_OUT_S[0] = wr_bit
        
        # Sending Color data
        if pxlf == 0x55: # 16 bit
            GPIO_OUT[0] = byte2gpio[(color >> 8) & 0xFF] # color hi
            GPIO_OUT_S[0] = wr_bit
            GPIO_OUT[0] = byte2gpio[color & 0xFF] # color low
            GPIO_OUT_S[0] = wr_bit
        elif pxlf == 0x66: # 18 bit
            GPIO_OUT[0] = byte2gpio[(color >> 10) & 0xFF ] # red
            GPIO_OUT_S[0] = wr_bit
            GPIO_OUT[0] = byte2gpio[(color >> 2) & 0xFF ] # green
            GPIO_OUT_S[0] = wr_bit
            GPIO_OUT[0] = byte2gpio[(color << 4) & 0xF0] # blue
            GPIO_OUT_S[0] = wr_bit 
        else: # PIXEL_FORMAT == 0x77: # 24 bit
            GPIO_OUT[0] = byte2gpio[(color >> 16) & 0xFF ] # red
            GPIO_OUT_S[0] = wr_bit
            GPIO_OUT[0] = byte2gpio[(color >> 8) & 0xFF ] # green
            GPIO_OUT_S[0] = wr_bit
            GPIO_OUT[0] = byte2gpio[color & 0xFF] # blue
            GPIO_OUT_S[0] = wr_bit              
        
        GPIO_OUT_S[0] = int(self.cs_bit) # CS = 1 - Device Off

    def draw_line(self, x0, y0, x1, y1, color):
        """ Draw line using Bresenham's Algorithm
        Args
        x0 (int): Start X position   s
        y0 (int): Start Y position    \
        x1 (int): End X position       \ 
        y1 (int): End Y position        e
        color (int): RGB color
        """
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            
            self.draw_pixel(x0, y0, color)
            
            if x0 == x1 and y0 == y1:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
                
                
    def draw_vline(self, x, y, height, color, thickness = 1):
        """ Draw vertical line
        Args
        x (int): Start X position      xy
        y (int): Start Y position     h |   
        height (int): Height of line    v   
        color (int): RGB color
        thickness (int): thickness of line
        """        
        self.fill_rect(x, y, thickness, height, color)


    def draw_hline(self, x, y, width, color, thickness = 1):
        """ Draw horizontal line 
        Args
        x (int): Start X position          xy----->
        y (int): Start Y position              w
        width (int): Width of line            
        color (int): RGB color
        thickness (int): thickness of line
        """         
        self.fill_rect(x, y, width, thickness, color)

    
    def draw_rect(self, x, y, width, height, color, thickness = 1):
        """ Draw rectangle 
        Args  
        x (int): Start X position          xy----->
        y (int): Start Y position          |   w  .
        height (int): Height of line    h  |      .
        width (int): Width of square       v.......  
        thickness (int): thickness of line   
        color (int): RGB color
        """         
        self.fill_rect(x, y, width, thickness, color)
        self.fill_rect(x , y + thickness, thickness, height, color)
        self.fill_rect(x + thickness, y + height, width, thickness, color)        
        self.fill_rect(x + width, y, thickness, height, color)

    @micropython.viper
    def fill_rect(self, x:int, y:int, x_len:int, y_len:int, color:int):
        """ Draw filled rectangle
        Args
        x (int): Start X position          xy----->
        y (int): Start Y position          |   w  .
        x_len (int): Width of rectangle  h |      .
        y_len (int): Height of rectangle   v.......
        color (int): RGB color
        """
        wr_bit = int(self.wr_bit)
        pxlf   = int(self.pixel_format)
        
        byte2gpio = ptr32(self.BYTE2GPIO)     
        #Getting pointers to registers
        GPIO_OUT   = ptr32(self.GPIO_OUT_REG)  # 0 - 31  pins
        GPIO_OUT_S = ptr32(self.GPIO_OUT_SET) # + bit
        
        self.set_window(x, y, x + x_len - 1, y + y_len - 1) # Setting draw area
        
        amount = x_len * y_len # amount of pixels

        if pxlf == 0x55: # 16 bit
            color_hi  = byte2gpio[(color >> 8) & 0xFF] 
            color_low = byte2gpio[color & 0xFF] 

            while amount > 0:
                GPIO_OUT[0] = color_hi
                GPIO_OUT_S[0] = wr_bit
                GPIO_OUT[0] = color_low
                GPIO_OUT_S[0] = wr_bit

                amount -= 1
        elif pxlf == 0x66: # 18 bit
            gpio1 = byte2gpio[ (color >> 10) & 0xFF ] 
            gpio2 = byte2gpio[ (color >> 2) & 0xFF ]  
            gpio3 = byte2gpio[ (color << 4) & 0xF0 ]   
        
            while amount > 0:
                GPIO_OUT[0] = gpio1
                GPIO_OUT_S[0] = wr_bit
                GPIO_OUT[0] = gpio2
                GPIO_OUT_S[0] = wr_bit
                GPIO_OUT[0] = gpio3
                GPIO_OUT_S[0] = wr_bit            
                amount -= 1
        else: # PIXEL_FORMAT == 0x77: # 24 bit
            color_r = byte2gpio[(color >> 16) & 0xFF ] 
            color_g = byte2gpio[(color >> 8) & 0xFF ]  
            color_b = byte2gpio[color & 0xFF]    
        
            while amount > 0:
                GPIO_OUT[0] = color_r
                GPIO_OUT_S[0] = wr_bit
                GPIO_OUT[0] = color_g
                GPIO_OUT_S[0] = wr_bit
                GPIO_OUT[0] = color_b
                GPIO_OUT_S[0] = wr_bit            
                amount -= 1
        
        GPIO_OUT_S[0] = int(self.cs_bit) # CS = 1 - Device Off

    def fill_screen(self, color):
        """ Fill whole screen
        Args
        color (int): RGB color
        """
        self.fill_rect(0, 0, self.width, self.height, color)
        
    def draw_circle(self, x, y, radius, color, border = 1):
        """ Draw circle
        Args
        x (int): Start X position          
        y (int): Start Y position              
        radius (int): Radius of circle         
        border (int): border of circle   
        color (int): RGB color
        """
        if (x < 0 or y < 0 or x >= self.width or y >= self.height):
            print("Invalid params in draw_circle")
            return

        for r in range(radius - border, radius):
            # Bresenham algorithm
            x_pos = 0 - r
            y_pos = 0
            err = 2 - 2 * r
            while 1:
                self.draw_pixel(x - x_pos, y + y_pos, color)
                self.draw_pixel(x + x_pos, y + y_pos, color)
                self.draw_pixel(x + x_pos, y - y_pos, color)
                self.draw_pixel(x - x_pos, y - y_pos, color)
                
                e2 = err
                if (e2 <= y_pos):
                    y_pos += 1
                    err += y_pos * 2 + 1
                    if(0-x_pos == y_pos and e2 <= x_pos):
                        e2 = 0
                if (e2 > x_pos):
                    x_pos += 1
                    err += x_pos * 2 + 1
                if x_pos > 0:
                    break    
    
    def fill_circle(self, x, y, radius, color):
        """ Draw filled circle
        Args
        x (int): Start X position          
        y (int): Start Y position              
        radius (int): Radius of circle         
        border (int): border of circle   
        color (int): RGB color
        """
        for p in range(-radius, radius + 1):
            # Calculating the horizontal line
            dx = int( (radius**2 - p**2)**0.5 )  
            self.fill_rect(x - dx, y + p, dx*2, 1, color)
            
    """
    *** Image area ***
    """
    @micropython.viper
    def rgb(self, red :int, green :int, blue :int)->int:
        """ Convert 8,8,8 bits RGB to 16/18/24 bits  """
        pxlf = int(self.pixel_format)
        
        if pxlf == 0x55: # 16-bits
            return ( (red << 11) & 0xF800 | (green << 5) & 0x07E0 | blue & 0x001F )
        
        elif pxlf == 0x66: # 18-bits
            return ( (red << 10) & 0x3F000  | (green << 4) & 0xFC0 | (blue >> 2) & 0x3F )
        
        else: # 0x77 24-bits
            return ( (red << 16) & 0xFF0000 | (green << 8) & 0xFF00 | blue & 0x00FF )
    
    @micropython.viper
    def draw_raw_image(self, filename, x: int, y: int, width: int, height: int):
        """ Draw RAW image (RGB565 format) on display
        Args
        filename (string): filename of image, example: "rain.bmp"
        x (int) : Start X position
        y (int) : Start Y position
        width (int) : Width of raw image
        height (int) : Height of raw image
        """
        wr_bit = int(self.wr_bit)
        pxlf   = int(self.pixel_format)
        
        if pxlf == 0x55:
            f = open(filename, 'rb')
                    
            #Getting pointers to registers
            GPIO_OUT   = ptr32(self.GPIO_OUT_REG) # 0 - 31  pins
            GPIO_OUT_S = ptr32(self.GPIO_OUT_SET)
            byte2gpio  = ptr32(self.BYTE2GPIO) #pointer to byte2gpio converter
                  
            self.set_window(x, y, x + width - 1, y + height - 1) # Set start position
                  
            byte_width = width * 2

            for row in range(height):
                image_data = f.read(byte_width) # read image row
                image_buffer = ptr8(image_data) # get pointer to image row
                
                for pos in range(byte_width):
                    GPIO_OUT[0] = byte2gpio[ image_buffer[ pos ] ]
                    GPIO_OUT_S[0] = wr_bit
                    
            self.cs.value(1)  # Chip disabled
        else:
            print("Supports 16-bit display format only")

    def draw_bmp(self, filename, x = 0, y = 0):
        """ Draw BMP image on display
        Args
        filename (string): filename of image, example: "rain.bmp"
        x (int) : Start X position
        y (int) : Start Y position
        """
        f = open(filename, 'rb')

        if f.read(2) == b'BM':  #header
            dummy    = f.read(8) #file size(4), creator bytes(4)
            offset   = int.from_bytes(f.read(4), 'little')
            dummy    = f.read(4) #hdrsize
            width    = int.from_bytes(f.read(4), 'little')
            height   = int.from_bytes(f.read(4), 'little')
            planes   = int.from_bytes(f.read(2), 'little')
            depth    = int.from_bytes(f.read(2), 'little')
            compress = int.from_bytes(f.read(4), 'little')

            if planes == 1 and depth == 24 and compress == 0: #compress method == uncompressed
                rowsize = (width * 3 + 3) & ~3
                
                if height < 0:
                    height = -height

                frameWidth, frameHeight = width, height
                
                if x + frameWidth > self.width:
                    frameWidth = self.width - x
                    
                if y + frameHeight > self.height:
                    frameHeight = self.height - y
           
                f.seek(offset)
                
                self.set_window(x, y, x + frameWidth - 1, y + frameHeight - 1)
                
                self._send_bmp_to_display(f, frameHeight, frameWidth, offset, rowsize)
         
                self.cs.value(1)
                    
                    
    @micropython.viper           
    def _send_bmp_to_display( self, f, frameHeight: int, frameWidth: int, offset: int, rowsize: int ):
        """ Send bmp-file to display
        Args
        f (object File) : Image file
        frameHeight (int): Height of image frame
        frameWidth (int): Width of image frame
        offset (int): Internal byte offset of image-file
        rowsize (int): Internal byte rowsize of image-file        
        """
        wr_bit = int(self.wr_bit)
        pxlf   = int(self.pixel_format)
                
        GPIO_OUT   = ptr32(self.GPIO_OUT_REG) # Getting pointer to Pin registers
        GPIO_OUT_S = ptr32(self.GPIO_OUT_SET)
        byte2gpio  = ptr32(self.BYTE2GPIO)

        for row in range(frameHeight):
            # Start position of new row in image-file
            pos = offset + row * rowsize
                                    
            if int(f.tell()) != pos:
                f.seek(pos)
            
            # Reading one row from image-file
            bgr_row = f.read(3 * frameWidth)
            image_buffer = ptr8(bgr_row)
            
            if pxlf == 0x55:                
                col = frameWidth
                while col > 0:             
                    #Getting color bytes
                    red   = image_buffer[ col * 3 ]
                    green = image_buffer[ col * 3 + 1 ]
                    blue  = image_buffer[ col * 3 + 2 ]
                    
                    # Sending new bit-masks directly to registers
                    GPIO_OUT[0] = byte2gpio[ (blue & 0xF8 ) | ( green & 0xFC ) >> 5 ] # color hi
                    GPIO_OUT_S[0] = wr_bit
                    GPIO_OUT[0] = byte2gpio[ (green & 0x1C ) << 3 | red >> 3 ] # color low
                    GPIO_OUT_S[0] = wr_bit
                    col -= 1 
            else: # PIXEL_FORMAT == 0x66 & 0x77
                col = frameWidth
                while col > 0:
                    red   = image_buffer[ col * 3 ] 
                    green = image_buffer[ col * 3 + 1 ]  
                    blue  = image_buffer[ col * 3 + 2 ] 

                    GPIO_OUT[0] = byte2gpio[ blue ] 
                    GPIO_OUT_S[0] = wr_bit
                    GPIO_OUT[0] = byte2gpio[ green ] 
                    GPIO_OUT_S[0] = wr_bit
                    GPIO_OUT[0] = byte2gpio[ red ]
                    GPIO_OUT_S[0] = wr_bit               
                    col -= 1 
                
    def draw_bitmap( self, bitmap, x_start, y_start, size, color ):
        """ Draw bitmap
        Args
        bitmap (bytes): Bytes of bitmap
        x_start (int): Start X position
        y_start (int): Start Y position
        color (int): RGB color
        """
        for y, row in enumerate(bitmap):
            for x in range(size):
                if (row >> x) & 1:
                    self.draw_pixel( x_start + x, y_start + y, color )

    @micropython.viper
    def draw_bitmap_fast( self, bitmap, x_start:int, y_start:int, size:int, color:int, bg:int ):
        """ Draw bitmap (fast version)
        Args
        bitmap (bytes): Bytes of bitmap
        x_start (int): Start X position
        y_start (int): Start Y position
        color (int): RGB color
        bg (int): Bacground, RGB color
        """
        wr_bit = int(self.wr_bit)
        pxlf   = int(self.pixel_format)
        
        byte2gpio  = ptr32(self.BYTE2GPIO)
        #Getting pointers to registers
        GPIO_OUT   = ptr32(self.GPIO_OUT_REG) # 0 - 31  pins
        GPIO_OUT_S = ptr32(self.GPIO_OUT_SET) # + bit
        
        self.set_window(x_start, y_start, x_start + size - 1, y_start + size - 1)
        
        # Main & Backrground color masks        
        if pxlf == 0x55: # 16-bit
            color_hi  = byte2gpio[(color >> 8) & 0xFF]
            color_low = byte2gpio[color & 0xFF]
            bg_hi     = byte2gpio[bg >> 8]
            bg_low    = byte2gpio[bg & 0xFF]

            for y in range(size):
                row = int(bitmap[y])
                for x in range(size):
                    if (row >> x) & 1: # main color
                        GPIO_OUT[0] = color_hi
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = color_low
                        GPIO_OUT_S[0] = wr_bit
                    else: # background
                        GPIO_OUT[0] = bg_hi
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = bg_low
                        GPIO_OUT_S[0] = wr_bit
        elif pxlf == 0x66: # 18-bit
            main1 = byte2gpio[ (color >> 10) & 0xFF ] 
            main2 = byte2gpio[ (color >> 2) & 0xFF ]  
            main3 = byte2gpio[ (color << 4) & 0xF0 ]
            
            bg1 = byte2gpio[ (bg >> 10) & 0xFF ] 
            bg2 = byte2gpio[ (bg >> 2) & 0xFF ]  
            bg3 = byte2gpio[ (bg << 4) & 0xF0 ]

            for y in range(size):
                row = int(bitmap[y])
                for x in range(size):
                    if (row >> x) & 1: # main color
                        GPIO_OUT[0] = main1
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = main2
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = main3
                        GPIO_OUT_S[0] = wr_bit                    
                    else: # background
                        GPIO_OUT[0] = bg1
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = bg2
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = bg3
                        GPIO_OUT_S[0] = wr_bit
        else: # PIXEL_FORMAT == 0x77: 24-bit 
            color_r = byte2gpio[(color >> 16) & 0xFF ] 
            color_g = byte2gpio[(color >> 8) & 0xFF ]  
            color_b = byte2gpio[color & 0xFF]
            
            bg_r = byte2gpio[(bg >> 16) & 0xFF ] 
            bg_g = byte2gpio[(bg >> 8) & 0xFF ]  
            bg_b = byte2gpio[bg & 0xFF]

            for y in range(size):
                row = int(bitmap[y])
                for x in range(size):
                    if (row >> x) & 1: # main color
                        GPIO_OUT[0] = color_r
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = color_g
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = color_b
                        GPIO_OUT_S[0] = wr_bit                    
                    else: # background
                        GPIO_OUT[0] = bg_r
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = bg_g
                        GPIO_OUT_S[0] = wr_bit
                        GPIO_OUT[0] = bg_b
                        GPIO_OUT_S[0] = wr_bit 
                    
        GPIO_OUT_S[0] = int(self.cs_bit) # CS = 1 - Device Off
  
    """
    *** Text area ***
    """
    
    def set_font(self, font):
        """ Set font for text
        Args
        font (module): Font module generated by font_to_py.py
        """
        self.font = font
        
    def draw_text(self, text, x, y, color):
        """ Draw text on display
        Args
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        """
        x_start = x
        screen_height = self.height
        screen_width = self.width

        font = self.font        
        if font == None:
            print("Font not set")
            return False
        
        for char in text:
            if char == "\n": # New line
                x = screen_width
                continue
            
            if char == "\t": #replace tab to space
                char = " "
                
            glyph = font.get_ch(char)
            glyph_height = glyph[1]
            glyph_width = glyph[2]
            
            if char == " ": # double size for space
                x += glyph_width
                
            if x + glyph_width > screen_width:
                x = x_start
                y += glyph_height
                
            if y + glyph_height > screen_height: # End of screen
                break                
                
            self._draw_glyph(glyph, x, y, color)
            x += glyph_width              
                
    @micropython.viper
    def _draw_glyph(self, glyph, x:int, y:int, color:int):
        """ Draw one glyph (char) on display
        Args
        glyph (tuple) : Glyph data [data, height, width]
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        """
        data   = ptr8(glyph[0]) #memoryview to glyph
        height = int(glyph[1])
        width  = int(glyph[2])
        
        i = 0
        for h in range(height):
            bit_len = 0                    
            while bit_len < width:
                byte = data[i]
                xpos = bit_len + x
                ypos = h + y
                
                #Drawing pixels when bit = 1
                if (byte >> 7) & 1:
                    self.draw_pixel(xpos + 0, ypos, color)
                if (byte >> 6) & 1:
                    self.draw_pixel(xpos + 1, ypos, color)
                if (byte >> 5) & 1:
                    self.draw_pixel(xpos + 2, ypos, color)
                if (byte >> 4) & 1:
                    self.draw_pixel(xpos + 3, ypos, color)
                if (byte >> 3) & 1:
                    self.draw_pixel(xpos + 4, ypos, color)
                if (byte >> 2) & 1:
                    self.draw_pixel(xpos + 5, ypos, color)
                if (byte >> 1) & 1:
                    self.draw_pixel(xpos + 6, ypos, color)
                if byte & 1:
                    self.draw_pixel(xpos + 7, ypos, color)
                
                bit_len += 8
                i += 1       

    def draw_text_fast(self, text, x, y, color, bg = 0x0000):
        """ Draw text on display (fast version)
        Args
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        bg (int) : Bacground, RGB color
        """        
        x_start = x
        glyph_height = 0
        screen_height = self.height
        screen_width = self.width

        font = self.font        
        if font == None:
            print("Font not set")
            return False
        
        for char in text:
            if char == "\n": # New line
                x = screen_width
                continue
            
            if char == "\t": #replace tab to space
                char = " "                
            
            glyph = font.get_ch(char)
            glyph_height = glyph[1]
            glyph_width = glyph[2]
            
            if x + glyph_width >= screen_width: # End of row
                x = x_start
                y += glyph_height
                
            if y + glyph_height >= screen_height: # End of screen
                break
                
            self._draw_glyph_fast(glyph, x, y, color, bg)
            x += glyph_width
            
            if char == " " and (x + glyph_width) <= screen_width: # double size for space
                self._draw_glyph_fast(glyph, x, y, color, bg)
                x += glyph_width
        self.cs.value(1)
  
    @micropython.viper
    def _draw_glyph_fast(self, glyph, x:int, y:int, color:int, bg: int):
        """ Draw one glyph (char) on display (Fast version)
        Args
        glyph (tuple) : Glyph data [data, height, width]
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        bg (int) : Bacground, RGB color
        """
        glyph_data = ptr8(glyph[0]) #memoryview to glyph
        glyph_height = int(glyph[1]) 
        glyph_width = int(glyph[2])
 
        pxlf   = int(self.pixel_format)
        wr_bit = int(self.wr_bit)        
        
        # Gpio preparation
        byte2gpio = ptr32(self.BYTE2GPIO)
        #Getting pointers to registers
        GPIO_OUT   = ptr32(self.GPIO_OUT_REG) # 0 - 31  pins
        GPIO_OUT_S = ptr32(self.GPIO_OUT_SET) # + bit
        
        self.set_window(x, y, x + glyph_width - 1, y + glyph_height - 1)
        
        # Main & Backrground color masks
        if pxlf == 0x55: # 16-bit
            color_hi   = byte2gpio[(color >> 8) & 0xFF]
            color_low  = byte2gpio[color & 0xFF]
            bg_hi      = byte2gpio[(bg >> 8) & 0xFF]
            bg_low     = byte2gpio[bg & 0xFF]
            # Sending Color data        
            i = 0
            for dots_row in range(glyph_height): # 
                dots_sum = 0                    
                while dots_sum < glyph_width:
                    byte = glyph_data[i]
                    dot = 0
                    
                    while dot < 8 and dot + dots_sum < glyph_width:
                        if (byte >> (7 - dot)) & 1: # main color
                            GPIO_OUT[0] = color_hi
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = color_low
                            GPIO_OUT_S[0] = wr_bit
                        else: # background
                            GPIO_OUT[0] = bg_hi
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = bg_low
                            GPIO_OUT_S[0] = wr_bit
                        dot += 1                         
     
                    dots_sum += 8
                    i += 1
        elif pxlf == 0x66: # 18-bit
            main1 = byte2gpio[ (color >> 10) & 0xFF ] 
            main2 = byte2gpio[ (color >> 2) & 0xFF ]  
            main3 = byte2gpio[ (color << 4) & 0xF0 ]
            
            bg1 = byte2gpio[ (bg >> 10) & 0xFF ] 
            bg2 = byte2gpio[ (bg >> 2) & 0xFF ]  
            bg3 = byte2gpio[ (bg << 4) & 0xF0 ]        
            
            i = 0
            for dots_row in range(glyph_height): # 
                dots_sum = 0                    
                while dots_sum < glyph_width:
                    byte = glyph_data[i]
                    dot = 0
                    
                    while dot < 8 and dot + dots_sum < glyph_width:
                        if (byte >> (7 - dot)) & 1: # main color
                            GPIO_OUT[0] = main1
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = main2
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = main3
                            GPIO_OUT_S[0] = wr_bit                    
                        else: # background
                            GPIO_OUT[0] = bg1
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = bg2
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = bg3
                            GPIO_OUT_S[0] = wr_bit 
                        dot += 1                         
     
                    dots_sum += 8
                    i += 1
        else: # PIXEL_FORMAT == 0x77: # 24-bit 
            color_r = byte2gpio[(color >> 16) & 0xFF ] 
            color_g = byte2gpio[(color >> 8) & 0xFF ]  
            color_b = byte2gpio[color & 0xFF]
            
            bg_r = byte2gpio[(bg >> 16) & 0xFF ] 
            bg_g = byte2gpio[(bg >> 8) & 0xFF ]  
            bg_b = byte2gpio[bg & 0xFF]        
            
            i = 0
            for dots_row in range(glyph_height): # 
                dots_sum = 0                    
                while dots_sum < glyph_width:
                    byte = glyph_data[i]
                    dot = 0
                    
                    while dot < 8 and dot + dots_sum < glyph_width:
                        if (byte >> (7 - dot)) & 1: # main color
                            GPIO_OUT[0] = color_r
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = color_g
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = color_b
                            GPIO_OUT_S[0] = wr_bit                    
                        else: # background
                            GPIO_OUT[0] = bg_r
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = bg_g
                            GPIO_OUT_S[0] = wr_bit
                            GPIO_OUT[0] = bg_b
                            GPIO_OUT_S[0] = wr_bit 
                        dot += 1                         
     
                    dots_sum += 8
                    i += 1            
        
    def scroll_text(self, text, x, y, color, bg = 0x0000, delay = 10):
        """ Scroll text on display
        Args
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        bg (int) : Bacground, RGB color
        delay (int): Delay between new lines (ms)
        """
        font = self.font        
        if font == None:
            print("Font not set")
            return False
        
        screen_width = self.width
        screen_height = self.height
        
        self.vert_scroll(0, screen_height, 0)
        run_scrolling = False
        
        x_start = x
        
        glyph1st = font.get_ch(text[0])
        glyph_height = glyph1st[1] # from first char
        
        for char in text:
            if char == "\n": # New line
                x = screen_width
                continue
            
            if char == "\t": #replace tab to space
                char = " "                
            
            glyph = font.get_ch(char)
            glyph_height = glyph[1]
            glyph_width = glyph[2]
            
            if x + glyph_width >= screen_width: # End of row
                x = x_start                        
                y += glyph_height
                
                if y + glyph_height > screen_height: # End of screen
                    run_scrolling = True
                    y = 0

                if run_scrolling:
                    self._scroll_row(y, glyph_height, screen_width, bg, delay)
                
            self._draw_glyph_fast(glyph, x, y, color, bg)
            x += glyph_width
            
            if char == " " and (x + glyph_width) <= screen_width: # double size for space
                self._draw_glyph_fast(glyph, x, y, color, bg)
                x += glyph_width
        self.cs.value(1)
             
    def _scroll_row(self, y, glyph_height, screen_width, bg, delay):
        """ Scroll one row of text """
        for ys in range(glyph_height):
            self.vert_scroll_start_address(y + ys + 1) #scrolling up on glyph_height
            self.fill_rect(0, y + ys, screen_width, 1, bg)
            sleep_ms(delay)





