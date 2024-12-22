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

## Pin restrictions:

For Esp32, Raspberry Pi Pico, Esp32-S3: Only pins between 1-31 can be used.
For Esp32 D1R32: CS pin should be 32 or 33 (This pin uses a register GPIO_OUT1_REG).

## File Structure:

* **ili9xxx_8b.py** - Base library for ILI9341/ILI9486/ILI9488. Specified on Esp32, Raspberry Pi Pico and Esp32-S3.
* **ili9xxx_d1r32.py** - Base library for ILI9341/ILI9486/ILI9488. Specified on Esp32 D1R32 only.
* **ili9341.py** - Main library for ILI9341 display (2.4"..2.8"). 
* **ili9486.py** - Main library for ILI9486 display (3.5"). 
* **ili9488.py** - Main library for ILI9488 display (3.5"..4"). 

* **ili9xxx_pin_checker.py** - Checks the correct connection of pins to controller. Use when you want to change recommended pins.
* **resist_touch.py** - resistive touchscreen library. Specified on Esp32.
* **resist_touch_rp2.py** - resistive touchscreen library. Specified on Raspberry Pi Pico.

* **touch_calibration_ili9488.py**, **touch_calibration_ili9486.py**,  **touch_calibration_ili9341.py** - Touchscreen calibration tool. Run and click on 9 green squares one by one.
After that, a set of new calibration parameters will be displayed, which should be replaced in resist_touch.py on ​​line 22-24.

* **ILI9341_example/** - a set of examples for using the library ILI9341.py
* **ILI9486_example/** - a set of examples for using the library ILI9486.py
* **ILI9488_example/** - a set of examples for using the library ILI9488.py
* **utils/** - a set of utils
font_to_py.py
pip install freetype-py
font_to_py.py -x LibreBodoni-Bold.ttf 24 LibreBodoni24.py

## Minimum code to run (ILI9488):
```python
from ili9488 import ILI9488

#Esp32 D1R32
DATA_PINS = [12, 13, 26, 25, 17, 16, 27, 14]
CS_PIN = 32
DC_PIN = 15 #rs/dc
WR_PIN = 4
RD_PIN = 2
RST_PIN = 33

tft = ILI9488(DATA_PINS, CS_PIN, DC_PIN, WR_PIN, RD_PIN, RST_PIN)

tft.fill_screen(0xF800) # Fill the screen with red color
```
## Display functions:

* **set_rotation (rotation = 0):** Set orientation of display. 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees.
* **invert_display (on = True):** Enables or disables color inversion on the display.
* **idle_mode (on = True):** Enables or disables idle mode on the display.
* **set_adaptive_brightness (mode):** Set adaptive brightness.
* **vert_scroll (top_fix, scroll_height, bot_fix):** Vertical scroll settings.
* **vert_scroll_start_address (start = 0):** Set vertical scroll start address, and run scrolling.
* **tearing_effect (on = True):** Activate "Tearing effect".

## Draw functions:

* **fill_screen (color):** Fill whole screen.
* **draw_pixel (x, y, color):** Draw one pixel on display.
* **draw_line (x0, y0, x1, y1, color):** Draw line using Bresenham's Algorithm.
* **draw_vline (x, y, height, color, thickness = 1):** Draw vertical line.
* **draw_hline (x, y, width, color, thickness = 1):** Draw horizontal line.
* **draw_rect (x, y, width, height, color, thickness = 1):** Draw rectangle.
* **fill_rect (x, y, x_len, y_len, color):** Draw filled rectangle.
* **draw_circle (x, y, radius, color, border = 1):** Draw circle.
* **fill_circle (x, y, radius, color):** Draw filled circle.

## Image functions:

* **draw_bmp (filename, x = 0, y = 0):** Draw BMP image on display.
* **draw_raw_image (filename, x, y, width, height):** Draw RAW image (RGB565 format) on display.
* **draw_bitmap (bitmap, x_start, y_start, size, color ):** Draw bitmap.
* **draw_bitmap_fast (bitmap, x_start, y_start, size, color, bg):** Draw bitmap (fast version). Need to set background.
* **rgb (red, green, blue):** Convert 8,8,8 bits RGB to 16/18/24 bits.

## Text functions:

* **set_font (font):** Set font for text. Converted font is used. 
Conversion example: utils/font_to_py.py -x FONT_NAME.ttf 16 NEW_FONT_NAME_16.py
More details: https://github.com/peterhinch/micropython-font-to-py
* **draw_text (text, x, y, color):** Draw text on display.
* **draw_text_fast (self, text, x, y, color, bg = 0x0000):** Draw text on display (fast version). Need to set background.
* **scroll_text (text, x, y, color, bg = 0x0000, delay = 10):** Scroll text on display.

![Photo of back side of Esp32-D1R32](/../main/photos/ili9xxx_example.png)
