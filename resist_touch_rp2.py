"""
resist_touch v 0.2.3

Project path: https://github.com/r2d2-arduino/micropython_ili9488_9486_9341_shields

Author: Arthur Derkach 
"""

from machine import Pin, ADC
from time import sleep_ms 

class ResistiveTouchScreen:   
    MIN_LEVEL   = const(6500) # Minimum ADC signal level to accept the value
    MAX_LEVEL   = const(59000) # Maximum ADC signal level to accept the value
    NOISE_PRESS = const(2000) # To avoid phantom activations
    NOISE_LEVEL = const(8000) # Acceptable level of point scatter
    NUM_SAMPLES = const(11) # Number of attempts to find the correct value    
    
    def __init__(self, yu_pin, xl_pin, yd_pin, xr_pin, rd_pin, width, height):
        
        # min, max, direction
        self.X_CALIB = [8017, 55965, 3]
        self.Y_CALIB = [8177, 58398, 0]        
        
        self.auto_calibration = 0 # Allow to auto-calibrate        
        
        self.YU = Pin(yu_pin,  Pin.OUT)  # Up Y 
        self.XL = Pin(xl_pin,  Pin.OUT)  # Left X 
        self.YD = Pin(yd_pin,  Pin.OUT)  # Down Y 
        self.XR = Pin(xr_pin,  Pin.OUT)  # Right X
        self.RD = Pin(rd_pin,  Pin.OUT, value = 1) # Must be 1
                
        # Analog In for measuring
        self.ADC_XR = ADC(self.XR)  # Analog In for XR        
        self.ADC_YU = ADC(self.YU)  # Analog In for 
        
        self.width  = width # < height
        self.height = height
        
        self.rotation = 0 # default - 0 degrees
        self.revert = self.Y_CALIB[2] & 1
        
        self.x_coef, self.y_coef, self.x_corr, self.y_corr, self.x_len, self.y_len = self.calc_coefs()
        
        self.prev_x = -1
        self.prev_y = -1        
        
    def calc_coefs(self):
        x_min, x_max, x_dir = self.X_CALIB
        y_min, y_max, y_dir = self.Y_CALIB

        x_len = self.width
        y_len = self.height
        
        if y_dir & 1:
            x_len = self.height
            y_len = self.width
        
        x_coef = (x_max - x_min) / x_len
        y_coef = (y_max - y_min) / y_len
        
        x_corr = x_min / x_coef 
        y_corr = y_min / y_coef
        
        return x_coef, y_coef, x_corr, y_corr, x_len, y_len
    
    def reset_pins(self):
        """ Reset pins to default """
        self.XL.init(Pin.OUT, value = 0)
        self.XR.init(Pin.OUT, value = 0)
        self.YU.init(Pin.OUT, value = 0)
        self.YD.init(Pin.OUT, value = 0)
        self.RD.init(Pin.OUT, value = 1)


    def read_x(self):
        """ Measuring X adc value
        Return (int): X value 0..65535 """
        self.YU.value(1)        
        self.YD.value(0)

        self.XL.init(Pin.IN)
        self.XR.init(Pin.IN)
        
        x = self.ADC_XR.read_u16()
        
        return x
    
    def read_y(self):
        """ Measuring Y adc value
        Return (int): Y value 0..65535 """
        self.XR.value(1)        
        self.XL.value(0)

        self.YU.init(Pin.IN)
        self.YD.init(Pin.IN)
        
        y = self.ADC_YU.read_u16()
  
        return y
    
    def read_z(self):
        """ Measuring pressure
        Return (int): Z value 0..65535 """
        self.XL.init(Pin.OUT, value = 0)
        self.YD.init(Pin.OUT, value = 1)
        self.XR.off()
        self.XR.init(Pin.IN)
        self.YU.off()
        self.YU.init(Pin.IN)
        
        z1 = self.ADC_XR.read_u16()
        z2 = self.ADC_YU.read_u16()
        
        return 65535 - z2 + z1  
    
    def read_touch(self):
        """ Read ADC values of touch. Exclude noise touches. 
        Return (int, int): X & Y adc values
        """
        z = self.read_z()

        if z < NOISE_PRESS:
            return -NOISE_PRESS, -NOISE_PRESS
        self.reset_pins()
        
        #Taking multiple measurements to choose an average X
        x_list = []
        x_list.append( self.read_x() )
        for _ in range(NUM_SAMPLES - 1):
            x_list.append( self.ADC_XR.read_u16() )
        x_list.sort()
        x = x_list[NUM_SAMPLES//2 + 1]
        self.reset_pins()
        
        #Taking multiple measurements to choose an average Y
        y_list = []
        y_list.append( self.read_y() )
        for _ in range(NUM_SAMPLES - 1):
            y_list.append( self.ADC_YU.read_u16() )
        y_list.sort()        
        y = y_list[NUM_SAMPLES//2 + 1]
        self.reset_pins()
        
        if (MIN_LEVEL < x < MAX_LEVEL) and (MIN_LEVEL < y < MAX_LEVEL):
            sum_xy = x + y
            prev_sum = self.prev_x + self.prev_y
                    
            self.prev_x, self.prev_y = x, y
            
            if (0 <= sum_xy - prev_sum < NOISE_LEVEL) or (0 <= prev_sum - sum_xy < NOISE_LEVEL):
                if self.auto_calibration:
                    self.auto_calibrate(x, y)
                return x, y
            else:
                print("Sum reject", sum_xy, prev_sum)

        return -NOISE_LEVEL, -NOISE_LEVEL
      
    def set_rotation(self, rotation):
        """ Set orientation for Toushscreen
        Args
        rotation (int): 0..3, 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees
        """
        self.rotation = rotation

        directions = (0, 1, 2, 3, 0, 1, 2, 3)
        x_dir = directions[ self.X_CALIB[2] + 4 - rotation ]
        y_dir = directions[ self.Y_CALIB[2] + 4 - rotation ]
        self.X_CALIB[2] = x_dir
        self.Y_CALIB[2] = y_dir
        
    def read_coordinats(self):
        """ Read X and Y coordinates on screen
        Return (int, int): X & Y coordinates in pixels
        """        
        x_adc, y_adc = self.read_touch()
        
        if x_adc < 0 or y_adc < 0:
            return -NOISE_LEVEL, -NOISE_LEVEL

        x_pix = int( x_adc / self.x_coef - self.x_corr )
        y_pix = int( y_adc / self.y_coef - self.y_corr )

        revert = self.revert 
        
        if self.rotation & 1: # for 90 & 270 degress
            revert = 1 - revert 
        
        x_dir = self.X_CALIB[2] 
        y_dir = self.Y_CALIB[2] 
        
        x_coord = x_pix
        y_coord = y_pix
        
        if revert:
            if y_dir == 3: # left <- right
                y_coord = self.y_len - y_pix
                   
            if x_dir == 0: # down -> up      
                x_coord = self.x_len - x_pix
                
            return y_coord, x_coord
        else:
            if x_dir == 3: # left <- right
                x_coord = self.x_len - x_pix
                   
            if y_dir == 0: # down -> up      
                y_coord = self.y_len - y_pix
                
            return x_coord, y_coord            
        
    def listening(self, delay = 10):
        """ Listening of touches
        Args
        delay (int): Delay in ms between new listening
        Return (int, int): X & Y coordinates in pixels
        """
        
        if self.rotation & 1:
            x_len = self.height
            y_len = self.width
        else:
            x_len = self.width
            y_len = self.height
            
        while True:
            #start = time.ticks_us()
            x, y = self.read_coordinats()
            if 0 <= x <= x_len and 0 <= y <= y_len:
                #print((time.ticks_us()-start), 'us')
                print(x, y)
                return x, y
            sleep_ms(delay)
            
    def auto_calibrate(self, x, y):
        """ Auto calibrate X & Y coordinates """
        x_min, x_max, x_dir = self.X_CALIB
        y_min, y_max, y_dir = self.Y_CALIB
        
        recalib = False
        
        if x < x_min:
            self.X_CALIB[0] = x
            recalib = True
        if x > x_max:
            self.X_CALIB[1] = x
            recalib = True
            
        if y < y_min:
            self.Y_CALIB[0] = y
            recalib = True
        if y > y_max:
            self.Y_CALIB[1] = y
            recalib = True
            
        if recalib:
            self.x_coef, self.y_coef, self.x_corr, self.y_corr, self.x_len, self.y_len = self.calc_coefs()
            print('recalib')
            