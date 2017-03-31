#  SamplerBox2
#
#  author:          Joseph Ernest (twitter: @JosephErnest, mail: contact@samplerbox.org)
#  contributor:     Alex MacRae (alex.finlay.macrae@gmail.com)
#  url:             http://www.samplerbox.org/
#  license:         Creative Commons ShareAlike 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)
#
#  samplerbox2.py:  Main file
#

# TODO: if we're compiling a dist, bundled files such as config.ini can't be found, ie relative paths are affected

# import os, sys
# if 'Python' in  os.path.dirname(sys.executable):
#     env_basename = os.path.dirname(sys.executable)
# else:
#     env_basename = ''

#########################################
# IMPORT
# MODULES
#########################################
import time
usleep = lambda x: time.sleep(x / 1000000.0)
msleep = lambda x: time.sleep(x / 1000.0)
import threading
import rtmidi2
# from filters import FilterType, Filter, FilterChain
# from utility import byteToPCM, floatToPCM, pcmToFloat, sosfreqz
from modules import globalvars as gv
from modules import audiocontrols
from modules import displayer
from modules import buttons
from modules import systemfunctions
from modules import setlist
from modules import loadsamples

###########
# Logging #
###########

# TODO: not quite there yet

# import sys
# log_file = open("console.log", 'w')
log_file = None
# sys.stdout = log_file

#######################
# Start Displayer     #
# Load MIDI mappings  #
# Start the Navigator #
# Start the GUI       #
#######################
print '#### START SETLIST ####'
gv.setlist = setlist.Setlist()
print '####  END SETLIST  ####\n'

gv.ac = audiocontrols.AudioControls()
gv.autochorder = audiocontrols.AutoChorder()
gv.displayer = displayer.Displayer()
gv.sysfunc = systemfunctions.SystemFunctions()
gv.ls = loadsamples.LoadingSamples()
bnt = buttons.Buttons()
from modules import midicallback

if gv.SYSTEM_MODE == 1:
    from modules import midimaps
    from modules import navigator_sys_1
    gv.midimaps = midimaps.MidiMapping().maps
    gv.nav = navigator_sys_1.Navigator(navigator_sys_1.PresetNav)
elif gv.SYSTEM_MODE == 2:
    from modules import navigator_sys_2
    gv.nav = navigator_sys_2

import modules.gui as gui
if gv.USE_GUI and not gv.IS_DEBIAN: gv.gui = gui.SamplerBoxGUI() # Start the GUI

#########################################
##  MIDI IN via SERIAL PORT
##  this should be extended with logic for "midi running status"
##  possible solution at http://www.samplerbox.org/forum/146
#########################################

if gv.USE_SERIALPORT_MIDI:
    import serial

    ser = serial.Serial('/dev/ttyAMA0', baudrate=38400)  # see hack in /boot/cmline.txt : 38400 is 31250 baud for MIDI!

    def MidiSerialCallback():
        message = [0, 0, 0]
        while True:
            i = 0
            while i < 3:
                data = ord(ser.read(1))  # read a byte
                if data >> 7 != 0:
                    i = 0  # status byte!   this is the beginning of a midi message: http://www.midi.org/techspecs/midimessages.php
                message[i] = data
                i += 1
                if i == 2 and message[0] >> 4 == 12:  # program change: don't wait for a third byte: it has only 2 bytes
                    message[2] = 0
                    i = 3
            midicallback.MidiCallback(src='', message=message, time_stamp=None)

    MidiThread = threading.Thread(target=MidiSerialCallback)
    MidiThread.daemon = True
    MidiThread.start()

################################
# LOAD FIRST SAMPLE-SET/PRESET #
################################

gv.ls.LoadSamples()

##########################
# MIDI DEVICES DETECTION #
# MAIN LOOP              #
##########################

midi_in = rtmidi2.MidiInMulti()

curr_ports = []
prev_ports = []
first_loop = True

time.sleep(0.5)

try:
    def midi_devices_loop():
        global prev_ports, first_loop
        while True:
            no_playing_sounds = False
            for channel in xrange(16):
                if not gv.playingnotes[channel+1]:
                    no_playing_sounds = True
            if no_playing_sounds: # only check when there are no sounds
                curr_ports = rtmidi2.get_in_ports()
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
            time.sleep(0.2)

    if gv.USE_GUI and not gv.IS_DEBIAN:
        # MIDI device detection is threaded because Tkinter's loop is now the main loop
        LoadingInterrupt = False
        LoadingThread = threading.Thread(target=midi_devices_loop)
        LoadingThread.daemon = True
        LoadingThread.start()

        #########################
        # START GUI / MAIN LOOP #
        #########################

        if not gv.IS_DEBIAN:
            gv.gui.start_gui_loop()  # this is the main loop

    else:
        midi_devices_loop() # this is the main loop

except KeyboardInterrupt:
    print "\nstopped by ctrl-c\n"
except:
    print "\nstopped by Other Error"
finally:
    gv.sysfunc.shutdown(log_file)

