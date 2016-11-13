#########################################
##  LCD DISPLAY
##   - HD44780 class, based on 16x2 LCD interface code by Rahul Kar, see:
##     http://www.rpiblog.com/2012/11/interfacing-16x2-lcd-with-raspberry-pi.html
##   - Actual display routine
#########################################

import globalvars as gv
import time

class HD44780:
    # def __init__(self, pin_rs=7, pin_e=8, pins_db=[25,24,22,23,27,17,18,4]):
    def __init__(self, pin_rs=7, pin_e=8, pins_db=[27, 17, 18, 4]):

        # remove first 4 elements for 4-bit operation
        # and mind the physical wiring !
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)

        self.clear()

    def clear(self):
        """ Blank / Reset LCD """

        self.cmd(0x33)  # Initialization by instruction
        gv.msleep(5)
        self.cmd(0x33)
        gv.usleep(100)
        self.cmd(0x32)  # set to 4-bit mode
        self.cmd(0x28)  # Function set: 4-bit mode, 2 lines
        # self.cmd(0x38) # Function set: 8-bit mode, 2 lines
        self.cmd(0x0C)  # Display control: Display on, cursor off, cursor blink off
        self.cmd(0x06)  # Entry mode set: Cursor moves to the right
        self.cmd(0x01)  # Clear Display: Clears the display & set cursor position to line 1 column 0

    def cmd(self, bits, char_mode=False):
        """ Send command to LCD """

        time.sleep(0.001)
        bits = bin(bits)[2:].zfill(8)

        GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        # for i in range(8):       # use range 4 for 4-bit operation
        for i in range(4):  # use range 4 for 4-bit operation
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)

        GPIO.output(self.pin_e, True)
        gv.usleep(1)  # command needs to be > 450 nsecs to settle
        GPIO.output(self.pin_e, False)
        gv.usleep(100)  # command needs to be > 37 usecs to settle

        """ 4-bit operation start """
        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4, 8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i - 4], True)

        GPIO.output(self.pin_e, True)
        gv.usleep(1)  # command needs to be > 450 nsecs to settle
        GPIO.output(self.pin_e, False)
        gv.usleep(100)  # command needs to be > 37 usecs to settle
        """ 4-bit operation end """

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""

        self.cmd(0x01)  # Clear Display: Clears the display & set cursor position to line 1 column 0
        x = 0
        for char in text:
            if char == '\n':
                self.cmd(0xC0)  # next line
                x = 0
            else:
                x += 1
                if x < 17: self.cmd(ord(char), True)


if gv.USE_HD44780_16x2_LCD and gv.IS_DEBIAN:

    if gv.SYSTEM_MODE == 2:

        import RPi.GPIO as GPIO
        import time

        lcd = HD44780(gv.GPIO_LCD_RS, gv.GPIO_LCD_E, gv.GPIO_LCD_D4, gv.GPIO_LCD_D5, gv.GPIO_LCD_D6, gv.GPIO_LCD_D7)

if gv.USE_HD44780_16x2_LCD:

    def display(s2):
        # lcd.clear()

        if gv.USE_ALSA_MIXER:
            s1 = "%s %s %d%% %+d" % (gv.chordname[gv.currchord], gv.sample_mode, gv.global_volume, gv.globaltranspose)
        else:
            s1 = "%s %s %+d" % (gv.chordname[gv.currchord], gv.sample_mode, gv.globaltranspose)
        if s2 == "":
            if gv.currvoice > 1: s2 = str(gv.currvoice) + ":"
            s2 += gv.basename + " " * 15
            if gv.nav2.buttfunc > 0:
                s2 = s2[:14] + "*" + gv.nav2.button_disp[gv.nav2.buttfunc]

        if gv.PRINT_LCD_MESSAGES:
            print "display: %s \\ %s" % (s1, s2)
        # lcd.message(s1 + " "*8 + "\n" + s2 + " "*15)
        if gv.IS_DEBIAN:
            lcd.message(s1 + "\n" + s2)



    # lcd.clear()
    time.sleep(0.5)
    display('Start SamplerBox')
    time.sleep(0.5)



