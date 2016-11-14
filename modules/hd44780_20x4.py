###########################
# HD44780 16x2 LCD MESSAGES
###########################

import globalvars as gv
import displayer

USE_LCD = gv.USE_HD44780_20x4_LCD

if gv.SYSTEM_MODE == 1 and USE_LCD:

    import threading
    import time
    import psutil
    import lcdcustomchars as lcdcc

    # Define some device constants
    LCD_COLS = 20  # Maximum characters per line
    LCD_ROWS = 4  # Maximum rows
    LCD_CHR = True
    LCD_CMD = False

    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

    LCD_CHARS = [0x40, 0x48, 0x50, 0x58, 0x60, 0x68, 0x70, 0x78]

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    displayCalled = False
    inPresetMode = True
    inSysMode = False
    inMenuMode = False
    tempDisplay = False

    if gv.IS_DEBIAN:
        WhileSleep = 0.02
    else:
        WhileSleep = 0.1

    timeout_init = 2  # default timeout reset time
    timeout_length = timeout_init # initial timeout length (timeout_custom will override)

    STRING_1 = ''
    STRING_2 = ''
    STRING_3 = ''
    STRING_4 = ''
    STRING_1_PRIORITY = ''
    STRING_2_PRIORITY = ''
    STRING_3_PRIORITY = ''
    STRING_4_PRIORITY = ''

    if USE_LCD and gv.IS_DEBIAN:
        import RPi.GPIO as GPIO
        from RPLCD import CharLCD

        lcd = CharLCD(pin_rs=gv.GPIO_LCD_RS, pin_rw=None, pin_e=gv.GPIO_LCD_E, pins_data=[gv.GPIO_LCD_D4, gv.GPIO_LCD_D5, gv.GPIO_LCD_D6, gv.GPIO_LCD_D7],
                      numbering_mode=GPIO.BCM, cols=LCD_COLS, rows=LCD_ROWS)

        # Write custom codes to the LCD
        lcd.create_char(1, lcdcc.block)
        lcd.create_char(2, lcdcc.arrow_right_01)
        lcd.create_char(3, lcdcc.voice_button_on)
        lcd.create_char(4, lcdcc.voice_button_off)


    def resetModes():
        global displayCalled, inPresetMode, inSysMode, inMenuMode, tempDisplay
        displayCalled = False
        inPresetMode = False
        inSysMode = False
        inMenuMode = False
        tempDisplay = False


    def makeVoiceButtons():
        button_str = ''
        for v in gv.voices:
            if (v == gv.currvoice - 1):
                button_str += unichr(3)
            else:
                button_str += unichr(4)
        return button_str


    def lcd_main():
        # Main program block
        global timeout_length, timeout_start, displayCalled, inPresetMode, tempDisplay
        if USE_LCD and gv.IS_DEBIAN:
            global lcd
            lcd.clear()

        lcd_string(unichr(1)*LCD_COLS, 1)
        lcd_string("WELCOME TO".center(LCD_COLS, ' '), 2)
        lcd_string("SAMPLERBOX".center(LCD_COLS, ' '), 3)
        lcd_string(unichr(1)*LCD_COLS, 4)

        time.sleep(1)

        timeout_start = time.time()

        while True:
            if displayCalled:
                now = time.time()

                if (now - timeout_start) > timeout_length:
                    displayCalled = False
                    tempDisplay = False

                if tempDisplay:
                    lcd_string(STRING_1, 1)
                    lcd_string(STRING_2, 2)
                    lcd_string(STRING_3, 3)
                    lcd_string(STRING_4, 4)

                elif displayer.menu_mode == displayer.DISP_PRESET_MODE:
                    lcd_string(STRING_1_PRIORITY[:LCD_COLS - 4] + makeVoiceButtons(), 1)
                    lcd_string(STRING_2_PRIORITY, 2)
                    lcd_string(STRING_3_PRIORITY, 3)
                    lcd_string(STRING_4_PRIORITY, 4)
                elif displayer.menu_mode == displayer.DISP_MENU_MODE:
                    lcd_string(STRING_1_PRIORITY, 1)
                    lcd_string(STRING_2_PRIORITY, 2)
                    lcd_string(STRING_3_PRIORITY, 3)
                    lcd_string(STRING_4_PRIORITY, 4)

                # elif displayer.menu_mode == displayer.DISP_UTILS_MODE:
                #     displayer.menu_mode = displayer.DISP_PRESET_MODE
                #     cpu = int(psutil.cpu_percent(None) / (LCD_COLS - 4)) + 1
                #     ram = int(float(psutil.virtual_memory().percent) / (LCD_COLS - 4)) + 1
                #     cpu_str = 'CPU' + (unichr(1) * cpu)
                #     ram_str = 'RAM' + (unichr(1) * ram)
                #
                #     lcd_string(cpu_str, 3, is_priority=False)
                #     lcd_string(ram_str, 4, is_priority=False)


                #     timeout_length = timeout_init
                #     for i in xrange(int(timeout_length)):
                #         cpu = int(psutil.cpu_percent(None) / (LCD_COLS - 4)) + 1
                #         ram = int(float(psutil.virtual_memory().percent) / (LCD_COLS - 4)) + 1
                #         lcd_string('CPU' + (unichr(1) * cpu), 3)
                #         lcd_string('RAM' + (unichr(1) * ram), 4)
                #         timeout_length -= 1
                #         time.sleep(WhileSleep)
                #         if not inSysMode:
                #             break
                #     if timeout_length == 0:
                #         resetModes()
                #         inPresetMode = True
                # else:
                #     lcd_string(STRING_1[:LCD_COLS - 4] + (unichr(4) * len(gv.voices)), 1)
                #     lcd_string(STRING_2, 2)
                #     lcd_string(STRING_3, 3)
                #     lcd_string(STRING_4, 4)

            time.sleep(WhileSleep)


    def lcd_string(message, line):

        if gv.PRINT_LCD_MESSAGES:
            print '{line ' + str(line) + '} -->  ' + message[:LCD_COLS]

        if USE_LCD and gv.IS_DEBIAN:
            global lcd
        message = message.ljust(LCD_COLS, " ")

        if USE_LCD and gv.IS_DEBIAN:
            lcd._set_cursor_pos((line - 1, 0))
            lcd.write_string(message[:LCD_COLS])



    def display(message, line=1, is_priority=False, timeout_custom=None):
        global STRING_1, STRING_2, STRING_3, STRING_4
        global STRING_1_PRIORITY, STRING_2_PRIORITY, STRING_3_PRIORITY, STRING_4_PRIORITY
        global displayCalled, timeout_length, timeout_start, tempDisplay


        message += '                '

        # Send string to display
        if line == 1:
            STRING_1 = message
            if is_priority:
                STRING_1_PRIORITY = message
            else:
                tempDisplay = True
        if line == 2:
            STRING_2 = message
            if is_priority:
                STRING_2_PRIORITY = message
            else:
                tempDisplay = True
        if line == 3:
            STRING_3 = message
            if is_priority:
                STRING_3_PRIORITY = message
            else:
                tempDisplay = True
        if line == 4:
            STRING_4 = message
            if is_priority:
                STRING_4_PRIORITY = message
            else:
                tempDisplay = True

        if timeout_custom != None:
            timeout_length = timeout_custom
        else:
            timeout_length = timeout_init

        timeout_start = time.time()


        displayCalled = True


    LCDThread = threading.Thread(target=lcd_main)
    LCDThread.daemon = True
    LCDThread.start()
