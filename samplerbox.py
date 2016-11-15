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

from modules import globalvars as gv
from modules import sound
from modules import loadsamples as ls
from modules import buttons
from modules import midicallback
from modules import displayer


###########################
# Start Displayer
# Load MIDI mappings
# Start the Navigator
###########################

gv.displayer = displayer.Displayer()

if gv.SYSTEM_MODE == 1:
    from modules import midimaps
    from modules import navigator_sys_1
    gv.midimaps = midimaps.MidiMapping().maps
    gv.nav = navigator_sys_1.Navigator(navigator_sys_1.PresetNav)
elif gv.SYSTEM_MODE == 2:
    from modules import navigator_sys_2
    gv.nav = navigator_sys_2





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

gv.displayer.disp_change(str_override='Running')


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
    gv.displayer.disp_change(str_override='Good bye!', line=1, timeout=1)
    gv.displayer.disp_change(str_override='Good bye!', line=2, timeout=1)
    gv.displayer.disp_change(str_override='Good bye!', line=3, timeout=1)
    gv.displayer.disp_change(str_override='Good bye!', line=4, timeout=1)
    sleep(0.2)
    if gv.IS_DEBIAN:
        import RPi.GPIO as GPIO
        GPIO.cleanup()

