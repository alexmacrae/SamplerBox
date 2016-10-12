import RPi.GPIO as GPIO
from RPLCD import CharLCD, cleared, cursor
import time
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


lcd.create_char(0, smiley)
lcd.create_char(1, black)
lcd.create_char(2, battery_100)
lcd.create_char(3, battery_50)
lcd.create_char(4, battery_25)
lcd.create_char(5, battery_0)

while True:
    lcd.clear()
    lcd.write_string(unichr(2))
    time.sleep(1)
    lcd.clear()
    lcd.write_string(unichr(3))
    time.sleep(1)
    lcd.clear()
    lcd.write_string(unichr(4))
    time.sleep(1)
    lcd.clear()
    lcd.write_string(unichr(5))
    time.sleep(1)

