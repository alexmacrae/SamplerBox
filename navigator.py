#  SamplerBox Navigator
#
#  author:    Alex MacRae (alex.finlay.macrae@gmail.com)
#  url:       https://github.com/alexmacrae/
#  license:   Creative Commons ShareAlike 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)
#
#  samplerbox2.py: Main file
#

#########################################
# Import
#
#########################################
import configparser
import os
import psutil
import sys
import rtmidi2
import time
import threading
import loadsamples as ls
import globalvars as gvars

#
#customCharMapping = {
#    "[smile]": {"address": 0, 
#        "character":
#        [0b00000,
#        0b00000,
#        0b01010,
#        0b00000,
#        0b10001,
#        0b01110,
#        0b00000,
#        0b00000]}
#}    


MIDI_CONFIG_DIR    = "midi config/"
CONFIG_FILE_PATH    = "system config/config.ini"
SETLIST_FILE_PATH   = "setlist/setlist.txt"
SONG_FOLDERS_LIST   = os.listdir(gvars.SAMPLES_DIR)

USING_CONFIG_FILE   = False

TESTING = False


print '''
  /==============================//
 /== NAVIGATOR by ALEX MACRAE ==//
/==============================//
'''

def write_setlist(list_to_write):
    print('-= WRITING NEW SETLIST =-')
    setlist = open(SETLIST_FILE_PATH, "w")
    list_to_write = list(filter(None, list_to_write)) # remove empty strings / empty lines
    for song in list_to_write:
        setlist.write(song + '\n')
    setlist.close()


def findMissingFolders():
    
    # Check to see if the song name in the setlist matches the name of a folder.
    # If it doesn't, mark it by prepending an *asterix and rewrite the setlist file.
    
    songsInSetlist = open(SETLIST_FILE_PATH).read().splitlines()
    songsInSetlist = list(filter(None, songsInSetlist)) # remove empty strings / empty lines
    changes = False
    k = 0
    for song_name in songsInSetlist:
        i = 0
        for song_folder_name in SONG_FOLDERS_LIST:
            
            if(song_name == song_folder_name):
                #print(song_name + ' was found')
                break
            elif(song_name.replace('* ', '') == song_folder_name):
                #print(song_name + ' was found - previous lost')
                songsInSetlist[k] = song_name.replace('* ', '')
                #break
            else:
                if(i == len(SONG_FOLDERS_LIST) - 1):
                    print(song_name + ' WAS NOT FOUND. ')
                    songsInSetlist[k] = '* ' + song_name.replace('* ', '')
                    changes = True
                    break
                    
            i += 1
        k += 1
            
    if (changes):
        write_setlist(songsInSetlist)
    else:
        print('-= No missing folders detected =-\n')
        

def findAndAddNewFolders():
    # Check for new song folders and add them to the end of the setlist
    
    songsInSetlist = open(SETLIST_FILE_PATH).read().splitlines()
    songsInSetlist = list(filter(None, songsInSetlist)) # remove empty strings / empty lines
    changes = False
    
    if (set(songsInSetlist).intersection(SONG_FOLDERS_LIST) != len(SONG_FOLDERS_LIST) and len(songsInSetlist) != 0):

        for song_folder_name in SONG_FOLDERS_LIST:
            i = 0
            for song_name in songsInSetlist:
                if(song_folder_name == song_name):
                    break
                elif (i == len(songsInSetlist) - 1):
                    print (song_folder_name + ' - NEW FOLDER')
                    changes = True
                    songsInSetlist.append(song_folder_name)
                    break

                i += 1
    elif (len(songsInSetlist) == 0):
        songsInSetlist = SONG_FOLDERS_LIST
        changes = True
        print ('Setlist empty - adding all foldings')
        
    #print(songsInSetlist)
    if(changes):
        write_setlist(songsInSetlist)
    else:
        print('-= No new folders found =-\n')


#______________________________________________________________________________  
# On startup detect missing folders and add any new ones found                
findMissingFolders()                
findAndAddNewFolders()
#______________________________________________________________________________  


class Navigator:

    menu = {
        0: {
            'name': 'Setlist',
            'submenu': {
                0: {'name': 'Rearrange/Move song', 'fn': ['SelectSong', 'MoveSong']},
                1: {'name': 'Remove missing', 'fn': 'SetlistRemoveMissing'},
                2: {'name': 'Delete songs', 'fn': ['SelectSong', 'DeleteSong']}
            }
        },
        1: {'name': 'All songs', 'fn': ''},
        2: {'name': 'Master volume', 'fn': 'MasterVolumeConfig'},
        3: {'name': 'MIDI Mapping', 
            'submenu': {
                0: {'name': 'Master Volume', 'fn': ['MidiMapper', 'MasterVolumeConfig']},
                1: {'name': 'Voices',
                    'submenu': {
                        0: {'name': 'Voice 1', 'fn': ['MidiMapper', '!voices!']},
                        1: {'name': 'Voice 2', 'fn': ['MidiMapper', '!voices!']},
                        2: {'name': 'Voice 3', 'fn': ['MidiMapper', '!voices!']},
                        3: {'name': 'Voice 4', 'fn': ['MidiMapper', '!voices!']}
                    }
                },
                2: {'name': 'Sys Left/Right', 'fn': ['MidiMapper', '!sys pos changer!']}
                }
            },
        4: {'name': 'System settings',
            'submenu': {
                0: {'name': 'Max polyphony', 'fn': 'MaxPolyphonyConfig'},
                1: {'name': 'MIDI channel', 'fn': 'MidiChannelConfig'},
                2: {'name': 'Audio channels', 'fn': 'ChannelsConfig'},
                3: {'name': 'Buffer size', 'fn': 'BufferSizeConfig'},
                4: {'name': 'Sample rate', 'fn': 'SampleRateConfig'}
            }
        }
    }
    state               = None
    menuCoords          = [0]
    menuPosition        = menu
    config              = configparser.ConfigParser()

    def __init__(self, initState):
        Navigator.state = initState
        self.loadState(Navigator.state)
        self.runState()

        
    def loadState(self, theClass):
        Navigator.state = theClass

    def runState(self):
        Navigator.state = Navigator.state()
    
    def setMenuPosition(self):
        if len(Navigator.menuCoords) == 1:
            print '1'
            Navigator.menuPosition = Navigator.menu
        if len(Navigator.menuCoords) == 2:
            print '2'
            Navigator.menuPosition = Navigator.menu[Navigator.menuCoords[0]]['submenu']
        if len(Navigator.menuCoords) == 3:
            print '3'
            Navigator.menuPosition = Navigator.menu[Navigator.menuCoords[0]]['submenu'][Navigator.menuCoords[1]]['submenu']
        


    def parseConfig(self):
        if self.config.read(CONFIG_FILE_PATH):
            print '-= Reading settings from config.ini =-'
            Navigator.USING_CONFIG_FILE = True
            Navigator.MAX_POLYPHONY     = int(self.config['DEFAULT']['MAX_POLYPHONY'])
            Navigator.MIDI_CHANNEL      = int(self.config['DEFAULT']['MIDI_CHANNEL'])
            Navigator.CHANNELS          = int(self.config['DEFAULT']['CHANNELS'])
            Navigator.BUFFERSIZE        = int(self.config['DEFAULT']['BUFFERSIZE'])
            Navigator.SAMPLERATE        = int(self.config['DEFAULT']['SAMPLERATE'])
            Navigator.GLOBAL_VOLUME     = int(self.config['DEFAULT']['GLOBAL_VOLUME'])
        else:
            print '!! config.ini does not exist - using defaults !!'
            Navigator.USING_CONFIG_FILE  = False
            Navigator.MAX_POLYPHONY      = 80
            Navigator.MIDI_CHANNEL       = 1
            Navigator.CHANNELS           = 2
            Navigator.BUFFERSIZE         = 128
            Navigator.SAMPLERATE         = 44100
            Navigator.GLOBAL_VOLUME      = 100

    def writeConfig(self):

        self.config['DEFAULT']['MAX_POLYPHONY']  = str(self.MAX_POLYPHONY)
        self.config['DEFAULT']['MIDI_CHANNEL']   = str(self.MIDI_CHANNEL)
        self.config['DEFAULT']['CHANNELS']       = str(self.CHANNELS)
        self.config['DEFAULT']['BUFFERSIZE']     = str(self.BUFFERSIZE)
        self.config['DEFAULT']['SAMPLERATE']     = str(self.SAMPLERATE)
        self.config['DEFAULT']['GLOBAL_VOLUME']   = str(self.GLOBAL_VOLUME)
        print 'WRITING CONFIG'
        with open(CONFIG_FILE_PATH, 'w') as configfile:
            self.config.write(configfile)

    def getMenuPathStr(self):
        path_list = []
        if len(Navigator.menuCoords) == 1:
            path_list = [Navigator.menu[Navigator.menuCoords[0]]['name']]
        if len(Navigator.menuCoords) == 2:
            path_list = [Navigator.menu[Navigator.menuCoords[0]]['name'],
                         Navigator.menu[Navigator.menuCoords[0]]['submenu'][Navigator.menuCoords[1]]['name']]
        if len(Navigator.menuCoords) == 3:
            path_list = [Navigator.menu[Navigator.menuCoords[0]]['name'],
                         Navigator.menu[Navigator.menuCoords[0]]['submenu'][Navigator.menuCoords[1]]['name'],
                         Navigator.menu[Navigator.menuCoords[0]]['submenu'][Navigator.menuCoords[1]]['submenu'][
                             Navigator.menuCoords[2]]['name']]

        menu_msg = '>>> [Menu]'
        for name in path_list:
            menu_msg += '->[' + name + ']'

        return menu_msg



#______________________________________________________________________________






                
class PresetNav(Navigator):
    
    
    
    def __init__(self):
        
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.numFolders = len(os.walk(gvars.SAMPLES_DIR).next()[1])
        print '-= Welcome to preset land =-'
        print '[' + str(gvars.preset + 1) + '] ' + str(self.setlistList[gvars.preset])

    def right(self):
        gvars.preset += 1
        
        gvars.current_voice = 1
        if(gvars.preset >= self.numFolders):
            gvars.preset = 0
        print '[' + str(gvars.preset + 1) + '] ' + str(self.setlistList[gvars.preset])
        ls.LoadSamples()

    def left(self):
        gvars.preset -= 1
        
        gvars.current_voice = 1
        if(gvars.preset < 0):
            gvars.preset = self.numFolders-1
        print '[' + str(gvars.preset + 1) + '] ' + str(self.setlistList[gvars.preset])
        ls.LoadSamples()
            
    def enter(self):
        self.loadState(MenuNav)
        self.runState()
        
    
    def cancel(self): # can remove empty class methods
        pass
        print '-= Does nothing. Perhaps cycle display modes =-'
        # eg CPU/RAM, battery life, time, wifi/bluetooth status




#______________________________________________________________________________

class MenuNav(Navigator):

    def __init__(self):

        self.menu_pos = self.menuCoords[-1]
        print self.getMenuPathStr()
        

    #select next menu item
    def right(self):

        if  self.menu_pos < len(self.menuPosition)-1:
            self.menu_pos += 1
            self.menuCoords[-1] = self.menu_pos
            print self.getMenuPathStr()
        else:
            print self.getMenuPathStr() + ' (end)'

    #select previous menu item
    def left(self):

        if  self.menu_pos > 0:
            self.menu_pos -= 1
            self.menuCoords[-1] = self.menu_pos
            print self.getMenuPathStr()
        else:
            print self.getMenuPathStr() + ' (start)'
            
    def enter(self):

        if 'submenu' in self.menuPosition[self.menuCoords[-1]]:
            print ' > Entering submenu for [' + self.menuPosition[self.menuCoords[-1]]['name'] + ']'
            self.menuCoords.append(0)
            self.setMenuPosition()
            self.loadState(MenuNav)
            self.runState()
        elif 'fn' in self.menuPosition[self.menuCoords[-1]]:
            print '** Entering [' + self.menuPosition[self.menuCoords[-1]]['name'] + '] function'
            fn = self.menuPosition[self.menuCoords[-1]]['fn']
            if isinstance(fn, list):
                fn = eval(fn[0])
            else:
                fn = eval(fn)
            self.loadState(fn)
            self.runState()
    
    def cancel(self):
        if len(self.menuCoords) > 1:
            self.menuCoords.pop()
            self.setMenuPosition()
            self.loadState(MenuNav)
            self.runState()
        else:
            self.loadState(PresetNav)# this will become the gvars.presets state
            self.runState()
    


    

#______________________________________________________________________________
        
     
class SelectSong(Navigator):
    
    def __init__(self):
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.nextState = eval(self.menuPosition[self.menuCoords[-1]]['fn'][1])
        print ' * Current song selection: <' + str(gvars.preset + 1) + " " + str(self.setlistList[gvars.preset]) + '>'
    
    # next song
    def right(self):
        if(gvars.preset < len(self.setlistList)-1):
            gvars.preset += 1
        print " * Song selected: <" + str(gvars.preset + 1) + " " + str(self.setlistList[gvars.preset]) + '>'

    # previous song
    def left(self):
        if(gvars.preset > 0):
            gvars.preset -= 1
        print " * Song selected: <" + str(gvars.preset + 1) + " " + str(self.setlistList[gvars.preset]) + '>'
        
    def enter(self):
        self.loadState(self.nextState)
        self.runState()
        
        
    def cancel(self):
        self.loadState(MenuNav)
        self.runState()


#______________________________________________________________________________

class MoveSong(Navigator):
    
    def __init__(self):
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.prevState = eval(self.menuPosition[self.menuCoords[-1]]['fn'][0])
        print ' ** Moving song: <' + str(gvars.preset + 1) + " " + str(self.setlistList[gvars.preset]) + '>'

    # Move song up the setlist
    def left(self):
        if(gvars.preset > 0):
            self.setlistList[int(gvars.preset)], self.setlistList[int(gvars.preset) - 1] = self.setlistList[int(gvars.preset) - 1], self.setlistList[int(gvars.preset)]
            gvars.preset -= 1
            #write_setlist(self.setlistList)
        print 'New position: <' + str(gvars.preset + 1) + " " + str(self.setlistList[int(gvars.preset)]) + '>'
   
    # Move song down the setlist
    def right(self):
        if(gvars.preset < len(self.setlistList) - 1):
            self.setlistList[int(gvars.preset)], self.setlistList[int(gvars.preset) + 1] = self.setlistList[int(gvars.preset) + 1], self.setlistList[int(gvars.preset)]
            gvars.preset += 1
            #write_setlist(self.setlistList)
        print 'New position: <' + str(gvars.preset + 1) + " " + str(self.setlistList[int(gvars.preset)]) + '>'
        
    
    def enter(self):
        write_setlist(self.setlistList)
        self.loadState(self.prevState)
        self.runState()
    
    def cancel(self):
        self.loadState(self.prevState)
        self.runState()



#______________________________________________________________________________

class SetlistRemoveMissing(Navigator):
    
    def __init__(self):
        
        print 'Remove missing songs? [Y/N]'
        
        
        
    def enter(self):

        songsInSetlist = open(SETLIST_FILE_PATH).read().splitlines()
        i = 0
        for song in songsInSetlist:
            if('* ' in song):
                del songsInSetlist[i]
                write_setlist(songsInSetlist)
            i += 1
        
        self.loadState(MenuNav)
        self.runState()
        
    def right(self):
        pass
    def left(self):
        pass
    def cancel(self):
        self.loadState(MenuNav)
        self.runState()


#______________________________________________________________________________   


class DeleteSong(Navigator):
    
    def __init__(self):
        
        self.prevState = eval(self.menuPosition[self.menuCoords[-1]]['fn'][0])
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        print 'Are you sure? [Y/N]'
        print 'WARNING: will crash if we delete all songs'
        
    def enter(self):
        print self.setlistList
        del self.setlistList[gvars.preset]
        write_setlist(self.setlistList)
        print self.setlistList
        if gvars.preset != 0:
            gvars.preset -= 1
        
        
        self.loadState(self.prevState)
        self.runState()

    def cancel(self):    
        self.loadState(self.prevState)
        self.runState()


#______________________________________________________________________________
  

class MaxPolyphonyConfig(Navigator):
    def __init__(self):
        print '-= Max polyphony =-'
        print 'Current polyphony = ' + str(self.MAX_POLYPHONY)

    def left(self):
        self.MAX_POLYPHONY = max(self.MAX_POLYPHONY - 8, 1)
        print self.MAX_POLYPHONY
        
    def right(self):
        self.MAX_POLYPHONY = min(self.MAX_POLYPHONY + 8, 128)
        print self.MAX_POLYPHONY
    
    def enter(self):
        self.writeConfig()
        print '-- requires a restart --' # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()
    
    def cancel(self):
        self.enter()
  
#______________________________________________________________________________    
    
class MidiChannelConfig(Navigator):
    def __init__(self):
        print '-= MIDI Channel !IMPORTANT: All MIDI ports are open with rtmidi2 =-'
        print 'Current MIDI Channel = ' + str(self.MIDI_CHANNEL)

    def left(self):
        self.MIDI_CHANNEL = max(self.MIDI_CHANNEL - 1, 1)
        print self.MIDI_CHANNEL
        
    def right(self):
        self.MIDI_CHANNEL = min(self.MIDI_CHANNEL + 1, 16)
        print self.MIDI_CHANNEL
    
    def enter(self):
        self.writeConfig()
        print '-- requires a restart (maybe?) --' # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()
    
    def cancel(self):
        self.enter()
    

#______________________________________________________________________________

class ChannelsConfig(Navigator):
    def __init__(self):
        print '-= Audio Channels =-'
        print 'Current number of channels = ' + str(self.CHANNELS)
        self.options = [1, 2, 4, 6, 8]
        self.i = 1
        for x in self.options:
            if x == self.CHANNELS:
                self.i = self.options.index(x)
        
    def left(self):
        if self.i > 0:
            self.i -= 1
        self.CHANNELS = max(self.options[self.i], self.options[0])
        print self.CHANNELS
        
    def right(self):
        if self.i < len(self.options):
            self.i += 1
        self.CHANNELS = min(self.options[self.i], self.options[-1])
        print self.CHANNELS
    
    def enter(self):
        self.writeConfig()
        print '-- requires a restart (maybe?) --' # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()
    
    def cancel(self):
        self.enter()
    

#______________________________________________________________________________

class BufferSizeConfig(Navigator):
    def __init__(self):
        print '-= Buffer size =-'
        print 'Current buffer size = ' + str(self.BUFFERSIZE)
        self.options = [16, 32, 64, 128, 256, 512, 1024, 2048]
        self.i = 3
        for x in self.options:
            if x == self.BUFFERSIZE:
                self.i = self.options.index(x)
        
    def left(self):
        if self.i > 0:
            self.i -= 1
        self.BUFFERSIZE = max(self.options[self.i], self.options[0])
        print self.BUFFERSIZE
        
    def right(self):
        if self.i < len(self.options):
            self.i += 1
        self.BUFFERSIZE = min(self.options[self.i], self.options[-1])
        print self.BUFFERSIZE
    
    def enter(self):
        self.writeConfig()
        print '-- requires a restart (maybe?) --' # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()
    
    def cancel(self):
        self.enter()


#______________________________________________________________________________

class SampleRateConfig(Navigator):
    def __init__(self):
        print '-= Buffer size =-'
        print 'Current buffer size = ' + str(self.SAMPLERATE)
        self.options = [44100, 48000, 96000]
        self.i = 0
        for x in self.options:
            if x == self.SAMPLERATE:
                self.i = self.options.index(x)
        
    def left(self):
        if self.i > 0:
            self.i -= 1
        self.SAMPLERATE = max(self.options[self.i], self.options[0])
        print self.SAMPLERATE
        
    def right(self):
        if self.i < len(self.options):
            self.i += 1
        self.SAMPLERATE = min(self.options[self.i], self.options[-1])
        print self.SAMPLERATE
    
    def enter(self):
        self.writeConfig()
        print '-- requires a restart (maybe?) --' # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()
    
    def cancel(self):
        self.enter()


#______________________________________________________________________________
  
class MasterVolumeConfig(Navigator):
    
    def __init__(self):
        print '-= Master volume =-'
        print 'Current global volume = ' + str(self.GLOBAL_VOLUME)
        buttonDown = False

    def left(self):
        self.GLOBAL_VOLUME = max(self.GLOBAL_VOLUME - 4, 0)
        print self.GLOBAL_VOLUME
        
        # Would be cool to work out a "do while (condition)" without the infinite
        # loop blocking the "midi button up" message
        
#        self.buttonDown = True
#        time.sleep(0.5)
#        while self.buttonDown:
#            globalvolume = max(globalvolume - 4, 0)
#            time.sleep(0.2)
#            print globalvolume, self.buttonDown

        
    def right(self):
        self.buttonDown = True
        self.GLOBAL_VOLUME = min(self.GLOBAL_VOLUME + 4, 100)
        print self.GLOBAL_VOLUME
    
    def enter(self):
        self.writeConfig()
        self.loadState(MenuNav)
        self.runState()
    
    def cancel(self):
        self.writeConfig()
        self.loadState(MenuNav)
        self.runState()

#_____________________________________________________________________________

class MidiMapper(Navigator):
    
    MIDI_LEARN = False

    def __init__(self):
        MidiMapper.MIDI_LEARN = True
        #self.next_state = eval(str(self.menuPosition['fn'][1]))
            
    def learn(self, src, message):
        self.deviceName = src[:src.rfind(" "):] # Strips the port number(s) from after the final space.
            # These numbers change depending on the USB port.
        self.midiMessage = message
        MidiMapper.MIDI_LEARN = False
        self.writeMidiDeviceConfig()
    
    def enter(self):
        print 'here'
        #self.loadState(self.next_state)
        #self.runState()
    
    def writeMidiDeviceConfig(self):
        #print self.deviceName
        #print self.midiMessage
                
        config = configparser.RawConfigParser()
        config.add_section('MIDIMAP')
        config.set('MIDIMAP', 'device_name', str(self.deviceName))
        config.set('MIDIMAP', 'mmessage', str(self.midiMessage))

        # Writing our configuration file to 'example.cfg'
        with open(MIDI_CONFIG_DIR + self.deviceName + '.ini', 'wb') as configfile:
            config.write(configfile)
        self.cancel()
        
        
    
    def cancel(self):
        MidiMapper.MIDI_LEARN = False
        self.loadState(MenuNav)
        self.runState()
  
#########################################
# LOAD THE
# NAVIGATOR
#########################################

# n = Navigator()
# Navigator.parseConfig()
# Navigator.loadState(PresetNav)
# Navigator.runState()


#______________________________________________________________________________


if TESTING:

    def MidiCallback(src, message, time_stamp):

        messagetype = message[0] >> 4
        if messagetype == 13:
            return

        messagechannel = (message[0] & 15) + 1

        note = message[1] if len(message) > 1 else None
        midinote = note
        velocity = message[2] if len(message) > 2 else None

    #    if (messagetype != 14):
    #        print "ch: " + str(messagechannel) + " type: " + str(messagetype) + " raw: " + str(message) + " SRC: " + str(src)

        if MidiMapper.MIDI_LEARN and note != 49:
            Navigator.state.learn(src, message)

        if(messagetype == 11):


            if(note == 49): # Enter button
                if(velocity == 127):
                    if Navigator:
                        Navigator.state.enter()
    #            else:
    #                Navigator.state.enterUp()




        if(note == 48): # Left arrow button
            if(velocity == 127):
                Navigator.state.left()
    #            else:
    #                Navigator.state.leftUp()


        if(note == 50): # Right arrow button
            if(velocity == 127):
                Navigator.state.right()
    #            else:
    #                Navigator.state.rightUp()


        if(note == 65): # Cancel button
            if(velocity == 127):
                Navigator.state.cancel()
    #            else:
    #                Navigator.state.cancelUp()








    def mididevicesearch():
        stopit = False
        midi_in = rtmidi2.MidiInMulti()  # .open_ports("*")
        curr_ports = []
        prev_ports = []
        first_loop = True
        while True:

            #System info
            #print 'CPU usage: '+ str (psutil.cpu_percent(None)) + '%  ////  RAM usage: ' + str(float(psutil.virtual_memory().percent)) + '%'

            if stopit:
                break
            curr_ports = rtmidi2.get_in_ports()
            #print curr_ports
            if (len(prev_ports) != len(curr_ports)):
                midi_in.close_ports()
                prev_ports = []
            for port in curr_ports:
                if port not in prev_ports and 'Midi Through' not in port and (len(prev_ports) != len(curr_ports)):
                    midi_in.open_ports(port)
                    midi_in.callback = MidiCallback
                    if first_loop:
                        print ('Opened MIDI port: ' + port)
                    else:
                        print ('Reopening MIDI port: ' + port)
            prev_ports = curr_ports
            first_loop = False
            time.sleep(2)

    MidiDeviceThread = threading.Thread(target=mididevicesearch)
    MidiDeviceThread.daemon = True
    MidiDeviceThread.start()



#new_song_selector = SelectSong()
#new_song_selector.next()

#def foldernames_and_setlist_match():
#    songsInSetlist = open(SETLIST_FILE_PATH).read().splitlines()
#    
#    merged_list = songsInSetlist + SONG_FOLDERS_LIST
#    
#    print(merged_list)
#    
#    for song_name in songsInSetlist:
#        
#        for song_folder_name in SONG_FOLDERS_LIST:
#            if(song_name == song_folder_name):
#                print(song_name + ': found')
#                break
#
#    
#    
#    if(songsInSetlist == SONG_FOLDERS_LIST):
#        return True
#    else:
#        return False
#
#
#
#
#if (os.path.isfile(SETLIST_FILE_PATH)):
#    print ('exists')
#    print (foldernames_and_setlist_match())
#else:
#    print ('nup')
#    setlist = open(SETLIST_FILE_PATH, "w")
#    for song_folder in SONG_FOLDERS_LIST:
#        setlist.write(song_folder + '\n')
#    
#    setlist.close()
#
