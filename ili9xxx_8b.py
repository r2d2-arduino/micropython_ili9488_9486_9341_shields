"""
ILI9XXX_8B display-shield v 0.3.6

Displays: ILI9341, ILI9486, ILI9488
Connection: 8-bit Data Bus
Colors: 16-bit, 18-bit, 24-bit
Controllers: Esp32, Esp32-S3, Raspberry Pi Pico

Project path: https://github.com/r2d2-arduino/micropython_ili9488_9486_9341_shields
MIT License

Author: Arthur Derkach
"""
from machine import Pin
from time import sleep_ms


class ILI9XXX_8B():
    
    def __init__( self, data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin,
                  width = 0, height = 0, bpp = 16, display_model = 0 ):
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
        bpp     (int): Bits per Pixel: 16, 18 or 24
        controller (string): Controller name: ESP32, ESP32-S3, ESP32-C3, RP2
        display_model (hex): One of 0x9341, 0x9386 (default), 0x9388 
        """

        self.data_pins = data_pins
        self.cs_pin = cs_pin
        self.dc_pin = dc_pin
        self.wr_pin = wr_pin
        self.rst_pin = rst_pin
        self.rd_pin = rd_pin
        
        self.db0 = Pin(data_pins[0], Pin.OUT, value = 0)
        self.db1 = Pin(data_pins[1], Pin.OUT, value = 0)
        self.db2 = Pin(data_pins[2], Pin.OUT, value = 0)
        self.db3 = Pin(data_pins[3], Pin.OUT, value = 0)
        self.db4 = Pin(data_pins[4], Pin.OUT, value = 0)
        self.db5 = Pin(data_pins[5], Pin.OUT, value = 0)
        self.db6 = Pin(data_pins[6], Pin.OUT, value = 0)
        self.db7 = Pin(data_pins[7], Pin.OUT, value = 0)
        self.db_pins = [self.db0, self.db1, self.db2, self.db3, self.db4, self.db5, self.db6, self.db7]
               
        self.cs = Pin(cs_pin, Pin.OUT, value = 1)
        self.dc = Pin(dc_pin, Pin.OUT, value = 1)
        self.wr = Pin(wr_pin, Pin.OUT, value = 0)
        self.rst= Pin(rst_pin,Pin.OUT, value = 1)
        self.rd = Pin(rd_pin, Pin.OUT, value = 1)
            
        self.reset()
        
        self.rotation = 0
        
        self.display_model = display_model
        
        if display_model == 0:
            self.display_model = self.read_display_model()
            #print( 'Display model:', hex(self.display_model) )
        
        if bpp == 24:
            self.pixel_format = 0x77
        elif bpp == 18:
            self.pixel_format = 0x66
        else: # bpp == 16:
            self.pixel_format = 0x55
        
        
        self.width = 240 # default width
        self.height = 320 # default height
        
        if width > 0:
            self.width = width
        else:            
            if self.display_model in (0x9486, 0x9488): 
                self.width = 320                
                
        if height > 0:
            self.height = height
        else:       
            if self.display_model in (0x9486, 0x9488): 
                self.height = 480

        if self.display_model == 0x9341:
            self.init_display_9341()
        elif self.display_model == 0x9486:
            self.init_display_9486()
        elif self.display_model == 0x9488:
            self.init_display_9488()
        else:
            print('Unknown Display Model!', hex(self.display_model))
            self.init_display_9486()

        self.wr_bit = 1 << wr_pin
        self.dc_bit = 1 << dc_pin

        self.controller_name = self.read_controller_name()

        if self.controller_name == 'ESP32-D1R32': # fix for ESP32-D1R32
            self.cs_bit = 1 << (cs_pin - 32)
        else:
            self.cs_bit = 1 << cs_pin

        if self.controller_name in ('ESP32-S3', 'ESP32-C3'):
            self.GPIO_OUT_REG  = 0x60004004 # 00-31 pin-output registers
            self.GPIO_OUT_SET  = 0x60004008 # + bit
        elif self.controller_name == 'RP2': #Raspberry Pi Pico
            self.GPIO_OUT_REG = 0xD0000010
            self.GPIO_OUT_SET = 0xD0000014
        else: # ESP32
            self.GPIO_OUT_REG = 0x3FF44004
            self.GPIO_OUT_SET = 0x3FF44008

        self.BYTE2GPIO = bytearray(1024)
        self.gpio_state = 0
        self.update_byte2gpio()


    def reset(self):
        """ Resets display settings to default. """
        self.rst.value(0)
        sleep_ms(10)
        self.rst.value(1)
        sleep_ms(120)
        self.write_command(0x01)  # Software Reset
        sleep_ms(120)

    def init_display_9341(self):

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

    def init_display_9486(self):
        """ Initial display settings """

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

    def init_display_9488(self):
        """ Main settings of display """

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

    def read_data(self):
        """ Reading data from the display. """
        self.dc.value(1) # Data mode
        self.wr.value(1) #
        self.rd.value(0) # Read mode On (LOW)
        self.cs.value(0) # Selecting a device

        # Switch data pins to input mode
        for pin in self.db_pins:
            pin.init(Pin.IN)

        data = 0
        for i in range(8):
            data |= self.db_pins[i].value() << i

        self.rd.value(1)  # Deactivate Read mode (HIGH)
        self.cs.value(1)  # Deselect device

        # Switch data pins back to output mode
        for pin in self.db_pins:
            pin.init(Pin.OUT, value=0)
        return data

    def read_display_model(self):
        """ Reading display model """
        self.write_command(0xD3)
        dummy = self.read_data()
        version = self.read_data()
        model1  = self.read_data()
        model2  = self.read_data()

        model = (model1 << 8) + model2

        return model

    @staticmethod
    def read_controller_name():
        from os import uname
        
        """ Reading controller name """
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

    def reinit_pins(self):
        """ Reinit most important pins.
        Most often used in combination with another devices.
        """
        self.cs.init(Pin.OUT,  value = 1)
        self.dc.init(Pin.OUT,  value = 1)
        self.wr.init(Pin.OUT,  value = 0)
        self.rst.init(Pin.OUT, value = 1)
        self.rd.init(Pin.OUT,  value = 1)

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
        self.db0.value( value & 1 )
        self.db1.value((value >> 1) & 1)
        self.db2.value((value >> 2) & 1)
        self.db3.value((value >> 3) & 1)
        self.db4.value((value >> 4) & 1)
        self.db5.value((value >> 5) & 1)
        self.db6.value((value >> 6) & 1)
        self.db7.value((value >> 7) & 1)


    @micropython.viper
    def update_byte2gpio(self):
        """ Generate to memory all 256 states of data gpio
        Return (bytearray): All 256 x 32-bit states """

        # Base setting before making register snapshot
        self.cs.value(0)
        self.dc.value(1)
        self.wr.value(0)
        self.set_data_pins(0)

        # Getting current state of gpio registers (snapshot)
        gpio_out_ptr = ptr32(int(self.GPIO_OUT_REG))
        empty_mask = gpio_out_ptr[0]
        
        #print(empty_mask, int(self.gpio_state))
        if empty_mask == int(self.gpio_state):
            return
        #print('update')
        self.gpio_state = empty_mask
        
        self.cs.value(1) # Deselect device

        # Data pins cashing
        dpins = self.data_pins
        p0 = int(dpins[0])
        p1 = int(dpins[1])
        p2 = int(dpins[2])
        p3 = int(dpins[3])
        p4 = int(dpins[4])
        p5 = int(dpins[5])
        p6 = int(dpins[6])
        p7 = int(dpins[7])

        # Getting 32-bit access to gpio bytearray
        buffer = ptr32(self.BYTE2GPIO)

        # Generating of all 256 states
        for byte in range(256):
            # Convert byte to gpio setting
            bit_gpio  = ((byte & 1) << p0)
            bit_gpio |= (((byte >> 1) & 1) << p1)
            bit_gpio |= (((byte >> 2) & 1) << p2)
            bit_gpio |= (((byte >> 3) & 1) << p3)
            bit_gpio |= (((byte >> 4) & 1) << p4)
            bit_gpio |= (((byte >> 5) & 1) << p5)
            bit_gpio |= (((byte >> 6) & 1) << p6)
            bit_gpio |= (((byte >> 7) & 1) << p7)

            # Saving state in memory
            buffer[ byte ] = bit_gpio | empty_mask

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

        if self.display_model == 0x9486:
            if self.rotation == 0: # 0 deg
                self.memory_access_control(0, 0, 0, 0, 1, 0)
            elif self.rotation == 1: # 90 deg
                self.memory_access_control(0, 1, 1, 0, 1, 0)
            elif self.rotation == 2: # 180 deg
                self.memory_access_control(1, 1, 0, 0, 1, 0)
            elif self.rotation == 3: # 270 deg
                self.memory_access_control(1, 0, 1, 0, 1, 0)
        else:
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
            
            self.swap_dimensions()

    def invert_display(self, on = True):
        """ Enables or disables color inversion on the display.
        Args
        on (bool): True = Enable inversion, False = Disable inversion
        """
        if on:
            self.write_command(0x21)
        else:
            self.write_command(0x20)

    def tearing_effect(self, on = True):
        """ Activate "Tearing effect"
        Args
        on (bool): True = Enable effect, False = Disable effect
        """
        if bool(on):
            self.write_command(0x35)
        else:
            self.write_command(0x34)

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
            print('Error mode in def set_adaptive_brightness')
            print(mode)

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

        total_height = top_fix + bot_fix + scroll_height

        if total_height == screen_height:
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
