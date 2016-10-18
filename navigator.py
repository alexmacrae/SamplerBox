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
import lcd

MIDI_CONFIG_DIR = "midi config/"
CONFIG_FILE_PATH = "system config/config.ini"
SETLIST_FILE_PATH = "setlist/setlist.txt"
SONG_FOLDERS_LIST = os.listdir(gvars.SAMPLES_DIR)

USING_CONFIG_FILE = False

print '''
  /==============================//
 /== NAVIGATOR by ALEX MACRAE ==//
/==============================//
'''


def write_setlist(list_to_write):
    print('-= WRITING NEW SETLIST =-')
    setlist = open(SETLIST_FILE_PATH, "w")
    list_to_write = list(filter(None, list_to_write))  # remove empty strings / empty lines
    for song in list_to_write:
        setlist.write(song + '\n')
    setlist.close()


def findMissingFolders():
    # Check to see if the song name in the setlist matches the name of a folder.
    # If it doesn't, mark it by prepending an *asterix and rewrite the setlist file.

    songsInSetlist = open(SETLIST_FILE_PATH).read().splitlines()
    songsInSetlist = list(filter(None, songsInSetlist))  # remove empty strings / empty lines
    changes = False
    k = 0
    for song_name in songsInSetlist:
        i = 0
        for song_folder_name in SONG_FOLDERS_LIST:

            if (song_name == song_folder_name):
                # print(song_name + ' was found')
                break
            elif (song_name.replace('* ', '') == song_folder_name):
                # print(song_name + ' was found - previous lost')
                songsInSetlist[k] = song_name.replace('* ', '')
                # break
            else:
                if (i == len(SONG_FOLDERS_LIST) - 1):
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
    songsInSetlist = list(filter(None, songsInSetlist))  # remove empty strings / empty lines
    changes = False

    if (set(songsInSetlist).intersection(SONG_FOLDERS_LIST) != len(SONG_FOLDERS_LIST) and len(songsInSetlist) != 0):

        for song_folder_name in SONG_FOLDERS_LIST:
            i = 0
            for song_name in songsInSetlist:
                if (song_folder_name == song_name):
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

    # print(songsInSetlist)
    if (changes):
        write_setlist(songsInSetlist)
    else:
        print('-= No new folders found =-\n')

    # ______________________________________________________________________________


def removeMissingSetlistSongs():
    songsInSetlist = open(SETLIST_FILE_PATH).read().splitlines()
    i = 0
    for song in songsInSetlist:
        if ('* ' in song):
            del songsInSetlist[i]
            write_setlist(songsInSetlist)
        i += 1




# ______________________________________________________________________________
# On startup detect missing folders and add any new ones found                
findMissingFolders()
removeMissingSetlistSongs()
findAndAddNewFolders()

# ______________________________________________________________________________


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
    state = None
    menuCoords = [0]
    menuPosition = menu
    config = configparser.ConfigParser()

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
            print 'Menu level: [1]'
            Navigator.menuPosition = Navigator.menu
        if len(Navigator.menuCoords) == 2:
            print 'Menu level: [2]'
            Navigator.menuPosition = Navigator.menu[Navigator.menuCoords[0]]['submenu']
        if len(Navigator.menuCoords) == 3:
            print 'Menu level: [3]'
            Navigator.menuPosition = Navigator.menu[Navigator.menuCoords[0]]['submenu'][Navigator.menuCoords[1]][
                'submenu']

    def parseConfig(self):
        if self.config.read(CONFIG_FILE_PATH):
            print '-= Reading settings from config.ini =-'
            Navigator.USING_CONFIG_FILE = True
            Navigator.MAX_POLYPHONY = int(self.config['DEFAULT']['MAX_POLYPHONY'])
            Navigator.MIDI_CHANNEL = int(self.config['DEFAULT']['MIDI_CHANNEL'])
            Navigator.CHANNELS = int(self.config['DEFAULT']['CHANNELS'])
            Navigator.BUFFERSIZE = int(self.config['DEFAULT']['BUFFERSIZE'])
            Navigator.SAMPLERATE = int(self.config['DEFAULT']['SAMPLERATE'])
            Navigator.GLOBAL_VOLUME = int(self.config['DEFAULT']['GLOBAL_VOLUME'])
        else:
            print '!! config.ini does not exist - using defaults !!'
            Navigator.USING_CONFIG_FILE = False
            Navigator.MAX_POLYPHONY = 80
            Navigator.MIDI_CHANNEL = 1
            Navigator.CHANNELS = 2
            Navigator.BUFFERSIZE = 128
            Navigator.SAMPLERATE = 44100
            Navigator.GLOBAL_VOLUME = 100

    def writeConfig(self):

        self.config['DEFAULT']['MAX_POLYPHONY'] = str(self.MAX_POLYPHONY)
        self.config['DEFAULT']['MIDI_CHANNEL'] = str(self.MIDI_CHANNEL)
        self.config['DEFAULT']['CHANNELS'] = str(self.CHANNELS)
        self.config['DEFAULT']['BUFFERSIZE'] = str(self.BUFFERSIZE)
        self.config['DEFAULT']['SAMPLERATE'] = str(self.SAMPLERATE)
        self.config['DEFAULT']['GLOBAL_VOLUME'] = str(self.GLOBAL_VOLUME)
        print 'WRITING CONFIG'
        with open(CONFIG_FILE_PATH, 'w') as configfile:
            self.config.write(configfile)

    def getMenuPathStr(self):
        path_list = []
        menu_msg = ''
        if len(Navigator.menuCoords) == 1:
            path_list = [Navigator.menu[Navigator.menuCoords[0]]['name']]
            menu_msg += 'Menu' + unichr(2)
        if len(Navigator.menuCoords) == 2:
            path_list = [Navigator.menu[Navigator.menuCoords[0]]['name'],
                         Navigator.menu[Navigator.menuCoords[0]]['submenu'][Navigator.menuCoords[1]]['name']]
        if len(Navigator.menuCoords) == 3:
            path_list = [Navigator.menu[Navigator.menuCoords[0]]['name'],
                         Navigator.menu[Navigator.menuCoords[0]]['submenu'][Navigator.menuCoords[1]]['name'],
                         Navigator.menu[Navigator.menuCoords[0]]['submenu'][Navigator.menuCoords[1]]['submenu'][
                             Navigator.menuCoords[2]]['name']]


        # for name in path_list:
        #     menu_msg += '->[' + name + ']'
        menu_msg += path_list[-1]

        return menu_msg


# ______________________________________________________________________________





class PresetNav(Navigator):
    def __init__(self):

        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.numFolders = len(os.walk(gvars.SAMPLES_DIR).next()[1])
        print '-= Welcome to preset land =-'
        lcd.resetModes()
        lcd.inPresetMode = True
        self.display()

    def display(self):
        p = gvars.preset
        s1 = str(p + 1) + unichr(2) + str(self.setlistList[p])
        if p == self.numFolders - 1:
            p = 0
        else:
            p += 1
        s2 = str(p + 1) + unichr(2) + str(self.setlistList[p])

        lcd.display(s1, 1, True)
        lcd.display(s2, 2, True)


    def right(self):
        gvars.preset += 1
        lcd.resetModes()
        lcd.inPresetMode = True
        gvars.current_voice = 1
        if (gvars.preset >= self.numFolders):
            gvars.preset = 0
        self.display()
        ls.LoadSamples()

    def left(self):
        gvars.preset -= 1
        lcd.resetModes()
        lcd.inPresetMode = True
        gvars.current_voice = 1
        if (gvars.preset < 0):
            gvars.preset = self.numFolders - 1
        self.display()
        ls.LoadSamples()

    def enter(self):
        self.loadState(MenuNav)
        self.runState()

    def cancel(self):  # can remove empty class methods
        lcd.TimeOut = lcd.TimeOutReset
        lcd.resetModes()
        lcd.inSysMode = True
        # eg CPU/RAM, battery life, time, wifi/bluetooth status


# ______________________________________________________________________________

class MenuNav(Navigator):
    def __init__(self):

        self.menu_pos = self.menuCoords[-1]
        lcd.resetModes()
        lcd.menuMode = True
        lcd.display(self.getMenuPathStr(), 1)
        lcd.display('-------------------------', 2)

    # select next menu item
    def right(self):

        if self.menu_pos < len(self.menuPosition) - 1:
            self.menu_pos += 1
            self.menuCoords[-1] = self.menu_pos
            lcd.display(self.getMenuPathStr(), 1)
        else:
            lcd.display(self.getMenuPathStr() + ' (end)', 1)

    # select previous menu item
    def left(self):

        if self.menu_pos > 0:
            self.menu_pos -= 1
            self.menuCoords[-1] = self.menu_pos
            lcd.display(self.getMenuPathStr(), 1)
        else:
            lcd.display(self.getMenuPathStr() + ' (start)', 1)

    def enter(self):

        if 'submenu' in self.menuPosition[self.menuCoords[-1]]:
            lcd.display('Entering submenu for [' + self.menuPosition[self.menuCoords[-1]]['name'] + ']', 1)
            self.menuCoords.append(0)
            self.setMenuPosition()
            self.loadState(MenuNav)
            self.runState()
        elif 'fn' in self.menuPosition[self.menuCoords[-1]]:
            lcd.display('Entering [' + self.menuPosition[self.menuCoords[-1]]['name'] + '] function', 1)
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
            self.loadState(PresetNav)  # this will become the gvars.presets state
            self.runState()



# ______________________________________________________________________________


class SelectSong(Navigator):
    def __init__(self):
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.nextState = eval(self.menuPosition[self.menuCoords[-1]]['fn'][1])
        self.display()

    def display(self):
        lcd.display('Select song', 1)
        lcd.display(str(gvars.preset + 1) + " " + str(self.setlistList[gvars.preset]), 2)

    # next song
    def right(self):
        if (gvars.preset < len(self.setlistList) - 1):
            gvars.preset += 1
        self.display()

    # previous song
    def left(self):
        if (gvars.preset > 0):
            gvars.preset -= 1
        self.display()

    def enter(self):
        self.loadState(self.nextState)
        self.runState()

    def cancel(self):
        self.loadState(MenuNav)
        self.runState()


# ______________________________________________________________________________

class MoveSong(Navigator):
    def __init__(self):
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        self.prevState = eval(self.menuPosition[self.menuCoords[-1]]['fn'][0])
        self.display()

    def display(self):
        lcd.display('Moving song', 1)
        lcd.display(str(gvars.preset + 1) + " " + str(self.setlistList[gvars.preset]), 2)

    # Move song up the setlist
    def left(self):
        if (gvars.preset > 0):
            self.setlistList[int(gvars.preset)], self.setlistList[int(gvars.preset) - 1] = self.setlistList[
                                                                                               int(gvars.preset) - 1], \
                                                                                           self.setlistList[
                                                                                               int(gvars.preset)]
            gvars.preset -= 1
            # write_setlist(self.setlistList)
        self.display()

    # Move song down the setlist
    def right(self):
        if (gvars.preset < len(self.setlistList) - 1):
            self.setlistList[int(gvars.preset)], self.setlistList[int(gvars.preset) + 1] = self.setlistList[
                                                                                               int(gvars.preset) + 1], \
                                                                                           self.setlistList[
                                                                                               int(gvars.preset)]
            gvars.preset += 1
            # write_setlist(self.setlistList)
        self.display()

    def enter(self):
        write_setlist(self.setlistList)
        self.loadState(self.prevState)
        self.runState()

    def cancel(self):
        self.loadState(self.prevState)
        self.runState()


# ______________________________________________________________________________

class SetlistRemoveMissing(Navigator):
    def __init__(self):

        lcd.display('Remove missing songs? [Y/N]', 2)

    def enter(self):

        songsInSetlist = open(SETLIST_FILE_PATH).read().splitlines()
        i = 0
        for song in songsInSetlist:
            if ('* ' in song):
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


# ______________________________________________________________________________


class DeleteSong(Navigator):
    def __init__(self):
        self.prevState = eval(self.menuPosition[self.menuCoords[-1]]['fn'][0])
        self.setlistList = open(SETLIST_FILE_PATH).read().splitlines()
        lcd.display('Are you sure? [Y/N]', 1)
        lcd.display('WARNING: will crash if we delete all songs', 2)

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


# ______________________________________________________________________________


class MaxPolyphonyConfig(Navigator):
    def __init__(self):
        self.display()

    def display(self):
        lcd.display('Max polyphony', 1)
        lcd.display(str(self.MAX_POLYPHONY) + ' (1-128)', 2)


    def left(self):
        self.MAX_POLYPHONY = max(self.MAX_POLYPHONY - 8, 1)
        self.display()

    def right(self):
        self.MAX_POLYPHONY = min(self.MAX_POLYPHONY + 8, 128)
        self.display()

    def enter(self):
        self.writeConfig()
        print '-- requires a restart --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()

    def cancel(self):
        self.enter()


# ______________________________________________________________________________

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
        print '-- requires a restart (maybe?) --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()

    def cancel(self):
        self.enter()


# ______________________________________________________________________________

class ChannelsConfig(Navigator):
    def __init__(self):
        self.options = [1, 2, 4, 6, 8]
        self.i = 1
        for x in self.options:
            if x == self.CHANNELS:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        lcd.display('Audio Channels', 1)
        lcd.display('['+str(self.CHANNELS)+']' + ' (1,2,4,6,8)', 2)


    def left(self):
        if self.i > 0:
            self.i -= 1
        self.CHANNELS = max(self.options[self.i], self.options[0])
        self.display()

    def right(self):
        if self.i < len(self.options):
            self.i += 1
        self.CHANNELS = min(self.options[self.i], self.options[-1])
        self.display()

    def enter(self):
        self.writeConfig()
        print '-- requires a restart (maybe?) --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()

    def cancel(self):
        self.enter()


# ______________________________________________________________________________

class BufferSizeConfig(Navigator):
    def __init__(self):
        self.options = [16, 32, 64, 128, 256, 512, 1024, 2048]
        self.i = 3
        for x in self.options:
            if x == self.BUFFERSIZE:
                self.i = self.options.index(x)

    def display(self):
        lcd.display('Buffer size', 1)
        lcd.display(str(self.BUFFERSIZE), 2)

    def left(self):
        if self.i > 0:
            self.i -= 1
        self.BUFFERSIZE = max(self.options[self.i], self.options[0])
        self.display()

    def right(self):
        if self.i < len(self.options):
            self.i += 1
        self.BUFFERSIZE = min(self.options[self.i], self.options[-1])
        self.display()

    def enter(self):
        self.writeConfig()
        print '-- requires a restart (maybe?) --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()

    def cancel(self):
        self.enter()


# ______________________________________________________________________________

class SampleRateConfig(Navigator):
    def __init__(self):
        self.options = [44100, 48000, 96000]
        self.i = 0
        for x in self.options:
            if x == self.SAMPLERATE:
                self.i = self.options.index(x)

    def display(self):
        lcd.display('Sample rate', 1)
        lcd.display(str(self.SAMPLERATE), 2)

    def left(self):
        if self.i > 0:
            self.i -= 1
        self.SAMPLERATE = max(self.options[self.i], self.options[0])
        self.display()

    def right(self):
        if self.i < len(self.options):
            self.i += 1
        self.SAMPLERATE = min(self.options[self.i], self.options[-1])
        self.display()

    def enter(self):
        self.writeConfig()
        print '-- requires a restart (maybe?) --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)
        self.runState()

    def cancel(self):
        self.enter()


# ______________________________________________________________________________

class MasterVolumeConfig(Navigator):
    def __init__(self):


        buttonDown = False
        self.display()

    def display(self):
        lcd.display('Master volume', 1)
        lcd.display(self.GLOBAL_VOLUME, 2)


    def left(self):
        self.GLOBAL_VOLUME = max(self.GLOBAL_VOLUME - 4, 0)
        self.display()

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
        self.display()

    def enter(self):
        self.writeConfig()
        self.loadState(MenuNav)
        self.runState()

    def cancel(self):
        self.writeConfig()
        self.loadState(MenuNav)
        self.runState()


# _____________________________________________________________________________

class MidiMapper(Navigator):
    MIDI_LEARN = False

    def __init__(self):
        MidiMapper.MIDI_LEARN = True
        # self.next_state = eval(str(self.menuPosition['fn'][1]))

    def learn(self, src, message):
        self.deviceName = src[:src.rfind(" "):]  # Strips the port number(s) from after the final space.
        # These numbers change depending on the USB port.
        self.midiMessage = message
        MidiMapper.MIDI_LEARN = False
        self.writeMidiDeviceConfig()

    def enter(self):
        print 'here'
        # self.loadState(self.next_state)
        # self.runState()

    def writeMidiDeviceConfig(self):
        # print self.deviceName
        # print self.midiMessage

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


# ______________________________________________________________________________




# new_song_selector = SelectSong()
# new_song_selector.next()

# def foldernames_and_setlist_match():
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
# if (os.path.isfile(SETLIST_FILE_PATH)):
#    print ('exists')
#    print (foldernames_and_setlist_match())
# else:
#    print ('nup')
#    setlist = open(SETLIST_FILE_PATH, "w")
#    for song_folder in SONG_FOLDERS_LIST:
#        setlist.write(song_folder + '\n')
#    
#    setlist.close()
#
