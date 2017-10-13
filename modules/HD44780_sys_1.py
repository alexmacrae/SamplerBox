###########################
# HD44780 16x2 LCD MESSAGES
###########################

import globalvars as gv
import sys
import time
import threading
import lcdcustomchars as lcdcc


class LCD_SYS_1:
    def __init__(self):

        if gv.SYSTEM_MODE == 1 and (gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD):

            # Timing constants
            self.E_PULSE = 0.0005
            self.E_DELAY = 0.0005

            self.display_called = False
            self.temp_display = False

            if gv.IS_DEBIAN:
                self.thread_sleep = 0.05
            else:
                self.thread_sleep = 0.1

            self.timeout_init = 2  # default timeout reset time
            self.timeout_length = self.timeout_init  # initial timeout length (timeout_custom will override)

            self.STRING_1 = ''
            self.STRING_2 = ''
            self.STRING_3 = ''
            self.STRING_4 = ''
            self.STRING_1_PRIORITY = ''
            self.STRING_2_PRIORITY = ''
            self.STRING_3_PRIORITY = ''
            self.STRING_4_PRIORITY = ''

            self.loop_alive = True

            if gv.IS_DEBIAN:
                import RPi.GPIO as GPIO
                from RPLCD import CursorMode
                from RPLCD import CharLCD

                self.lcd = CharLCD(pin_rs=gv.GPIO_LCD_RS, pin_rw=None, pin_e=gv.GPIO_LCD_E,
                                   pins_data=[gv.GPIO_LCD_D4, gv.GPIO_LCD_D5, gv.GPIO_LCD_D6, gv.GPIO_LCD_D7],
                                   numbering_mode=GPIO.BCM, cols=gv.LCD_COLS, rows=gv.LCD_ROWS, charmap='A00')

                self.lcd.clear()

                # Hide the cursor
                self.lcd._set_cursor_mode(CursorMode.hide)

                # Fill the display with blank spaces
                for i in xrange(1, gv.LCD_ROWS+1):
                    self.lcd_string(' ', i)

                # Write custom codes to the LCD
                self.lcd.create_char(1, lcdcc.block)
                self.lcd.create_char(2, lcdcc.pause)
                self.lcd.create_char(3, lcdcc.voice_button_on)
                self.lcd.create_char(4, lcdcc.voice_button_off)
                self.lcd.create_char(5, lcdcc.block2)
                self.lcd.create_char(6, lcdcc.loading_hour_glass)

        self.LCDThread = threading.Thread(target=self.lcd_main)
        self.LCDThread.daemon = True
        self.LCDThread.start()

    def reset_after_timeout(self):
        self.display_called = False
        self.temp_display = False
        self.timeout_start = time.time()

    def lcd_main(self):

        if gv.USE_HD44780_20x4_LCD and gv.IS_DEBIAN:
            self.lcd.clear()

        # if gv.USE_HD44780_16x2_LCD:
        #     self.lcd_string("WELCOME TO".center(gv.LCD_COLS, ' '), 1)
        #     self.lcd_string("SAMPLERBOX".center(gv.LCD_COLS, ' '), 2)
        # elif gv.USE_HD44780_20x4_LCD:
        #     self.lcd_string(unichr(1) * gv.LCD_COLS, 1)
        #     self.lcd_string("WELCOME TO".center(gv.LCD_COLS, ' '), 2)
        #     self.lcd_string("SAMPLERBOX".center(gv.LCD_COLS, ' '), 3)
        #     self.lcd_string(unichr(1) * gv.LCD_COLS, 4)
        # time.sleep(0.6)

        self.timeout_start = time.time()
        print_message = ''

        while self.loop_alive:
            if self.display_called:

                now = time.time()

                if (now - self.timeout_start) > self.timeout_length:
                    self.reset_after_timeout()

                if (self.temp_display or gv.displayer.menu_mode == gv.displayer.DISP_UTILS_MODE):
                    self.lcd_string(self.STRING_1, 1)
                    self.lcd_string(self.STRING_2, 2)
                    print_message = "\r%s||%s" % (self.STRING_1[:gv.LCD_COLS], self.STRING_2[:gv.LCD_COLS])
                    if gv.USE_HD44780_20x4_LCD:
                        self.lcd_string(self.STRING_3, 3)
                        self.lcd_string(self.STRING_4, 4)
                        print_message = "\r%s||%s||%s" % (print_message, self.STRING_3[:gv.LCD_COLS], self.STRING_4[:gv.LCD_COLS])

                elif gv.displayer.menu_mode == gv.displayer.DISP_PRESET_MODE:
                    self.lcd_string(self.STRING_1_PRIORITY, 1)
                    self.lcd_string(self.STRING_2_PRIORITY, 2)
                    print_message = "\r%s||%s" % (self.STRING_1_PRIORITY[:gv.LCD_COLS], self.STRING_2_PRIORITY[:gv.LCD_COLS])
                    if gv.USE_HD44780_20x4_LCD:
                        self.lcd_string(self.STRING_3_PRIORITY, 3)
                        self.lcd_string(self.STRING_4_PRIORITY, 4)
                        print_message = "\r%s||%s||%s" % (print_message, self.STRING_3_PRIORITY[:gv.LCD_COLS], self.STRING_4_PRIORITY[:gv.LCD_COLS])
                elif gv.displayer.menu_mode == gv.displayer.DISP_MENU_MODE:
                    self.lcd_string(self.STRING_1_PRIORITY, 1)
                    self.lcd_string(self.STRING_2_PRIORITY, 2)
                    print_message = "\r%s||%s" % (self.STRING_1_PRIORITY[:gv.LCD_COLS], self.STRING_2_PRIORITY[:gv.LCD_COLS])
                    if gv.USE_HD44780_20x4_LCD:
                        self.lcd_string(self.STRING_3_PRIORITY, 3)
                        self.lcd_string(self.STRING_4_PRIORITY, 4)
                        print_message = "\r%s||%s||%s" % (print_message, self.STRING_3_PRIORITY[:gv.LCD_COLS], self.STRING_4_PRIORITY[:gv.LCD_COLS])
                if gv.PRINT_LCD_MESSAGES:
                    sys.stdout.write(print_message)
                    sys.stdout.flush()
                    gui_message = print_message.replace('\r', '')
                    gui_message = gui_message.replace('||', '\r')
                    if gv.USE_GUI and not gv.IS_DEBIAN: gv.gui.output['text'] = gui_message

            time.sleep(self.thread_sleep)

    def lcd_string(self, message, line):

        message = message[:gv.LCD_COLS]
        message = message.ljust(gv.LCD_COLS, " ")

        if (gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD) and gv.IS_DEBIAN:

            self.lcd.write_string(message[:gv.LCD_COLS])

    def display(self, message, line=1, is_priority=False, timeout_custom=None):

        message += ' ' * gv.LCD_COLS

        # Send string to display

        if line == 1:
            self.STRING_1 = message
            if is_priority:
                self.STRING_1_PRIORITY = message
            else:
                self.temp_display = True
        if line == 2:
            self.STRING_2 = message
            if is_priority:
                self.STRING_2_PRIORITY = message
            else:
                self.temp_display = True
        if line == 3:
            self.STRING_3 = message
            if is_priority:
                self.STRING_3_PRIORITY = message
            else:
                self.temp_display = True
        if line == 4:
            self.STRING_4 = message
            if is_priority:
                self.STRING_4_PRIORITY = message
            else:
                self.temp_display = True

        if timeout_custom != None:
            self.timeout_length = timeout_custom
        else:
            self.timeout_length = self.timeout_init

        self.timeout_start = time.time()

        self.display_called = True

    def stop(self):
        self.lcd.close()
        self.loop_alive = False

