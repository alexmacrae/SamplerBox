###########################
# HD44780 16x2 LCD MESSAGES
###########################
import globalvars as gvars
import threading
import psutil
import time
import lcdcustomchars as lcdcc

USE_LCD = gvars.USE_HD44780_16x2_LCD
IS_DEB = gvars.IS_DEBIAN
LCD_DEBUG = gvars.LCD_DEBUG

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

LCD_CHARS = [0x40, 0x48, 0x50, 0x58, 0x60, 0x68, 0x70, 0x78]

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

displayCalled = False
inPresetMode = True
inSysMode = False
menuMode = False

if IS_DEB:
    WhileSleep = 0.1
else:
    WhileSleep = 0.5

TimeOutReset = 3  # 3 sec
TimeOutReset /= WhileSleep  # Adjust according to while loop sleep time
TimeOut = TimeOutReset
DisplaySamplerName = True
STRING_1 = ''
STRING_2 = ''
STRING_1_PRIORITY = ''
STRING_2_PRIORITY = ''

if USE_LCD and IS_DEB:
    import RPi.GPIO as GPIO
    from RPLCD import CharLCD, cleared, cursor

    lcd = CharLCD(pin_rs=LCD_RS, pin_rw=None, pin_e=LCD_E, pins_data=[LCD_D4, LCD_D5, LCD_D6, LCD_D7],
                  numbering_mode=GPIO.BCM, cols=16, rows=2)

    # Write custom codes to the LCD
    lcd.create_char(1, lcdcc.block)


def resetModes():
    global displayCalled, inPresetMode, inSysMode
    displayCalled = False
    inPresetMode = False
    inSysMode = False
    menuMode = False


def lcd_main():
    # Main program block
    global TimeOut, displayCalled, inPresetMode
    if USE_LCD and IS_DEB:
        global lcd
        lcd.clear()

    lcd_string("   WELCOME TO   ", 1)
    lcd_string(" -=SAMPLERBOX=- ", 2)
    time.sleep(1)

    while True:
        if displayCalled:
            for i in xrange(int(TimeOutReset)):
                lcd_string(STRING_1, 1)
                lcd_string(STRING_2, 2)
                time.sleep(WhileSleep)
            displayCalled = False

        elif inPresetMode:
            lcd_string(STRING_1_PRIORITY, 1)
            lcd_string(STRING_2_PRIORITY, 2)
        elif inSysMode:
            for i in xrange(int(TimeOutReset)):
                cpu = int(psutil.cpu_percent(None) / 12)
                ram = int(float(psutil.virtual_memory().percent) / 12)
                lcd_string('CPU ' + (unichr(1) * cpu), 1)
                lcd_string('RAM ' + (unichr(1) * ram), 2)
                time.sleep(WhileSleep)
                if not inSysMode:
                    break
            inPresetMode = True
        else:
            lcd_string(STRING_1, 1)
            lcd_string(STRING_2, 2)

        time.sleep(WhileSleep)


def lcd_string(message, line):
    # Send string to display
    global STRING_1, STRING_2
    if USE_LCD and IS_DEB:
        global lcd
    message = message.ljust(LCD_WIDTH, " ")

    if USE_LCD and IS_DEB:
        lcd._set_cursor_pos((line - 1, 0))
        lcd.write_string(message[:16])
    if LCD_DEBUG:
        print '{line ' + str(line) + '} -->  ' + message[:16]


def display(message, line, is_priority=False, customTimeout=None):
    global STRING_1, STRING_2, STRING_1_PRIORITY, STRING_2_PRIORITY, displayCalled, TimeOut

    displayCalled = True

    if customTimeout:
        TimeOut = customTimeout/WhileSleep
    else:
        TimeOut = TimeOutReset

    message += '                '

    # Send string to display
    if line == 1:
        STRING_1 = message
        if is_priority:
            STRING_1_PRIORITY = message
    if line == 2:
        STRING_2 = message
        if is_priority:
            STRING_2_PRIORITY = message


LCDThread = threading.Thread(target=lcd_main)
LCDThread.daemon = True
LCDThread.start()
