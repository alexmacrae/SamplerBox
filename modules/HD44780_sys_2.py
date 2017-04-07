#########################################
##  LCD DISPLAY
#########################################

import globalvars as gv
import threading
import sys
import time

class LCD_SYS_2:

    def __init__(self):

        if gv.IS_DEBIAN:
            self.thread_sleep = 0.1
        else:
            self.thread_sleep = 0.2

        self.timeout_init = 3  # 3 sec
        self.timeout_init /= self.thread_sleep  # Adjust according to while loop sleep time
        self.timeout = self.timeout_init
        self.display_called = False

        if (gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD) and gv.IS_DEBIAN:

            import lcdcustomchars as lcdcc
            import RPi.GPIO as GPIO
            from RPLCD import CharLCD

            self.lcd = CharLCD(pin_rs=gv.GPIO_LCD_RS, pin_rw=None, pin_e=gv.GPIO_LCD_E,
                          pins_data=[gv.GPIO_LCD_D4, gv.GPIO_LCD_D5, gv.GPIO_LCD_D6, gv.GPIO_LCD_D7],
                          numbering_mode=GPIO.BCM, cols=gv.LCD_COLS, rows=gv.LCD_ROWS)

            self.lcd.create_char(1, lcdcc.block)
            self.lcd.create_char(2, lcdcc.arrow_right_01)
            self.lcd.create_char(3, lcdcc.voice_button_on)
            self.lcd.create_char(4, lcdcc.voice_button_off)

        if (gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD) and gv.SYSTEM_MODE == 2:

            self.STRING_1 = ''
            self.STRING_2 = ''

        self.LCDThread = threading.Thread(target=self.lcd_main)
        self.LCDThread.daemon = True
        self.LCDThread.start()

        # time.sleep(0.5)
        # display('Start SamplerBox') # bug: the way autochorder is loaded causes issue
        # time.sleep(0.5)


    def lcd_main(self):

        if gv.IS_DEBIAN:
            self.lcd.clear()

        self.lcd_string("WELCOME TO", 1)
        self.lcd_string("-=SAMPLERBOX=-", 2)
        time.sleep(1)

        while True:
            if self.display_called:
                if self.timeout > 0:
                    self.timeout -= 1
                else:
                    self.display_called = False
                    self.tempDisplay = False

                self.lcd_string(self.STRING_1, 1)
                self.lcd_string(self.STRING_2, 2)

            time.sleep(self.thread_sleep)

    def lcd_string(self, message, line):

        message = message.center(gv.LCD_COLS, " ")
        if gv.IS_DEBIAN:
            global lcd
            lcd._set_cursor_pos((line - 1, 0))
            lcd.write_string(message)


    def display(self, s2):

        if gv.USE_ALSA_MIXER:
            s1 = "%s %s %d%% %+d" % (gv.autochorder.CHORD_NAMES[gv.autochorder.current_chord], gv.sample_mode, gv.global_volume, gv.globaltranspose)
        else:
            s1 = "%s %s %+d" % (gv.autochorder.CHORD_NAMES[gv.autochorder.current_chord], gv.sample_mode, gv.globaltranspose)
            pass
        if s2 == "":
            if gv.currvoice > 1: s2 = str(gv.currvoice) + ":"
            s2 += str(gv.basename) + str(" " * gv.LCD_COLS)

            if gv.nav.buttfunc > 0:
                s2 = s2[:gv.LCD_COLS-2] + "*" + gv.nav.button_disp[gv.nav.buttfunc]
        else:
            s2 = s2 + ' ' * gv.LCD_COLS

        if gv.PRINT_LCD_MESSAGES:
            message = "%s || %s" % (s1[:gv.LCD_COLS], s2[:gv.LCD_COLS])
            # print "display: %s \\ %s" % (s1[:gv.LCD_COLS], s2[:gv.LCD_COLS])
            sys.stdout.write(message)
            sys.stdout.flush()
            if gv.USE_GUI:
                gui_message = message.replace('\r', '')
                gui_message = gui_message.replace(' || ', '\r')
                gv.gui.output['text'] = gui_message


        # lcd.message(s1 + " "*8 + "\n" + s2 + " "*15)
        # if gv.IS_DEBIAN:
        #     lcd.message(s1 + "\n" + s2)
        self.STRING_1 = str(s1[:gv.LCD_COLS])  # line 1
        self.STRING_2 = str(s2[:gv.LCD_COLS])  # line 2

        self.timeout = self.timeout_init
        self.display_called = True



