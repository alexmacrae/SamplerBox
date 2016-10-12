###########################
# HD44780 16x2 LCD MESSAGES
###########################
import globalvars as gvars

if gvars.USE_HD44780_16x2_LCD and gvars.IS_DEBIAN:
    import RPi.GPIO as GPIO
    import time
    import threading
    import psutil

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

    def lcd_custom(charPos, charDef):
        lcd_byte(LCD_CHARS[charPos], LCD_CMD)
        for line in charDef:
            lcd_byte(line, LCD_CHR)


    def lcd_main():
        # Main program block
        global TimeOutReset, TimeOut, DisplaySamplerName, display_called

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
        GPIO.setup(LCD_E, GPIO.OUT)  # E
        GPIO.setup(LCD_RS, GPIO.OUT)  # RS
        GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
        GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
        GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
        GPIO.setup(LCD_D7, GPIO.OUT)  # DB7

        # Initialise display
        lcd_init()
        sleep_time = 0.01

        lcd_string("   WELCOME TO   ", LCD_LINE_1)
        lcd_string(" -=SAMPLERBOX=- ", LCD_LINE_2)
        time.sleep(1)
        lcd_string("[              ]", LCD_LINE_1)
        lcd_string("[              ]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[=             ]", LCD_LINE_1)
        lcd_string("[             =]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[==            ]", LCD_LINE_1)
        lcd_string("[            ==]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[===           ]", LCD_LINE_1)
        lcd_string("[           ===]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[====          ]", LCD_LINE_1)
        lcd_string("[          ====]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[=====         ]", LCD_LINE_1)
        lcd_string("[         =====]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[======        ]", LCD_LINE_1)
        lcd_string("[        ======]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[=======       ]", LCD_LINE_1)
        lcd_string("[       =======]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[========      ]", LCD_LINE_1)
        lcd_string("[      ========]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[=========     ]", LCD_LINE_1)
        lcd_string("[     =========]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[==========    ]", LCD_LINE_1)
        lcd_string("[    ==========]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[===========   ]", LCD_LINE_1)
        lcd_string("[   ===========]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[============  ]", LCD_LINE_1)
        lcd_string("[  ============]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[============= ]", LCD_LINE_1)
        lcd_string("[ =============]", LCD_LINE_2)
        time.sleep(sleep_time)
        lcd_string("[==============]", LCD_LINE_1)
        lcd_string("[==============]", LCD_LINE_2)
        time.sleep(sleep_time)

        lcd_init()
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

            time.sleep(0.2)


    def lcd_init():
        # Initialise display
        lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
        lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
        lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
        lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
        lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
        lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        time.sleep(E_DELAY)


    def lcd_byte(bits, mode):
        # Send byte to data pins
        # bits = data
        # mode = True  for character
        #        False for command
        GPIO.output(LCD_RS, mode)  # RS

        # High bits
        GPIO.output(LCD_D4, False)
        GPIO.output(LCD_D5, False)
        GPIO.output(LCD_D6, False)
        GPIO.output(LCD_D7, False)
        if bits & 0x10 == 0x10:
            GPIO.output(LCD_D4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(LCD_D5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(LCD_D6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(LCD_D7, True)

        # Toggle 'Enable' pin
        lcd_toggle_enable()

        # Low bits
        GPIO.output(LCD_D4, False)
        GPIO.output(LCD_D5, False)
        GPIO.output(LCD_D6, False)
        GPIO.output(LCD_D7, False)
        if bits & 0x01 == 0x01:
            GPIO.output(LCD_D4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(LCD_D5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(LCD_D6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(LCD_D7, True)

        # Toggle 'Enable' pin
        lcd_toggle_enable()


    def lcd_toggle_enable():
        # Toggle enable
        time.sleep(E_DELAY)
        GPIO.output(LCD_E, True)
        time.sleep(E_PULSE)
        GPIO.output(LCD_E, False)
        time.sleep(E_DELAY)


    def lcd_string(message, line):
        # Send string to display

        message = message.ljust(LCD_WIDTH, " ")

        lcd_byte(line, LCD_CMD)

        for i in range(LCD_WIDTH):
            lcd_byte(ord(message[i]), LCD_CHR)


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
