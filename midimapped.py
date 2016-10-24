import rtmidi2
import time
from collections import OrderedDict
import midimapped_dict as mm_dict
import configparser
import numpy as np
import cPickle  # faster alternative


# CSV or json
# http://stackoverflow.com/questions/4893689/save-a-dictionary-to-a-file-alternative-to-pickle-in-python





# -----------------------------------------------------------

class Remapper:
    state = None
    mp = mm_dict.availableFunctions
    menuCoords = [0]
    menuPointer = 0
    function = None

    def __init__(self, initFunction):
        print 'init!'

        Remapper.state = initFunction
        Remapper.state = Remapper.state()
        # Remapper.menuPointer = Remapper.menuCoords[-1]
        # Remapper.menuPosition = self.getMenu()

    def loadState(self, theClass):
            Remapper.state = theClass()

    def left(self):
        pass
    def right(self):
        pass
    def enter(self):
        pass
    def cancel(self):
        pass

    def learn(self):
        print 'Learn init'

    def min(self, min, max):
        print 'Min init', min, max

    def max(self, min, max):
        print 'Max init', min, max

    def delete(self):
        print 'Delete init'

    def getMenu(self, mc = None):
        if not mc:
            mc = Remapper.menuCoords
        mp = Remapper.mp.get('submenu')
        i = 0
        while i < len(mc):
            if i > 0:
                mp = mp.get(mc[i-1]).get('submenu')
            i += 1
        return mp


# ______________________________________________________________________________

functionToMap = None

class MenuNav(Remapper):
    def __init__(self):
        self.menuPointer = self.menuCoords[-1]
        print self.getMenu().get(self.menuPointer).get('name')


    def left(self):

        if self.menuPointer > 0:
            self.menuPointer -= 1
            self.menuCoords[-1] = self.menuPointer
            print self.getMenu().get(self.menuPointer).get('name')
        else:
            print self.getMenu().get(self.menuPointer).get('name'), '(start)'

    def right(self):

        if self.menuPointer < len(self.getMenu()) -1:
            self.menuPointer += 1
            self.menuCoords[-1] = self.menuPointer
            print self.getMenu().get(self.menuPointer).get('name')
        else:
            print self.getMenu().get(self.menuPointer).get('name'), '(end)'

    def enter(self):
        global functionToMap
        menu = self.getMenu().get(self.menuPointer)
        try:
            if menu.has_key('submenu'):
                print 'Entering submenu for [' + menu.get('name') + ']'
                if menu.has_key('functionToMap'):
                    functionToMap = menu.get('functionToMap')
                self.menuCoords.append(0)
                self.loadState(MenuNav)
            if menu.has_key('fn'):
                Remapper.state = eval(menu.get('fn'))(functionToMap)

        except:
            pass

    def cancel(self):

        if len(self.menuCoords) > 1:
            self.menuCoords.pop()
            self.loadState(MenuNav)
        else:
            self.loadState(MenuNav)  # this will become the gvars.presets state



# ______________________________________________________________________________

learningMode = False

class Learn(Remapper):
    def __init__(self, functionToMap):
        global learningMode
        learningMode = True
        self.functionToMap = functionToMap
        self.learnedMidiMessage = None
        self.learnedMidiDevice = None

    def sendControlToMap(self, learnedMidiMessage, learnedMidiDevice):
        self.learnedMidiMessage = learnedMidiMessage
        self.learnedMidiDevice = learnedMidiDevice
        print learnedMidiMessage, learnedMidiDevice

    def enter(self):
        print 'Map:', self.learnedMidiMessage, self.learnedMidiDevice
        print 'To:', self.functionToMap







# ______________________________________________________________________________


devices = {
    'Launchkey 61 3': {
        'mapping': {
            176: {
                48: 'attack'
                # maybe a velocity range
            },
            144: {
                60: 1
            },
            128: {
                60: 1
            }
        }
    },
    'nanoKONTROL2 1': {
        'mapping': {
            176: {
                64: 'decay'
            }
        }
    }
}  # SAVE FOR LATER
# def save_obj(obj, name ):
#     with open(MIDI_CONFIG_FILE_PATH + name + '.pkl', 'wb') as f:
#         cPickle.dump(obj, f, 0)
#
#
# def load_obj(name):
#     with open(MIDI_CONFIG_FILE_PATH + name + '.pkl', 'rb') as f:
#         return cPickle.load(f)
#
# save_obj(devices, 'midimapping')
#
# newdevices = load_obj('midimapping')
#
# #print newdevices
#
# #print devices.keys()



##############


rm = Remapper(MenuNav)


############################
# ACTUAL DO STUFF FUNCTIONS
############################

def attack(val):
    print 'Attack:', val


def decay(val):
    print 'Decay:', val


def noteon(messagetype, note, vel):
    print messagetype, note, vel


def noteoff(messagetype, note, vel):
    print messagetype, note, vel


def setvolume(note, velocity):
    print 'Volume: ' + str(velocity) + ' (' + str(note) + ')'


#########################################
# MIDI CALLBACK
#########################################


def MidiCallback(src, message, time_stamp):
    cc_remapped = False

    messagetype = message[0] >> 4
    buttons = [48,49,50,65]

    if messagetype == 13:
        return

    messagechannel = (message[0] & 15) + 1

    note = message[1] if len(message) > 1 else None
    midinote = note
    velocity = message[2] if len(message) > 2 else None
    # if (messagetype != 14):
    # print "ch: " + str(messagechannel) + " type: " + str(messagetype) + " raw: " + str(message) + " SRC: " + str(src)
    # print message


    if learningMode and note not in buttons:

         Remapper.state.sendControlToMap(message, src)

    else:


        try:
            if (devices.get(src).get('mapping').get(message[0]).has_key(note)):
                key = devices.get(src).get('mapping').get(message[0])
                # remap note to a function
                if isinstance(key.get(note), str):
                    eval(key.get(note))(velocity)  # eval the string as a function name, and call it
                    cc_remapped = True
                # remap note to a key
                elif isinstance(key.get(note), int):
                    note = key.get(note)

        except:
            pass

        # Default CC mapping
        if not cc_remapped and messagetype != 9 and messagetype != 8 and messagetype == 11:

            if (note == 7):
                setvolume(note, velocity)


                # print 'CC not remapped'

        # Note on
        if messagetype == 9:  # WARNING - a remapped note might be coming from a CC messagetype
            noteon(messagetype, note, velocity)

        # Note off
        elif messagetype == 8:
            noteoff(messagetype, note, velocity)


        elif messagetype == 12:  # Program change
            print 'Program change ' + str(note)


            # special keys from Kurzweil
            # if len(message) == 1 and message[0] == 250:  # playbutton Kurzweil
            #     StartTrack()
            #
            # if len(message) == 1 and message[0] == 252: # stopbutton Kurzweil
            #     StopTrack()

        if (note == 49):  # Enter button
            if (velocity == 127):
                if rm:
                    rm.state.enter()

        if (note == 48):  # Left arrow button
            if (velocity == 127):
                rm.state.left()

        if (note == 50):  # Right arrow button
            if (velocity == 127):
                rm.state.right()

        if (note == 65):  # Cancel button
            if (velocity == 127):
                rm.state.cancel()


#########################################
# MIDI DEVICES DETECTION
# MAIN LOOP
#########################################

stopit = False

midi_in = rtmidi2.MidiInMulti()  # .open_ports("*")

curr_ports = []
prev_ports = []
first_loop = True

try:
    while True:
        # System info
        # print 'CPU: '+ str (psutil.cpu_percent(None)) + '%', 'MEM: ' + str(float(psutil.virtual_memory().percent)) + '%'

        if stopit:
            break
        curr_ports = rtmidi2.get_in_ports()
        # print curr_ports
        if (len(prev_ports) != len(curr_ports)):
            midi_in.close_ports()
            prev_ports = []

        for port in curr_ports:

            if port not in prev_ports and 'Midi Through' not in port and (
                    len(prev_ports) != len(curr_ports) and 'LoopBe Internal' not in port):
                midi_in.open_ports(port)
                midi_in.callback = MidiCallback
                if first_loop:
                    print 'Opened MIDI port: ' + port
                else:
                    print 'Reopening MIDI port: ' + port
        prev_ports = curr_ports
        first_loop = False

        time.sleep(2)
except KeyboardInterrupt:
    print "\nstopped by ctrl-c\n"
except:
    print "Other Error"
finally:
    print 'Seeya!'
