#########################################
##  LCD DISPLAY
#########################################

import globalvars as gv
import time
import threading

if gv.IS_DEBIAN:
    WhileSleep = 0.1
else:
    WhileSleep = 0.2

TimeOutReset = 3  # 3 sec
TimeOutReset /= WhileSleep  # Adjust according to while loop sleep time
TimeOut = TimeOutReset

LCD_COLS = 16
LCD_ROWS = 2

if gv.USE_HD44780_16x2_LCD and gv.IS_DEBIAN:

    import lcdcustomchars as lcdcc
    import RPi.GPIO as GPIO
    from RPLCD import CharLCD
    import time

    lcd = CharLCD(pin_rs=gv.GPIO_LCD_RS, pin_rw=None, pin_e=gv.GPIO_LCD_E,
                  pins_data=[gv.GPIO_LCD_D4, gv.GPIO_LCD_D5, gv.GPIO_LCD_D6, gv.GPIO_LCD_D7],
                  numbering_mode=GPIO.BCM, cols=LCD_COLS, rows=LCD_ROWS)

    lcd.create_char(1, lcdcc.block)
    lcd.create_char(2, lcdcc.arrow_right_01)
    lcd.create_char(3, lcdcc.voice_button_on)
    lcd.create_char(4, lcdcc.voice_button_off)


if gv.USE_HD44780_16x2_LCD  and gv.SYSTEM_MODE == 2:

    STRING_1 = ''
    STRING_2 = ''

    def lcd_main():
        # Main program block
        global TimeOut, displayCalled, inPresetMode, tempDisplay
        if gv.IS_DEBIAN:
            global lcd
            lcd.clear()

        lcd_string("WELCOME TO", 1)
        lcd_string("-=SAMPLERBOX=-", 2)
        time.sleep(1)

        while True:
            if displayCalled:
                if TimeOut > 0:
                    TimeOut -= 1
                else:
                    displayCalled = False
                    tempDisplay = False

                lcd_string(STRING_1, 1)
                lcd_string(STRING_2, 2)

            time.sleep(WhileSleep)



    def lcd_string(message, line):

        message = message.center(LCD_COLS, " ")
        lcd._set_cursor_pos((line - 1, 0))
        lcd.write_string(message)


    def display(s2):
        global STRING_1, STRING_2, TimeOut, displayCalled

        if gv.USE_ALSA_MIXER:
            s1 = "%s %s %d%% %+d" % (gv.chordname[gv.currchord], gv.sample_mode, gv.global_volume, gv.globaltranspose)
        else:
            s1 = "%s %s %+d" % (gv.chordname[gv.currchord], gv.sample_mode, gv.globaltranspose)
            pass
        if s2 == "":
            if gv.currvoice > 1: s2 = str(gv.currvoice) + ":"
            s2 += gv.basename + " " * LCD_COLS

            if gv.nav2.buttfunc > 0:
                s2 = s2[:LCD_COLS-2] + "*" + gv.nav2.button_disp[gv.nav2.buttfunc]
        else:
            s2 = s2 + ' ' * LCD_COLS

        if gv.PRINT_LCD_MESSAGES:
            print "display: %s \\ %s" % (s1[:LCD_COLS], s2[:LCD_COLS])
        # lcd.message(s1 + " "*8 + "\n" + s2 + " "*15)
        # if gv.IS_DEBIAN:
        #     lcd.message(s1 + "\n" + s2)
        STRING_1 = str(s1[:LCD_COLS])  # line 1
        STRING_2 = str(s2[:LCD_COLS])  # line 2

        TimeOut = TimeOutReset
        displayCalled = True


    LCDThread = threading.Thread(target=lcd_main)
    LCDThread.daemon = True
    LCDThread.start()





    #time.sleep(0.5)
    display('Start SamplerBox')
    #time.sleep(0.5)
    display('1Start SamplerBox')
    #time.sleep(0.5)
    display('2Start SamplerBox')
    #time.sleep(0.5)
    display('3Start SamplerBox')
    #time.sleep(0.5)


    #lcd.clear()
    time.sleep(0.5)
    display('Start SamplerBox')
    time.sleep(0.5)
