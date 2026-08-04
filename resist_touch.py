"""
resist_touch v 0.3.2

Project path: https://github.com/r2d2-arduino/micropython_ili9488_9486_9341_shields

Author: Arthur Derkach 
"""

from machine import Pin, ADC
from time import sleep_ms, sleep_us, ticks_us

class ResistiveTouchScreen:
    
    NUM_SAMPLES = const(11) # Number of attempts to find the correct value
    
    def __init__(self, yu_pin, xl_pin, yd_pin, xr_pin, rd_pin,
                 width, height, adc_type = 0 ):
        
        # min, max, direction
        #2.4 9341
        if adc_type == 0:
            self.X_CALIB = [534, 3693, 1]
            self.Y_CALIB = [557, 3888, 0]
        else: # rp2 pico
            self.X_CALIB = [9506, 57966, 0]
            self.Y_CALIB = [8242, 54301, 1]
        
        #2.8 9341
        #self.X_CALIB = [265, 3445, 3]
        #self.Y_CALIB = [343, 3639, 0]     
        
        #3.5 9486        
        #self.X_CALIB = [495, 3683, 1]
        #self.Y_CALIB = [301, 3847, 2]
        
        #3.5 9488
        #self.X_CALIB = [374, 3900, 0]
        #self.Y_CALIB = [505, 3739, 1]
    
        self.YU = Pin(yu_pin,  Pin.OUT)  # Up Y 
        self.XL = Pin(xl_pin,  Pin.OUT)  # Left X 
        self.YD = Pin(yd_pin,  Pin.OUT)  # Down Y 
        self.XR = Pin(xr_pin,  Pin.OUT)  # Right X
        self.RD = Pin(rd_pin,  Pin.OUT, value = 1) # Must be 1
                
        # Analog In for measuring
        self.ADC_XR = ADC(self.XR)  # Analog In for XR        
        self.ADC_YU = ADC(self.YU)  # Analog In for YU
        
        self.adc_type = adc_type
        self.adc_max = 4095
    
        self.ADC_LEVEL = [100, 4000] # Min/Max ADC signal level to accept the value
        self.NOISE = [100, 400] # Acceptable level of point scatter AND phantom activations
        
        if adc_type == 1: # for rpi pico
            self.ADC_LEVEL = [6500, 59000] # Min/Max ADC signal level to accept the value
            self.NOISE = [2000, 8000] # Acceptable level of point scatter AND avoiding phantom activations
            self.adc_max = 65535
            
        self.auto_calibration = 0 # Allow to auto-calibrate        
        
        if adc_type == 0: # esp32
            self.ADC_XR.atten(ADC.ATTN_11DB)
            self.ADC_YU.atten(ADC.ATTN_11DB)
            # Кэшируем вызовы методов АЦП, чтобы избавиться от if в циклах
            self._get_x_adc = self.ADC_XR.read
            self._get_y_adc = self.ADC_YU.read
        else: # rpi pico
            self._get_x_adc = self.ADC_XR.read_u16
            self._get_y_adc = self.ADC_YU.read_u16
        
        self.width  = width # < height
        self.height = height
        
        self.rotation = 0 # default - 0 degrees
        self.revert = self.Y_CALIB[2] & 1
        
        self.x_coef, self.y_coef, self.x_corr, self.y_corr, self.x_len, self.y_len = self.calc_coefs()
        
        self.prev_x = -1
        self.prev_y = -1
        
        self._sample_buf = [0] * self.NUM_SAMPLES
        
        self.reset_pins()
        
    def reset_pins(self):
        """ Reset pins to default """
        self.XL.init(Pin.OUT, value = 0)
        self.XR.init(Pin.OUT, value = 0)
        self.YU.init(Pin.OUT, value = 0)
        self.YD.init(Pin.OUT, value = 0)
        self.RD.init(Pin.OUT, value = 1)
        
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

    def read_x(self):
        """ Read X: Power to X-plate, read via Y-wiper """
        self.XL.init(Pin.OUT, value=0)
        self.XR.init(Pin.OUT, value=1)
        self.YU.init(Pin.IN)
        self.YD.init(Pin.IN)
        sleep_us(5) # Wait for voltage stabilization
        return self._get_y_adc() # Считываем YU

    def read_y(self):
        """ Read Y: Power to Y-plate, read via X-wiper """
        self.YU.init(Pin.OUT, value=1)
        self.YD.init(Pin.OUT, value=0)
        self.XL.init(Pin.IN)
        self.XR.init(Pin.IN)
        sleep_us(5)# Wait for voltage stabilization
        return self._get_x_adc() # Read XR

    def read_z(self):
        self.XL.init(Pin.OUT, value=0)
        self.YD.init(Pin.OUT, value=1)
        self.XR.init(Pin.IN)
        self.YU.init(Pin.IN)
        sleep_us(5) # Wait for voltage stabilization
        
        z1 = self._get_x_adc()
        z2 = self._get_y_adc()
        # Calculate pressure using correct ADC maximum
        return self.adc_max - z2 + z1    

    def read_touch(self):
        """ Read ADC values of touch. Exclude noise touches. 
        Return (int, int): X & Y adc values
        """
        min_lvl, max_lvl = self.ADC_LEVEL
        noise_lvl, noise_press = self.NOISE
        adc_type = self.adc_type
        num_samp = self.NUM_SAMPLES
        
        z = self.read_z()
        
        if z < noise_press:
            return -noise_press, -noise_press
        
        sambuf = self._sample_buf
        readx = self.read_x
        ready = self.read_y
        #Taking multiple measurements to choose an average X
        for i in range(num_samp):
            sambuf[i] = readx()
        
        sambuf.sort()
        x = sambuf[ num_samp // 2 ]
        
        #Taking multiple measurements to choose an average Y
        for i in range( num_samp ):
            sambuf[i] = ready()            
        sambuf.sort()
        y = sambuf[ num_samp // 2 ]
        
        self.reset_pins()

        if (min_lvl < x < max_lvl) and (min_lvl < y < max_lvl):
            sum_xy = x + y
            prev_sum = self.prev_x + self.prev_y
                    
            self.prev_x, self.prev_y = x, y
            
            if abs(sum_xy - prev_sum) < noise_lvl:
                if self.auto_calibration:
                    self.auto_calibrate(x, y)
                return x, y

        return -noise_lvl, -noise_lvl
      
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
        noise_lvl = self.NOISE[0]
        
        x_adc, y_adc = self.read_touch()
        
        if x_adc < 0 or y_adc < 0:
            return -noise_lvl, -noise_lvl

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
            #start = ticks_us()
            x, y = self.read_coordinats()
            if 0 <= x <= x_len and 0 <= y <= y_len:
                #print((ticks_us()-start), 'us')
                #print(x, y)
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

   