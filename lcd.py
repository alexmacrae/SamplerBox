###########################
# HD44780 16x2 LCD MESSAGES
###########################
import globalvars as gvars

if gvars.USE_HD44780_16x2_LCD and gvars.IS_DEBIAN:
    import RPi.GPIO as GPIO
    from RPLCD import CharLCD, cleared, cursor
    import time
    import threading
    import psutil
    import time

    # Define GPIO to LCD mapping
    LCD_RS = 7
    LCD_E = 8
    LCD_D4 = 27
    LCD_D5 = 17
    LCD_D6 = 18
    LCD_D7 = 4

    # Define some device constants
    LCD_WIDTH = 16  # Maximum characters per line
    LCD_CHR = True
    LCD_CMD = False

    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
    STRING_1   = ''
    STRING_2   = ''
    LCD_CHARS = [0x40, 0x48, 0x50, 0x58, 0x60, 0x68, 0x70, 0x78]

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    display_called = False

    TimeOutReset = 10  # 3 sec
    TimeOut = TimeOutReset
    DisplaySamplerName = True


    lcd = CharLCD(pin_rs=LCD_RS, pin_rw=None, pin_e=LCD_E, pins_data=[LCD_D4, LCD_D5, LCD_D6, LCD_D7],
                  numbering_mode=GPIO.BCM, cols=16, rows=2)




    def lcd_main():
        # Main program block
        global TimeOutReset, TimeOut, DisplaySamplerName, display_called, lcd

        # Initialise display
        lcd.clear()
        sleep_time = 0.01

        lcd_string("   WELCOME TO   ", LCD_LINE_1)
        lcd_string(" -=SAMPLERBOX=- ", LCD_LINE_2)
        time.sleep(1)

        while True:

            if display_called:
                lcd_string(STRING_1, LCD_LINE_1)
                lcd_string(STRING_2, LCD_LINE_2)
                if TimeOut > 0:
                    TimeOut -= 1
                else:
                    TimeOut = TimeOutReset
                    display_called = False

            else:
                lcd_string('CPU usage: ' + str(psutil.cpu_percent(None)) + '%', LCD_LINE_1)
                lcd_string('RAM usage: ' + str(float(psutil.virtual_memory().percent)) + "%", LCD_LINE_2)

            time.sleep(1)



    def lcd_string(message, line):
        # Send string to display
        global lcd, STRING_1, STRING_2

        message = message.ljust(LCD_WIDTH, " ")

        if line == 1 or line == LCD_LINE_1:
            lcd._set_cursor_pos((0, 0))
            lcd.write_string(message[:16])
            lcd._set_cursor_pos((1, 0))
            lcd.write_string(STRING_2[:16])
            print message[:16], STRING_2[:16]

        if line == 2 or line == LCD_LINE_2:
            lcd._set_cursor_pos((0, 0))
            lcd.write_string(STRING_1[:16])
            lcd._set_cursor_pos((1, 0))
            lcd.write_string(message[:16])
            print STRING_1[:16], message[:16]



    def display(message, line=LCD_LINE_1):
        global STRING_1, STRING_2, display_called, TimeOut, TimeOutReset

        display_called = True
        TimeOut = TimeOutReset

        # Send string to display
        if line == 1 or line == LCD_LINE_1:
            STRING_1 = message
        if line == 2 or line == LCD_LINE_2:
            STRING_2 = message




    LCDThread2 = threading.Thread(target=lcd_main)
    LCDThread2.daemon = True
    LCDThread2.start()


else:
    def display(message, line=1):
        if gvars.LCD_DEBUG:
            print message, line
        else:
            pass
