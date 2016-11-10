#  SamplerBox2
#
#  author:          Joseph Ernest (twitter: @JosephErnest, mail: contact@samplerbox.org)
#  contributor:     Alex MacRae (alex.finlay.macrae@gmail.com)
#  url:             http://www.samplerbox.org/
#  license:         Creative Commons ShareAlike 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)
#
#  samplerbox2.py:  Main file
#

#########################################
# IMPORT
# MODULES
#########################################
import time
usleep = lambda x: time.sleep(x / 1000000.0)
msleep = lambda x: time.sleep(x / 1000.0)
#import curses
import threading
import rtmidi2               # Use rtmidi2 instead. Make sure when installing rtmidi2 to change RPI date: $sudo date -s "Sept 23 18:31 2016". Then installing takes a while

#from filters import FilterType, Filter, FilterChain
#from utility import byteToPCM, floatToPCM, pcmToFloat, sosfreqz
from collections import OrderedDict
from time import sleep

import globalvars as gv
import sound
import loadsamples as ls
import navigator
import lcd
import buttons
import midicallback
import midimaps

###########################
# Load MIDI mappings
# Start the Navigator
###########################

gv.midimaps = midimaps.MidiMapping().maps
gv.nav = navigator.Navigator(navigator.PresetNav)

#########################################
##  based on 16x2 LCD interface code by Rahul Kar, see:
##  http://www.rpiblog.com/2012/11/interfacing-16x2-lcd-with-raspberry-pi.html
#########################################

# class HD44780:
#
#     def __init__(self, pin_rs=7, pin_e=8, pins_db=[25, 24, 23, 18]):
#         self.pin_rs = pin_rs
#         self.pin_e = pin_e
#         self.pins_db = pins_db
#
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(self.pin_e, GPIO.OUT)
#         GPIO.setup(self.pin_rs, GPIO.OUT)
#         for pin in self.pins_db:
#             GPIO.setup(pin, GPIO.OUT)
#
#         self.clear()
#
#     def clear(self):
#         """ Blank / Reset LCD """
#
#         self.cmd(0x33) # Initialization by instruction
#         msleep(5)
#         self.cmd(0x33)
#         usleep(100)
#         self.cmd(0x32) # set to 4-bit mode
#         self.cmd(0x28) # Function set: 4-bit mode, 2 lines
#         #self.cmd(0x38) # Function set: 8-bit mode, 2 lines
#         self.cmd(0x0C) # Display control: Display on, cursor off, cursor blink off
#         self.cmd(0x06) # Entry mode set: Cursor moves to the right
#         self.cmd(0x01) # Clear Display: Clear & set cursor position to line 1 column 0
#
#     def cmd(self, bits, char_mode=False):
#         """ Send command to LCD """
#
#         sleep(0.002)
#         bits = bin(bits)[2:].zfill(8)
#
#         GPIO.output(self.pin_rs, char_mode)
#
#         for pin in self.pins_db:
#             GPIO.output(pin, False)
#
#         #for i in range(8):       # use range 4 for 4-bit operation
#         for i in range(4):       # use range 4 for 4-bit operation
#             if bits[i] == "1":
#                 GPIO.output(self.pins_db[::-1][i], True)
#
#         GPIO.output(self.pin_e, True)
#         usleep(1)      # command needs to be > 450 nsecs to settle
#         GPIO.output(self.pin_e, False)
#         usleep(100)    # command needs to be > 37 usecs to settle
#
#         """ 4-bit operation start """
#         for pin in self.pins_db:
#             GPIO.output(pin, False)
#
#         for i in range(4, 8):
#             if bits[i] == "1":
#                 GPIO.output(self.pins_db[::-1][i-4], True)
#
#         GPIO.output(self.pin_e, True)
#         usleep(1)      # command needs to be > 450 nsecs to settle
#         GPIO.output(self.pin_e, False)
#         usleep(100)    # command needs to be > 37 usecs to settle
#         """ 4-bit operation end """
#
#     def message(self, text):
#         """ Send string to LCD. Newline wraps to second line"""
#
#         self.cmd(0x02) # Home Display: set cursor position to line 1 column 0
#         x = 0
#         for char in text:
#             if char == '\n':
#                 self.cmd(0xC0) # next line
#                 x = 0
#             else:
#                 x += 1
#                 if x < 17: self.cmd(ord(char), True)
#



#########################################
##  MIDI IN via SERIAL PORT
##  this should be extended with logic for "midi running status"
##  possible solution at http://www.samplerbox.org/forum/146
#########################################

if gv.USE_SERIALPORT_MIDI:
    import serial

    ser = serial.Serial('/dev/ttyAMA0', baudrate=38400)       # see hack in /boot/cmline.txt : 38400 is 31250 baud for MIDI!

    def MidiSerialCallback():
        message = [0, 0, 0]
        while True:
          i = 0
          while i < 3:
            data = ord(ser.read(1)) # read a byte
            if data >> 7 != 0:
              i = 0      # status byte!   this is the beginning of a midi message: http://www.midi.org/techspecs/midimessages.php
            message[i] = data
            i += 1
            if i == 2 and message[0] >> 4 == 12:  # program change: don't wait for a third byte: it has only 2 bytes
              message[2] = 0
              i = 3
          midicallback.MidiCallback(src='', message=message, time_stamp=None)

    MidiThread = threading.Thread(target = MidiSerialCallback)
    MidiThread.daemon = True
    MidiThread.start()



#########################################
# LOAD FIRST SOUNDBANK
#########################################

ls.LoadSamples()

#########################################
# MIDI DEVICES DETECTION
# MAIN LOOP
#########################################

midi_in = rtmidi2.MidiInMulti()

curr_ports = []
prev_ports = []
first_loop = True

lcd.display('Running', 1)


try:
    while True:
        curr_ports = rtmidi2.get_in_ports()
        #print curr_ports
        if (len(prev_ports) != len(curr_ports)):
            print '\n==== START GETTING MIDI DEVICES ===='
            midi_in.close_ports()
            prev_ports = []
            for port in curr_ports:
                if port not in prev_ports and 'Midi Through' not in port and (len(prev_ports) != len(curr_ports) and 'LoopBe Internal' not in port):
                    midi_in.open_ports(port)
                    midi_in.callback = midicallback.MidiCallback
                    if first_loop:
                        print 'Opened MIDI port: ' + port
                    else:
                        print 'Reopening MIDI port: ' + port
            print '====  END GETTING MIDI DEVICES  ====\n'
        prev_ports = curr_ports
        first_loop = False
        time.sleep(2)
except KeyboardInterrupt:
  print "\nstopped by ctrl-c\n"
except:
  print "\nstopped by Other Error"
finally:
    lcd.display('  -=STOPPED=-   ', 1)
    lcd.display(unichr(2)*lcd.LCD_COLS, 2)
    sleep(0.5)
    if gv.IS_DEBIAN:
        import RPi.GPIO as GPIO
        GPIO.cleanup()

