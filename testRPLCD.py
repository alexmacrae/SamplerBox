import RPi.GPIO as GPIO
from RPLCD import CharLCD, cleared, cursor
import time
import lcdcustomchars as lcdcc
lcd = CharLCD(pin_rs=7, pin_rw=None, pin_e=8, pins_data=[27, 17, 18, 4], numbering_mode=GPIO.BCM, cols=16, rows=2)

smiley = (
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b10001,
    0b10001,
    0b01110,
    0b00000,
)
black = (
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
    0b11111,
)

battery_0 = (
    0b00100,
    0b01110,
    0b01010,
    0b01010,
    0b01010,
    0b01010,
    0b01110,
    0b00000
)
battery_25 = (
    0b00100,
    0b01110,
    0b01010,
    0b01010,
    0b01010,
    0b01110,
    0b01110,
    0b00000
)

battery_50 = (
    0b00100,
    0b01110,
    0b01010,
    0b01010,
    0b01110,
    0b01110,
    0b01110,
    0b00000
)
battery_100 = (
    0b00100,
    0b01110,
    0b01110,
    0b01110,
    0b01110,
    0b01110,
    0b01110,
    0b00000
)

bmp1 = (
    0b10000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp2 = (
    0b11000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp3 = (
    0b11100,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp4 = (
    0b11110,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp5 = (
    0b11111,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp6 = (
    0b11111,
    0b10000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp7 = (
    0b11111,
    0b11000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp8 = (
    0b11111,
    0b11100,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp9 = (
    0b11111,
    0b11110,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp10 = (
    0b11111,
    0b11111,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp11 = (
    0b11111,
    0b11111,
    0b10000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp12 = (
    0b11111,
    0b11111,
    0b11000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp13 = (
    0b11111,
    0b11111,
    0b11100,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp14 = (
    0b11111,
    0b11111,
    0b11110,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp15 = (
    0b11111,
    0b11111,
    0b11111,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
bmp16 = (
    0b11111,
    0b11111,
    0b11111,
    0b10000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)


bmp_list = (bmp1, bmp2, bmp3, bmp4, bmp5, bmp6, bmp7, bmp8, bmp9, bmp10, bmp11, bmp12, bmp13, bmp14, bmp15, bmp16)



lcd.create_char(0, smiley)
lcd.create_char(1, black)
lcd.create_char(2, battery_100)
lcd.create_char(3, battery_50)
lcd.create_char(4, battery_25)
lcd.create_char(5, battery_0)

while True:
    lcd.clear()

    for b in lcdcc.battery_states:
        lcd.create_char(0, b)
        lcd.write_string(unichr(0))
        lcd._set_cursor_pos((0, 0))
        time.sleep(0.2)

    time.sleep(2)

