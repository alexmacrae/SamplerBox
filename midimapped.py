import rtmidi2
import time
from collections import OrderedDict
import menudict as mm_dict
import configparser
import numpy as np
import cPickle  # faster alternative


# CSV or json
# http://stackoverflow.com/questions/4893689/save-a-dictionary-to-a-file-alternative-to-pickle-in-python





# -----------------------------------------------------------

class Navigator:
    state = None
    mp = mm_dict.menu
    menuCoords = [0]
    menuPointer = 0
    function = None

    def __init__(self, initFunction):
        print 'init!'

        Navigator.state = initFunction
        Navigator.state = Navigator.state()
        # Navigator.menuPointer = Navigator.menuCoords[-1]
        # Navigator.menuPosition = self.getMenu()

    def loadState(self, theClass):
        Navigator.state = theClass()

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

    def getMenu(self, mc=None):
        if not mc:
            mc = Navigator.menuCoords
        mp = Navigator.mp.get('submenu')
        i = 0
        while i < len(mc):
            if i > 0:
                mp = mp.get(mc[i - 1]).get('submenu')
            i += 1
        return mp


# ______________________________________________________________________________

functionToMap = None
functionNiceName = None


class MenuNav(Navigator):
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

        if self.menuPointer < len(self.getMenu()) - 1:
            self.menuPointer += 1
            self.menuCoords[-1] = self.menuPointer
            print self.getMenu().get(self.menuPointer).get('name')
        else:
            print self.getMenu().get(self.menuPointer).get('name'), '(end)'

    def enter(self):
        global functionToMap, functionNiceName
        menu = self.getMenu().get(self.menuPointer)
        try:
            if menu.has_key('submenu'):
                print 'Entering submenu for [' + menu.get('name') + ']'
                if menu.has_key('functionToMap'):
                    functionToMap = menu.get('functionToMap')
                    functionNiceName = menu.get('name')
                self.menuCoords.append(0)
                self.loadState(MenuNav)
            if menu.has_key('fn'):
                self.menuCoords.append(0)
                Navigator.state = eval(menu.get('fn'))(functionToMap, functionNiceName)

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


class MidiLearn(Navigator):
    def __init__(self, functionToMap, functionNiceName):
        global learningMode
        learningMode = True
        self.functionToMap = functionToMap
        self.functionNiceName = functionNiceName
        self.learnedMidiMessage = None
        self.learnedMidiDevice = None
        print '-- Entered MIDI Learning Mode --'

    def sendControlToMap(self, learnedMidiMessage, learnedMidiDevice):
        self.learnedMidiMessage = learnedMidiMessage
        self.learnedMidiDevice = learnedMidiDevice
        print learnedMidiMessage, learnedMidiDevice

    def enter(self):
        global devices

        try:
            src = self.learnedMidiDevice
            messagetype = self.learnedMidiMessage[0]
            note = self.learnedMidiMessage[1]
            messageKey = (messagetype, note)
            if src not in devices:
                devices[src] = {}  # create new empty dict key for device
                print 'Creating new device in dict'
            else:
                print 'Device is in dict - do nothing'

            if messageKey not in devices.get(src):
                devices.get(src)[messageKey] = {}  # create new empty dict key for messageKey
                print 'Creating new dict for the messageKey'
            else:
                print '!! Already mapped to:', devices.get(src).get(messageKey).get('name')
                print 'Do you want to overwrite? Well too bad - doing it anyway ;)'

            devices.get(src)[messageKey] = {'name': self.functionNiceName, 'fn': self.functionToMap}

            self.cancel() # Go back



        except:
            print 'failed for some reason'
            pass

    def cancel(self):
        #print devices
        global learningMode
        learningMode = False
        if len(self.menuCoords) > 1:
            self.menuCoords.pop()
            self.loadState(MenuNav)
        else:
            self.loadState(MenuNav)  # this will become the gvars.presets state


# ______________________________________________________________________________


devices = {
    'Launchkey 61 3': {
        (176, 41): {
            'name': 'Attack',
            'fn': 'attack'
            # maybe a velocity range
        },
        (144, 60): {
            'note': 1
        },
        (128, 60): {
            'note': 1
        }
    },
    'nanoKONTROL2 1': {
        (176, 64): {
            'name': 'Decay',
            'fn': 'decay'
        }
    }
}

# SAVE FOR LATER
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


rm = Navigator(MenuNav)
# rm.state.right()
# rm.state.enter()
# rm.state.enter()
# Navigator.state.sendControlToMap([176, 1, 83], 'nanoKONTROL2 1')
# rm.state.enter()
# rm.state.cancel()


############################
# ACTUAL DO STUFF FUNCTIONS
############################

class Reverb:
    def roomsize(self, vel):
        print 'Roomsize:', vel

    def damping(self, vel):
        print 'Damping:', vel

    def wet(self, vel):
        print 'Wet:', vel

    def dry(self, vel):
        print 'Dry:', vel


def attack(val):
    print 'Attack:', val


def decay(val):
    print 'Decay:', val


def noteon(messagetype, note, vel):
    # print messagetype, note, vel
    pass


def noteoff(messagetype, note, vel):
    # print messagetype, note, vel
    pass


class MasterVolume:
    def setvolume(self, vel):
        print 'Volume: ' + str(vel)


#########################################
# MIDI CALLBACK
#########################################


def MidiCallback(src, message, time_stamp):
    cc_remapped = False

    messagetype = message[0] >> 4
    buttons = [48, 49, 50, 65]  # temporary until GPIO buttons used

    if messagetype == 13:
        return

    messagechannel = (message[0] & 15) + 1

    note = message[1] if len(message) > 1 else None
    midinote = note
    velocity = message[2] if len(message) > 2 else None
    # if (messagetype != 14):
    # print "ch: " + str(messagechannel) + " type: " + str(messagetype) + " raw: " + str(message) + " SRC: " + str(src)


    if learningMode and note not in buttons and messagetype != 8:

        Navigator.state.sendControlToMap(message, src)

    else:
        try:

            messageKey = (message[0], message[1])

            if devices.get(src).has_key(messageKey):

                # remap note to a function
                if devices.get(src).get(messageKey).has_key('fn'):

                    fnSplit = devices.get(src).get(messageKey).get('fn').split('.')
                    getattr(eval(fnSplit[0])(), fnSplit[1])(
                        velocity)  # runs method from class. ie getattr(MasterVolume(), 'setvolume')
                    cc_remapped = True

                # remap note to a key
                elif isinstance(devices.get(src).get(messageKey).get('note'), int):
                    note = devices.get(src).get(messageKey).get('note')

        except:
            pass

        # Default CC mapping
        if not cc_remapped and messagetype != 9 and messagetype != 8 and messagetype == 11:

            if (note == 7):
                MasterVolume().setvolume(velocity)


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
