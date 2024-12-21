"""

ILI9XXX_PIN_CHECKER for 8-bit shield v 0.2.2

Project path: https://github.com/r2d2-arduino/micropython_ili9488_9486_9341_shields

Author: r2d2-arduino

"""
# Set pins here or choose one of the sets

# for Esp32-S3
DATA_PINS = [9, 8, 18, 17, 15, 16, 3, 14] #D0..D7
CS_PIN  = 6
DC_PIN  = 7 # = RS_PIN
WR_PIN  = 1
RD_PIN  = 2
RST_PIN = 5
'''
#for RP2
DATA_PINS = [2, 1, 8, 7, 6, 5, 4, 3]
CS_PIN  = 26
DC_PIN  = 27 # rs/dc
WR_PIN  = 28
RD_PIN  = 22 
RST_PIN = 21

#for ESP32 D1R32
DATA_PINS = [12, 13, 26, 25, 17, 16, 27, 14]
CS_PIN = 32
DC_PIN = 15 #rs/dc
WR_PIN = 4
RD_PIN = 2
RST_PIN = 33
'''
from machine import Pin
from time import sleep_ms
from os import uname

class ILI9XXX_PIN_CHECKER:
        
    def __init__( self, data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin ):
        """
        Constructor
        Params:
        data_pins (list): List of data bus pin numbers (D0, D1, ..., D7), example: [12, 13, 26, 25, 17, 16, 27, 14]
        cs_pin  (int): CS pin number (Chip Select)
        dc_pin  (int): DC pin number (command/parameter mode)
        wr_pin  (int): WR pin number (Write data signal)
        rd_pin  (int): RD pin number (Read data signal)
        rst_pin (int): RST pin number (Reset)
        """
        
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
       
        controller = self.controller_definition()
        print("Controller: ", controller)
        
        if controller == 'ESP32':
            self.INVALID_PINS = [0, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
        elif controller == 'ESP32-S3':
            self.INVALID_PINS = [0, 12, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
        elif controller == 'RP2':
            self.INVALID_PINS = [ 23, 24, 25, 29]
        else: #Unknown controller
            self.INVALID_PINS = []
        
        self.check_pins( data_pins, cs_pin, dc_pin, wr_pin, rd_pin, rst_pin )
        
        self.test_control_pins()

        self.test_data_pins()
        
        self.check_model()
        
        print("Test done.")
    
    def check_pins(self, data_pins, cs_pin: int, dc_pin: int, wr_pin: int, rd_pin: int, rst_pin: int):
        """
        Checks that pins are not on a list of unusable pins.
        
        Params:
        data_pins (list): List of data bus pin numbers for D0, D1,..., D7
        cs_pin, dc_pin, wr_pin, rd_pin, rst_pin (int): Pun numbers for CS, DC, WR, RD, RST
        
        """
        all_pins = data_pins + [cs_pin, dc_pin, wr_pin, rd_pin, rst_pin]
        for pin in all_pins:
            if pin in self.INVALID_PINS:
                raise ValueError(f"Pin {pin} is not suitable for connection. Please use another GPIO.")

    def test_control_pins(self):
        """
        Checks the correct operation of control pins (CS, DC, WR, RD, RST)
        """        
        pins_to_test = {
            "CS": self.cs,
            "DC": self.dc,
            "WR": self.wr,
            "RD": self.rd,
            "RST": self.rst
        }
        for name, pin in pins_to_test.items():
            if not self.test_pin(pin):
                raise RuntimeError(f"Error checking pin {name}.")

    def test_data_pins(self):
        """
        Checks the correct operation of the data bus pins
        """
        for i, pin in enumerate(self.db_pins):
            if not self.test_pin(pin):
                raise RuntimeError(f"Error checking data pin D{i}.")

        # Checking the correctness of data transfer on the bus
        if not self.test_data_bus():
            raise RuntimeError("Error while checking data transfer on 8-bit bus.")

    def test_pin(self, pin):
        """
        Tests the pin for the ability to be set to different states
        """
        try:
            pin.value(0)
            if pin.value() != 0:
                return False
            pin.value(1)
            if pin.value() != 1:
                return False
        except Exception as e:
            print(f"Error checking pin: {e}")
            return False
        return True

    def test_data_bus(self):
        """
        Checks the correctness of data transfer on the 8-bit bus
        """
        test_values = [0x00, 0xFF, 0x55, 0xAA]  # Test data set

        for value in test_values:
            self.set_data_pins(value)  # Set the value on the data bus
            # Checking the setting of each bit
            for i in range(8):
                if self.db_pins[i].value() != ((value >> i) & 1):
                    print(f"Data transfer error on bus: expected {((value >> i) & 1)}, received {self.db_pins[i].value()}")
                    return False
        return True
    
    def read_data(self):
        """
        Reading data from the display.
        """
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
        
    def write_command(self, cmd):
        """Отправка команды на дисплей"""
        self.dc.value(0)  # Режим команды
        self.rd.value(1)
        self.wr.value(0)        
        self.cs.value(0)  # Выбор устройства

        self.set_data_pins(cmd)
        self.wr.value(0)
        self.wr.value(1) 
        self.cs.value(1)  # Отменить выбор устройства           
        
    def read_display_ids(self):
        """ Reading display ID. """
        self.write_command(0x04) 
        
        dummy = self.read_data()
        id1 = self.read_data()
        id2 = self.read_data()
        id3 = self.read_data()
        
        id_sum = (id1 << 16) | (id2 << 8) | id3
        
        ids = {'id1': id1, 'id2': id2, 'id3': id3, 'id_sum': id_sum}

        return ids

    def read_display_model(self):
        self.write_command(0xD3)
        dummy = self.read_data()
        version = self.read_data()
        model1  = self.read_data()
        model2  = self.read_data()
        
        model = (model1 << 8) + model2
        
        return model
    
    def check_model(self):
        model = self.read_display_model()
        if model == 0x8080:
            print("Display: Unknown")
        else:
            print("Display:", hex(model))
    
    def controller_definition(self):
        """ Definition of current controller
        Return (string): Controller name """
        
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


pin_checker = ILI9XXX_PIN_CHECKER(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)


