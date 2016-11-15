###########################
# HD44780 16x2 LCD MESSAGES
###########################

import globalvars as gv
import displayer

if gv.SYSTEM_MODE == 1 and (gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD):

    import threading
    import time
    import lcdcustomchars as lcdcc

    LCD_CHR = True
    LCD_CMD = False

    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

    LCD_CHARS = [0x40, 0x48, 0x50, 0x58, 0x60, 0x68, 0x70, 0x78]

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    display_called = False
    temp_display = False

    if gv.IS_DEBIAN:
        thread_sleep = 0.02
    else:
        thread_sleep = 0.1

    timeout_init = 2  # default timeout reset time
    timeout_length = timeout_init  # initial timeout length (timeout_custom will override)

    STRING_1 = ''
    STRING_2 = ''
    STRING_3 = ''
    STRING_4 = ''
    STRING_1_PRIORITY = ''
    STRING_2_PRIORITY = ''
    STRING_3_PRIORITY = ''
    STRING_4_PRIORITY = ''

    if gv.IS_DEBIAN:
        import RPi.GPIO as GPIO
        from RPLCD import CharLCD

        lcd = CharLCD(pin_rs=gv.GPIO_LCD_RS, pin_rw=None, pin_e=gv.GPIO_LCD_E,
                      pins_data=[gv.GPIO_LCD_D4, gv.GPIO_LCD_D5, gv.GPIO_LCD_D6, gv.GPIO_LCD_D7],
                      numbering_mode=GPIO.BCM, cols=gv.LCD_COLS, rows=gv.LCD_ROWS)

        # Write custom codes to the LCD
        lcd.create_char(1, lcdcc.block)
        lcd.create_char(2, lcdcc.arrow_right_01)
        lcd.create_char(3, lcdcc.voice_button_on)
        lcd.create_char(4, lcdcc.voice_button_off)


    def reset_after_timeout():
        global display_called, temp_display
        display_called = False
        temp_display = False


    def make_voice_buttons():
        button_str = ''
        for v in gv.voices:
            if (v == gv.currvoice - 1):
                button_str += unichr(3)
            else:
                button_str += unichr(4)
        return button_str


    def lcd_main():
        global timeout_length, timeout_start, display_called, temp_display
        
        if gv.USE_HD44780_20x4_LCD and gv.IS_DEBIAN:
            global lcd
            lcd.clear()


        if gv.USE_HD44780_16x2_LCD:
            lcd_string("WELCOME TO".center(gv.LCD_COLS, ' '), 1)
            lcd_string("SAMPLERBOX".center(gv.LCD_COLS, ' '), 2)
        if gv.USE_HD44780_20x4_LCD:
            lcd_string(unichr(1) * gv.LCD_COLS, 1)
            lcd_string("WELCOME TO".center(gv.LCD_COLS, ' '), 2)
            lcd_string("SAMPLERBOX".center(gv.LCD_COLS, ' '), 3)
            lcd_string(unichr(1) * gv.LCD_COLS, 4)

        time.sleep(1)

        timeout_start = time.time()

        while True:
            if display_called:
                now = time.time()

                if (now - timeout_start) > timeout_length:
                    reset_after_timeout()

                if temp_display or displayer.menu_mode == displayer.DISP_UTILS_MODE:
                    lcd_string(STRING_1, 1)
                    lcd_string(STRING_2, 2)
                    if gv.USE_HD44780_20x4_LCD:
                        lcd_string(STRING_3, 3)
                        lcd_string(STRING_4, 4)

                elif displayer.menu_mode == displayer.DISP_PRESET_MODE:
                    lcd_string(STRING_1_PRIORITY[:gv.LCD_COLS - 4] + make_voice_buttons(), 1)
                    lcd_string(STRING_2_PRIORITY, 2)
                    if gv.USE_HD44780_20x4_LCD:
                        lcd_string(STRING_3_PRIORITY, 3)
                        lcd_string(STRING_4_PRIORITY, 4)
                elif displayer.menu_mode == displayer.DISP_MENU_MODE:
                    lcd_string(STRING_1_PRIORITY, 1)
                    lcd_string(STRING_2_PRIORITY, 2)
                    if gv.USE_HD44780_20x4_LCD:
                        lcd_string(STRING_3_PRIORITY, 3)
                        lcd_string(STRING_4_PRIORITY, 4)

            time.sleep(thread_sleep)


    def lcd_string(message, line):

        if gv.PRINT_LCD_MESSAGES:
            print '{line ' + str(line) + '} -->  ' + message[:gv.LCD_COLS]

        message = message.ljust(gv.LCD_COLS, " ")

        if (gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD) and gv.IS_DEBIAN:
            global lcd
            lcd._set_cursor_pos((line - 1, 0))
            lcd.write_string(message[:gv.LCD_COLS])


    def display(message, line=1, is_priority=False, timeout_custom=None):
        global STRING_1, STRING_2, STRING_3, STRING_4
        global STRING_1_PRIORITY, STRING_2_PRIORITY, STRING_3_PRIORITY, STRING_4_PRIORITY
        global display_called, timeout_length, timeout_start, temp_display

        message += '                '

        # Send string to display
        if line == 1:
            STRING_1 = message
            if is_priority:
                STRING_1_PRIORITY = message
            else:
                temp_display = True
        if line == 2:
            STRING_2 = message
            if is_priority:
                STRING_2_PRIORITY = message
            else:
                temp_display = True
        if line == 3:
            STRING_3 = message
            if is_priority:
                STRING_3_PRIORITY = message
            else:
                temp_display = True
        if line == 4:
            STRING_4 = message
            if is_priority:
                STRING_4_PRIORITY = message
            else:
                temp_display = True

        if timeout_custom != None:
            timeout_length = timeout_custom
        else:
            timeout_length = timeout_init

        timeout_start = time.time()

        display_called = True


    LCDThread = threading.Thread(target=lcd_main)
    LCDThread.daemon = True
    LCDThread.start()
