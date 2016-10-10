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
SAMPLES_DIR          = "media/"
SONG_FOLDERS_LIST   = os.listdir(SAMPLES_DIR)

USING_CONFIG_FILE   = False




welcome_str = '''
   /==============================//
  /== FUNCTIONS BY ALEX MACRAE ==//
 /========== DID A COOL THING ==//
/==============================//
'''
print welcome_str

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
            
    #print (songsInSetlist)
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
  


    
# This is how a 16x2 LCD screen might look
'''
 1234567812345678
 ________________
|1YouDon 3Stairw |
|2WAIDH  *INTAY  |
|________________|

'''
#    
  
#______________________________________________________________________________   


preset = 0
currentVoice = 1

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
    state           = None
    menuCoords      = [0]
    menuPosition    = menu
    config          = configparser.ConfigParser()
    
    def __init__(self, initState=None):
        self.state = initState
        
    def loadState(self, theClass):
        self.state = theClass
    
    def runState(self):
        self.state = self.state()
    
    def setMenuPosition(self):
        if len(self.menuCoords) == 1:
            self.menuPosition = self.menu
        if len(self.menuCoords) == 2:
            self.menuPosition = self.menu[self.menuCoords[0]]['submenu']
        if len(self.menuCoords) == 3:
            self.menuPosition = self.menu[self.menuCoords[0]]['submenu'][self.menuCoords[1]]['submenu']
        
    def getMenuPosition(self):
        return self.menuPosition


    def parseConfig(self):
        if self.config.read(CONFIG_FILE_PATH):
            print '-= Reading settings from config.ini =-'
            self.USING_CONFIG_FILE = True
            self.MAX_POLYPHONY     = int(self.config['DEFAULT']['MAX_POLYPHONY'])
            self.MIDI_CHANNEL      = int(self.config['DEFAULT']['MIDI_CHANNEL'])
            self.CHANNELS          = int(self.config['DEFAULT']['CHANNELS'])
            self.BUFFERSIZE        = int(self.config['DEFAULT']['BUFFERSIZE'])
            self.SAMPLERATE        = int(self.config['DEFAULT']['SAMPLERATE'])
            self.GLOBAL_VOLUME     = int(self.config['DEFAULT']['GLOBAL_VOLUME'])
        else:
            print '!! config.ini does not exist - using defaults !!'
            self.USING_CONFIG_FILE  = False
            self.MAX_POLYPHONY      = 80
            self.MIDI_CHANNEL       = 1
            self.CHANNELS           = 2
            self.BUFFERSIZE         = 128
            self.SAMPLERATE         = 44100
            self.GLOBAL_VOLUME      = 100

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



#______________________________________________________________________________


def getMenuPathStr():
    path_list = []
    if len(n.menuCoords) == 1:
        path_list = [n.menu[n.menuCoords[0]]['name']]
    if len(n.menuCoords) == 2:
        path_list = [n.menu[n.menuCoords[0]]['name'], n.menu[n.menuCoords[0]]['submenu'][n.menuCoords[1]]['name']]
    if len(n.menuCoords) == 3:
        path_list = [n.menu[n.menuCoords[0]]['name'], n.menu[n.menuCoords[0]]['submenu'][n.menuCoords[1]]['name'], n.menu[n.menuCoords[0]]['submenu'][n.menuCoords[1]]['submenu'][n.menuCoords[2]]['name']]

    menu_msg = '>>> [Menu]'
    for name in path_list:
        menu_msg += '->[' + name + ']'
    
    return menu_msg




#______________________________________________________________________________


                
class PresetNav:
    
    
    
    def __init__(self):
        
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.numFolders = len(os.walk(SAMPLES_DIR).next()[1])
        print '-= Welcome to preset land =-'
        print '[' + str(preset + 1) + '] ' + str(self.setlistList[preset])

    def right(self):
        global preset, currentVoice
        preset += 1
        currentVoice = 1
        if(preset >= self.numFolders):
            preset = 0
        print '[' + str(preset + 1) + '] ' + str(self.setlistList[preset])
        #LoadSamples()

    def left(self):
        global preset, currentVoice
        preset -= 1
        currentVoice = 1
        if(preset < 0):
            preset = self.numFolders-1
        print '[' + str(preset + 1) + '] ' + str(self.setlistList[preset])
        #LoadSamples()
            
    def enter(self):
        n.loadState(MenuNav)
        n.runState()
        
    
    def cancel(self): # can remove empty class methods
        pass
        print '-= Does nothing in preset land =-'




#______________________________________________________________________________

class MenuNav:

    def __init__(self):
       
        n.menu_pos = n.menuCoords[-1]
        print getMenuPathStr()
        

    #select next menu item
    def right(self):

        if  n.menu_pos < len(n.getMenuPosition())-1:
            n.menu_pos += 1
            n.menuCoords[-1] = n.menu_pos
            print getMenuPathStr()
        else:
            print getMenuPathStr() + ' (end)'

    #select previous menu item
    def left(self):

        if  n.menu_pos > 0:
            n.menu_pos -= 1
            n.menuCoords[-1] = n.menu_pos
            print getMenuPathStr()
        else:
            print getMenuPathStr() + ' (start)'
            
    def enter(self):

        if 'submenu' in n.getMenuPosition()[n.menuCoords[-1]]:
            print ' > Entering submenu for [' + n.menuPosition[n.menuCoords[-1]]['name'] + ']'
            n.menuCoords.append(0)
            n.setMenuPosition()
            n.loadState(MenuNav)
            n.runState()
        elif 'fn' in n.getMenuPosition()[n.menuCoords[-1]]:
            print '** Entering [' + n.getMenuPosition()[n.menuCoords[-1]]['name'] + '] function'
            fn = n.getMenuPosition()[n.menuCoords[-1]]['fn']
            if isinstance(fn, list):
                fn = eval(fn[0])
            else:
                fn = eval(fn)
            n.loadState(fn)
            n.runState()
    
    def cancel(self):
        if len(n.menuCoords) > 1:
            n.menuCoords.pop()
            n.setMenuPosition()
            n.loadState(MenuNav)
            n.runState()
        else:
            n.loadState(PresetNav)# this will become the presets state
            n.runState() 
    


    

#______________________________________________________________________________
        
     
class SelectSong:        
    
    def __init__(self):
        
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.nextState = eval(n.getMenuPosition()[n.menuCoords[-1]]['fn'][1])
        print ' * Current song selection: <' + str(preset + 1) + " " + str(self.setlistList[preset]) + '>'
    
    # next song
    def right(self):
        global preset
        if(preset < len(self.setlistList)-1):
            preset += 1
        print " * Song selected: <" + str(preset + 1) + " " + str(self.setlistList[preset]) + '>'

    # previous song
    def left(self):
        global preset
        if(preset > 0):
            preset -= 1
        print " * Song selected: <" + str(preset + 1) + " " + str(self.setlistList[preset]) + '>'
        
    def enter(self):
        n.loadState(self.nextState)
        n.runState()
        
        
    def cancel(self):
        n.loadState(MenuNav)
        n.runState()


#______________________________________________________________________________

class MoveSong:    
    
    def __init__(self):
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.prevState = eval(n.getMenuPosition()[n.menuCoords[-1]]['fn'][0])
        print ' ** Moving song: <' + str(preset + 1) + " " + str(self.setlistList[preset]) + '>'

    # Move song up the setlist
    def left(self):
        global preset
        if(preset > 0):
            self.setlistList[int(preset)], self.setlistList[int(preset) - 1] = self.setlistList[int(preset) - 1], self.setlistList[int(preset)]
            preset -= 1
            #write_setlist(self.setlistList)
        print 'New position: <' + str(preset + 1) + " " + str(self.setlistList[int(preset)]) + '>'
   
    # Move song down the setlist
    def right(self):
        global preset
        if(preset < len(self.setlistList) - 1):
            self.setlistList[int(preset)], self.setlistList[int(preset) + 1] = self.setlistList[int(preset) + 1], self.setlistList[int(preset)]
            preset += 1
            #write_setlist(self.setlistList)
        print 'New position: <' + str(preset + 1) + " " + str(self.setlistList[int(preset)]) + '>'
        
    
    def enter(self):
        write_setlist(self.setlistList)
        n.loadState(self.prevState)
        n.runState()
    
    def cancel(self):
        n.loadState(self.prevState)
        n.runState()



#______________________________________________________________________________

class SetlistRemoveMissing():
    
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
        
        n.loadState(MenuNav)
        n.runState()
        
    def right(self):
        pass
    def left(self):
        pass
    def cancel(self):
        n.loadState(MenuNav)
        n.runState()


#______________________________________________________________________________   


class DeleteSong:
    
    def __init__(self):
        
        self.prevState = eval(n.getMenuPosition()[n.menuCoords[-1]]['fn'][0])
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        print 'Are you sure? [Y/N]'
        print 'WARNING: will crash if we delete all songs'
        
    def enter(self):
        global preset
        print self.setlistList
        del self.setlistList[preset]
        write_setlist(self.setlistList)
        print self.setlistList
        if preset != 0:
            preset -= 1
        
        
        n.loadState(self.prevState)
        n.runState()

    def cancel(self):    
        n.loadState(self.prevState)
        n.runState()


#______________________________________________________________________________
  

class MaxPolyphonyConfig:
    def __init__(self):
        print '-= Max polyphony =-'
        print 'Current polyphony = ' + str(n.MAX_POLYPHONY)

    def left(self):
        n.MAX_POLYPHONY = max(n.MAX_POLYPHONY - 8, 1)
        print n.MAX_POLYPHONY
        
    def right(self):
        n.MAX_POLYPHONY = min(n.MAX_POLYPHONY + 8, 128)
        print n.MAX_POLYPHONY
    
    def enter(self):
        n.writeConfig()
        print '-- requires a restart --' # or a reinstantiation of the sounddevice
        n.loadState(MenuNav)
        n.runState()
    
    def cancel(self):
        self.enter()
  
#______________________________________________________________________________    
    
class MidiChannelConfig:
    def __init__(self):
        print '-= MIDI Channel !IMPORTANT: All MIDI ports are open with rtmidi2 =-'
        print 'Current MIDI Channel = ' + str(n.MIDI_CHANNEL)

    def left(self):
        n.MIDI_CHANNEL = max(n.MIDI_CHANNEL - 1, 1)
        print n.MIDI_CHANNEL
        
    def right(self):
        n.MIDI_CHANNEL = min(n.MIDI_CHANNEL + 1, 16)
        print n.MIDI_CHANNEL
    
    def enter(self):
        n.writeConfig()
        print '-- requires a restart (maybe?) --' # or a reinstantiation of the sounddevice
        n.loadState(MenuNav)
        n.runState()
    
    def cancel(self):
        self.enter()
    

#______________________________________________________________________________

class ChannelsConfig:
    def __init__(self):
        print '-= Audio Channels =-'
        print 'Current number of channels = ' + str(n.CHANNELS)
        self.options = [1, 2, 4, 6, 8]
        self.i = 1
        for x in self.options:
            if x == n.CHANNELS:
                self.i = self.options.index(x)
        
    def left(self):
        if self.i > 0:
            self.i -= 1
        n.CHANNELS = max(self.options[self.i], self.options[0])
        print n.CHANNELS
        
    def right(self):
        if self.i < len(self.options):
            self.i += 1
        n.CHANNELS = min(self.options[self.i], self.options[-1])
        print n.CHANNELS
    
    def enter(self):
        n.writeConfig()
        print '-- requires a restart (maybe?) --' # or a reinstantiation of the sounddevice
        n.loadState(MenuNav)
        n.runState()
    
    def cancel(self):
        self.enter()
    

#______________________________________________________________________________

class BufferSizeConfig:
    def __init__(self):
        print '-= Buffer size =-'
        print 'Current buffer size = ' + str(n.BUFFERSIZE)
        self.options = [16, 32, 64, 128, 256, 512, 1024, 2048]
        self.i = 3
        for x in self.options:
            if x == n.BUFFERSIZE:
                self.i = self.options.index(x)
        
    def left(self):
        if self.i > 0:
            self.i -= 1
        n.BUFFERSIZE = max(self.options[self.i], self.options[0])
        print n.BUFFERSIZE
        
    def right(self):
        if self.i < len(self.options):
            self.i += 1
        n.BUFFERSIZE = min(self.options[self.i], self.options[-1])
        print n.BUFFERSIZE
    
    def enter(self):
        n.writeConfig()
        print '-- requires a restart (maybe?) --' # or a reinstantiation of the sounddevice
        n.loadState(MenuNav)
        n.runState()
    
    def cancel(self):
        self.enter()


#______________________________________________________________________________

class SampleRateConfig:
    def __init__(self):
        print '-= Buffer size =-'
        print 'Current buffer size = ' + str(n.SAMPLERATE)
        self.options = [44100, 48000, 96000]
        self.i = 0
        for x in self.options:
            if x == n.SAMPLERATE:
                self.i = self.options.index(x)
        
    def left(self):
        if self.i > 0:
            self.i -= 1
        n.SAMPLERATE = max(self.options[self.i], self.options[0])
        print n.SAMPLERATE
        
    def right(self):
        if self.i < len(self.options):
            self.i += 1
        n.SAMPLERATE = min(self.options[self.i], self.options[-1])
        print n.SAMPLERATE
    
    def enter(self):
        n.writeConfig()
        print '-- requires a restart (maybe?) --' # or a reinstantiation of the sounddevice
        n.loadState(MenuNav)
        n.runState()
    
    def cancel(self):
        self.enter()


#______________________________________________________________________________
  
class MasterVolumeConfig:
    
    def __init__(self):
        print '-= Master volume =-'
        print 'Current global volume = ' + str(n.GLOBAL_VOLUME)
        buttonDown = False

    def left(self):
        n.GLOBAL_VOLUME = max(n.GLOBAL_VOLUME - 4, 0)
        print n.GLOBAL_VOLUME
        
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
        n.GLOBAL_VOLUME = min(n.GLOBAL_VOLUME + 4, 100)
        print n.GLOBAL_VOLUME
    
    def enter(self):
        n.writeConfig()
        n.loadState(MenuNav)
        n.runState()
    
    def cancel(self):
        n.writeConfig()
        n.loadState(MenuNav)
        n.runState()

#_____________________________________________________________________________

class MidiMapper:
    
    MIDI_LEARN = False

    def __init__(self):
        MidiMapper.MIDI_LEARN = True
        #self.next_state = eval(str(n.getMenuPosition()['fn'][1]))
            
    def learn(self, src, message):
        self.deviceName = src[:src.rfind(" "):] # Strips the port number(s) from after the final space.
            # These numbers change depending on the USB port.
        self.midiMessage = message
        MidiMapper.MIDI_LEARN = False
        self.writeMidiDeviceConfig()
    
    def enter(self):
        print 'here'
        #n.loadState(self.next_state)
        #n.runState()
    
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
        n.loadState(MenuNav)
        n.runState()
  
#########################################
# LOAD THE
# NAVIGATOR
#########################################

n = Navigator()
n.parseConfig()
n.loadState(PresetNav)
n.runState()


#______________________________________________________________________________

def MidiCallback(src, message, time_stamp):
    global preset
    
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
        n.state.learn(src, message)
        
    if(messagetype == 11):
         
        
        if(note == 49): # Enter button
            if(velocity == 127):
                if n:
                    n.state.enter()
#            else:
#                n.state.enterUp()
            
           
        
        
    if(note == 48): # Left arrow button
        if(velocity == 127):
            n.state.left()
#            else:
#                n.state.leftUp()
    
        
    if(note == 50): # Right arrow button
        if(velocity == 127):
            n.state.right() 
#            else:
#                n.state.rightUp()
            
                
    if(note == 65): # Cancel button
        if(velocity == 127):
            n.state.cancel() 
#            else:
#                n.state.cancelUp()
        
        




stopit = False
midi_in = rtmidi2.MidiInMulti()#.open_ports("*")
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
