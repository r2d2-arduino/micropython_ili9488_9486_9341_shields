# micropython_ili9488_9486_9341_shields
Large and fast library for Esp32, RPi Pico and Esp32-S3. Used to work with ILI9488, ILI9486, ILI9341 (3.5"/2.8"/2.4") display-sheilds, with 8-bit data bus.
![Photo of back side of Esp32-D1R32](/../main/photos/ili9xxx_shields.png)

## Preparing for the Esp32 D1R32 board:

If you put the Esp32 D1R32 board on the display shield, the 3 pins will not work properly.
LCD_RST, LCD_CS, LCD_RS are placed on pins 36, 34, 35 which work only on the input.
While an output is needed to send data to the display.
Therefore, it is proposed to connect with wires: 36 -> 33, 34 -> 32, 35 -> 15. As shown in the photo.
For better operation, you can disconnect the contacts: 34, 35, 36, but this is not necessary. 
![Photo of back side of Esp32-D1R32](/../main/photos/esp32-r1d32-back.png)

## Preparing for the Esp32-S3 Uno board:

If you put the Esp32-S3 Uno board on the display shield, the 4 pins will not work properly.
LCD_D0, LCD_D1, LCD_D4, LCD_D5 are placed on pins 19, 20, 21 (used for USB hid/host) and 46 (used for Log).
Therefore, it is proposed to connect with wires: 19 -> 15, 20 -> 16, 21 -> 9, 46 -> 8. Also, make 2 cuts on the board. As shown in the photo.

![Photo of back side of Esp32-D1R32](/../main/photos/esp32-s3-uno-back.png)

## Preparing for other boards:
There is no need to change anything on the board. Since you can select any pins. The only thing that is recommended: check the operation of the pins in `ili9xxx_pin_checker.py`

## Pin restrictions:

For Esp32, Raspberry Pi Pico, Esp32-S3: Only pins between 1-31 can be used.
For Esp32 D1R32: CS pin should be 32 or 33 (This pin uses a register GPIO_OUT1_REG).

## File Structure:

* **ili9xxx_8b.py** - Base library ILI9XXX_8B for ILI9341/ILI9486/ILI9488. Specified on Esp32, RPi Pico and Esp32-S3.
* **ili9xxx_8b_direct.py** - Main library ILI9XXX_8B_DIRECT with direct draw.
* **ili9xxx_8b_fb.py** - Main library ILI9XXX_8B_FB with framebuffer.
* **resist_touch.py** - resistive touchscreen library.
* **touch_calibration_ili9xxx.py** - Touchscreen calibration tool. Run and click on 9 green squares one by one.
After that, a set of new calibration parameters will be displayed, which should be replaced in resist_touch.py on ​​line 22-24.
* **ili9xxx_pin_checker.py** - Checks the correct connection of pins to controller. Use when you want to change recommended pins.

* **examples/** - a set of examples for using the library ILI9XXX_8B_DIRECT
* **examples_fb/** - a set of examples for using the library ILI9XXX_8B_FB
* **resources/** - related files for examples.

## Dependencies:
The main libraries inherit from the graphics libraries tft_draw:
https://github.com/r2d2-arduino/tft_draw

## Minimum code to run:
The script will attempt to detect the display model automatically, but you can also specify it manually. For example, by setting input parameter display_model = 0x9488.
```python
from ili9xxx_8b_direct import ILI9XXX_8B_DIRECT

#Esp32 D1R32
DATA_PINS = [12, 13, 26, 25, 17, 16, 27, 14]
CS_PIN = 32
DC_PIN = 15 #rs/dc
WR_PIN = 4
RD_PIN = 2
RST_PIN = 33

tft = ILI9XXX_8B_DIRECT( DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN )

tft.fill( tft.rgb(255, 0, 0) ) # Fill the screen with red color
```
## Display functions:

* **set_rotation( rotation = 0 ):** Set orientation of display. 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees.
* **invert_display( on = True ):** Enables or disables color inversion on the display.
* **idle_mode( on = True ):** Enables or disables idle mode on the display.
* **set_adaptive_brightness( mode ):** Set adaptive brightness.
* **vert_scroll( top_fix, scroll_height, bot_fix ):** Vertical scroll settings.
* **vert_scroll_start_address( start = 0 ):** Set vertical scroll start address, and run scrolling.
* **tearing_effect( on = True ):** Activate "Tearing effect".

![Photo of back side of Esp32-D1R32](/../main/photos/ili9xxx_example.png)
