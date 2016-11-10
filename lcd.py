###########################
# HD44780 16x2 LCD MESSAGES
###########################
import globalvars as gv
import threading
import psutil
import time
import lcdcustomchars as lcdcc

USE_LCD = gv.USE_HD44780_16x2_LCD

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
    WhileSleep = 0.05
else:
    WhileSleep = 0.2

TimeOutReset = 3  # 3 sec
TimeOutReset /= WhileSleep  # Adjust according to while loop sleep time
TimeOut = TimeOutReset
DisplaySamplerName = True
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
    from RPLCD import CharLCD, cleared, cursor

    lcd = CharLCD(pin_rs=gv.LCD_RS, pin_rw=None, pin_e=gv.LCD_E, pins_data=[gv.LCD_D4, gv.LCD_D5, gv.LCD_D6, gv.LCD_D7],
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


def getTimeOut():
    return TimeOut


def lcd_main():
    # Main program block
    global TimeOut, displayCalled, inPresetMode, tempDisplay
    if USE_LCD and gv.IS_DEBIAN:
        global lcd
        lcd.clear()

    lcd_string("   WELCOME TO   ", 1)
    lcd_string(" -=SAMPLERBOX=- ", 2)
    lcd_string("", 3)
    lcd_string("", 4)
    time.sleep(1)

    while True:
        if displayCalled:
            if TimeOut > 0:
                TimeOut -= 1
            else:
                displayCalled = False
                tempDisplay = False

            if tempDisplay:
                lcd_string(STRING_1, 1)
                lcd_string(STRING_2, 2)
                lcd_string(STRING_3, 3)
                lcd_string(STRING_4, 4)

            elif inPresetMode:
                lcd_string(STRING_1_PRIORITY[:LCD_COLS - 4] + makeVoiceButtons(), 1)
                lcd_string(STRING_2_PRIORITY, 2)
                lcd_string(STRING_3_PRIORITY, 3)
                lcd_string(STRING_4_PRIORITY, 4)
            elif inMenuMode:
                lcd_string(STRING_1_PRIORITY, 1)
                lcd_string(STRING_2_PRIORITY, 2)
                lcd_string(STRING_3_PRIORITY, 3)
                lcd_string(STRING_4_PRIORITY, 4)

            elif inSysMode:
                TimeOut = TimeOutReset
                for i in xrange(int(TimeOut)):
                    cpu = int(psutil.cpu_percent(None) / (LCD_COLS - 4)) + 1
                    ram = int(float(psutil.virtual_memory().percent) / (LCD_COLS - 4)) + 1
                    lcd_string('CPU' + (unichr(1) * cpu), 3)
                    lcd_string('RAM' + (unichr(1) * ram), 4)
                    TimeOut -= 1
                    time.sleep(WhileSleep)
                    if not inSysMode:
                        break
                if TimeOut == 0:
                    resetModes()
                    inPresetMode = True
            else:
                lcd_string(STRING_1[:LCD_COLS - 4] + (unichr(4) * len(gv.voices)), 1)
                lcd_string(STRING_2, 2)
                lcd_string(STRING_3, 3)
                lcd_string(STRING_4, 4)

        time.sleep(WhileSleep)


def lcd_string(message, line):
    # Send string to display
    # global STRING_1, STRING_2, STRING_3, STRING_4
    if USE_LCD and gv.IS_DEBIAN:
        global lcd
    message = message.ljust(LCD_COLS, " ")

    if USE_LCD and gv.IS_DEBIAN:
        lcd._set_cursor_pos((line - 1, 0))
        lcd.write_string(message[:LCD_COLS])



def display(message, line=1, is_priority=False, customTimeout=None):
    global STRING_1, STRING_2, STRING_3, STRING_4, STRING_1_PRIORITY, STRING_2_PRIORITY, STRING_3_PRIORITY, STRING_4_PRIORITY
    global displayCalled, TimeOut, tempDisplay

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

    if customTimeout != None:
        TimeOut = customTimeout / WhileSleep
    else:
        TimeOut = TimeOutReset

    if gv.LCD_PRINT:
        print '{line ' + str(line) + '} -->  ' + message[:LCD_COLS]

    displayCalled = True



LCDThread = threading.Thread(target=lcd_main)
LCDThread.daemon = True
LCDThread.start()
