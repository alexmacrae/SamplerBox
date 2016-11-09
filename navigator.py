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
import loadsamples as ls
import globalvars as gvars
import lcd
import menudict
import configparser_samplerbox as cs


def write_setlist(list_to_write):
    print('-= WRITING NEW SETLIST =-')
    setlist = open(gvars.SETLIST_FILE_PATH, "w")
    list_to_write = list(filter(None, list_to_write))  # remove empty strings / empty lines
    for song in list_to_write:
        setlist.write(song + '\n')
    setlist.close()


def findMissingFolders():
    # Check to see if the song name in the setlist matches the name of a folder.
    # If it doesn't, mark it by prepending an *asterix and rewrite the setlist file.

    songsInSetlist = open(gvars.SETLIST_FILE_PATH).read().splitlines()
    songsInSetlist = list(filter(None, songsInSetlist))  # remove empty strings / empty lines
    changes = False
    k = 0
    for song_name in songsInSetlist:
        i = 0
        for song_folder_name in gvars.SONG_FOLDERS_LIST:

            if (song_name == song_folder_name):
                # print(song_name + ' was found')
                break
            elif (song_name.replace('* ', '') == song_folder_name):
                # print(song_name + ' was found - previous lost')
                songsInSetlist[k] = song_name.replace('* ', '')
                # break
            else:
                if (i == len(gvars.SONG_FOLDERS_LIST) - 1):
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

    songsInSetlist = open(gvars.SETLIST_FILE_PATH).read().splitlines()
    songsInSetlist = list(filter(None, songsInSetlist))  # remove empty strings / empty lines
    changes = False

    if (set(songsInSetlist).intersection(gvars.SONG_FOLDERS_LIST) != len(gvars.SONG_FOLDERS_LIST) and len(
            songsInSetlist) != 0):

        for song_folder_name in gvars.SONG_FOLDERS_LIST:
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
        songsInSetlist = gvars.SONG_FOLDERS_LIST
        changes = True
        print ('Setlist empty - adding all foldings')

    # print(songsInSetlist)
    if (changes):
        write_setlist(songsInSetlist)
    else:
        print('-= No new folders found =-\n')

        # ______________________________________________________________________________


def removeMissingSetlistSongs():
    songsInSetlist = open(gvars.SETLIST_FILE_PATH).read().splitlines()
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
    menu = menudict.menu

    state = None
    menuCoords = [0]
    menuPointer = 0
    function = None
    config = configparser.ConfigParser()

    def __init__(self, initState):
        Navigator.state = initState
        self.loadState(Navigator.state)

    def loadState(self, theClass):
        Navigator.state = theClass()

    def getMenuPathStr(self):

        menuMsg = self.getMenu().get(self.menuPointer).get('name')

        return menuMsg

    def getMenu(self, mc=None):
        if not mc:
            mc = Navigator.menuCoords
        menu = Navigator.menu.get('submenu')
        i = 0
        while i < len(mc):
            if i > 0:
                menu = menu.get(mc[i - 1]).get('submenu')
            i += 1
        return menu


# ______________________________________________________________________________





class PresetNav(Navigator):
    def __init__(self):

        self.setlistList = open(gvars.SETLIST_FILE_PATH).read().splitlines()
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

        lcd.display(s1, 1, is_priority=True)
        lcd.display(s2, 2, is_priority=True)

    def right(self):
        gvars.preset += 1
        lcd.resetModes()
        lcd.inPresetMode = True
        gvars.currvoice = 1
        if (gvars.preset >= self.numFolders):
            gvars.preset = 0
        self.display()
        ls.LoadSamples()

    def left(self):
        gvars.preset -= 1
        lcd.resetModes()
        lcd.inPresetMode = True
        gvars.currvoice = 1
        if (gvars.preset < 0):
            gvars.preset = self.numFolders - 1
        self.display()
        ls.LoadSamples()

    def enter(self):
        self.loadState(MenuNav)

    def cancel(self):  # can remove empty class methods
        lcd.TimeOut = lcd.TimeOutReset
        lcd.resetModes()
        lcd.inSysMode = True
        # eg CPU/RAM, battery life, time, wifi/bluetooth status


# ______________________________________________________________________________
functionToMap = None
functionNiceName = None


class MenuNav(Navigator):
    def __init__(self):

        self.menuPointer = self.menuCoords[-1]

        lcd.resetModes()

        lcd.inMenuMode = True
        lcd.display(self.getMenuPathStr(), 1)
        lcd.display('-------------------------', 2)

    def left(self):

        if self.menuPointer > 0:
            self.menuPointer -= 1
            self.menuCoords[-1] = self.menuPointer
            lcd.display(self.getMenu().get(self.menuPointer).get('name'))
        else:
            lcd.display(self.getMenu().get(self.menuPointer).get('name') + '(start)')

    def right(self):

        if self.menuPointer < len(self.getMenu()) - 1:
            self.menuPointer += 1
            self.menuCoords[-1] = self.menuPointer
            lcd.display(self.getMenu().get(self.menuPointer).get('name'))
        else:
            lcd.display(self.getMenu().get(self.menuPointer).get('name') + '(end)')

    def enter(self):
        global functionToMap, functionNiceName
        menu = self.getMenu().get(self.menuPointer)
        try:
            if menu.has_key('submenu'):
                lcd.display('Entering submenu for [' + menu.get('name') + ']')
                if menu.has_key('functionToMap'):
                    functionToMap = menu.get('functionToMap')
                    functionNiceName = menu.get('name')
                self.menuCoords.append(0)
                self.loadState(MenuNav)
            if menu.has_key('fn'):

                if (menu.get('fn') == 'MidiLearn') or (menu.get('fn') == 'DeleteMidiMap'):
                    self.menuCoords.append(0)
                    Navigator.state = eval(menu.get('fn'))(functionToMap, functionNiceName)
                elif isinstance(menu.get('fn'), list):
                    Navigator.state = eval(menu.get('fn')[0])(eval(menu.get('fn')[1]))  # for SelectSong
                else:
                    Navigator.state = eval(menu.get('fn'))()

        except:
            pass

    def cancel(self):
        if len(self.menuCoords) > 1:
            self.menuCoords.pop()
            self.loadState(MenuNav)
        else:
            self.loadState(PresetNav)  # this will become the gvars.presets state


# ______________________________________________________________________________


class SelectSong(Navigator):
    def __init__(self, nextState):
        self.setlistList = open(gvars.SETLIST_FILE_PATH).read().splitlines()
        self.nextState = nextState
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

    def cancel(self):
        self.loadState(MenuNav)


# ______________________________________________________________________________

class MoveSong(Navigator):
    def __init__(self):
        self.setlistList = open(gvars.SETLIST_FILE_PATH).read().splitlines()
        self.prevState = SelectSong
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
        Navigator.state = self.prevState(MoveSong)

    def cancel(self):
        Navigator.state = self.prevState(MoveSong)


# ______________________________________________________________________________

class SetlistRemoveMissing(Navigator):
    def __init__(self):

        lcd.display('Remove missing songs? [Y/N]', 2)

    def enter(self):

        songsInSetlist = open(gvars.SETLIST_FILE_PATH).read().splitlines()
        i = 0
        for song in songsInSetlist:
            if ('* ' in song):
                del songsInSetlist[i]
                write_setlist(songsInSetlist)
            i += 1

        self.loadState(MenuNav)

    def right(self):
        pass

    def left(self):
        pass

    def cancel(self):
        self.loadState(MenuNav)


# ______________________________________________________________________________


class DeleteSong(Navigator):
    def __init__(self):
        self.prevState = eval(self.menuPosition[self.menuCoords[-1]]['fn'][0])
        self.setlistList = open(gvars.SETLIST_FILE_PATH).read().splitlines()
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

    def cancel(self):
        self.loadState(self.prevState)


# ______________________________________________________________________________



class MidiLearn(Navigator):
    def __init__(self, functionToMap, functionNiceName):

        self.midimaps = gvars.midimaps
        # src[:src.rfind(" "):] # use this to strip the port number off the end of src

        gvars.learningMode = True
        self.functionToMap = functionToMap
        self.functionNiceName = functionNiceName
        self.learnedMidiMessage = None
        self.learnedMidiDevice = None
        lcd.display('Learning', 1)
        lcd.display('Select a control', 2)

    def sendControlToMap(self, learnedMidiMessage, learnedMidiDevice):
        self.learnedMidiMessage = learnedMidiMessage
        self.learnedMidiDevice = learnedMidiDevice
        lcd.display(str(learnedMidiMessage[0]) + ':' + str(learnedMidiMessage[1]) + ' ' + learnedMidiDevice, 2)
        self.enter()  #
        # print learnedMidiMessage, learnedMidiDevice

    def enter(self):

        mm = self.midimaps

        try:
            src = self.learnedMidiDevice
            messagetype = self.learnedMidiMessage[0]
            note = self.learnedMidiMessage[1]
            messageKey = (messagetype, note)
            if src not in mm:
                mm[src] = {}  # create new empty dict key for device
                print 'Creating new device in dict'
            else:
                print 'Device is in dict - do nothing'
            if messageKey not in mm.get(src):
                mm.get(src)[messageKey] = {}  # create new empty dict key for messageKey
                print 'Creating new dict for the messageKey'
            else:
                print '!! Already mapped to:', mm.get(src).get(messageKey).get('name')
                print 'Do you want to overwrite? Well too bad - doing it anyway ;)'

            mm.get(src)[messageKey] = {'name': self.functionNiceName, 'fn': self.functionToMap}

            import midimaps
            midimaps.MidiMapping().saveMaps(mm)

            self.cancel()  # Go back


        except:
            print 'failed for some reason'
            pass

    def cancel(self):
        # print devices
        lcd.display('----------------', 2)
        gvars.learningMode = False
        if len(self.menuCoords) > 1:
            self.menuCoords.pop()
            self.loadState(MenuNav)
        else:
            self.loadState(MenuNav)  # this will become the gvars.presets state


# ______________________________________________________________________________

class DeleteMidiMap(Navigator):
    def __init__(self, functionToUnmap, functionNiceName):

        self.midimaps = gvars.midimaps
        # src[:src.rfind(" "):] # use this to strip the port number off the end of src


        self.functionToUnmap = functionToUnmap
        self.functionNiceName = functionNiceName

        matchedMappings = {}
        i = 0
        for devices in self.midimaps.iteritems():
            deviceName = devices[0]
            deviceMaps = devices[1]
            for midiKey, midiKeyDict in deviceMaps.iteritems():
                # print mm2
                for midiKeyItem in midiKeyDict.iteritems():
                    fnName = midiKeyItem[1]
                    if fnName == functionToUnmap:
                        # Build a new dictionary to build dict addresses for matched keys

                        matchedMappings[i] = [deviceName, midiKey, functionToUnmap]
                        i += 1

        self.matchedMappings = matchedMappings
        self.i = 0

        self.deleteDisplay()

    def deleteDisplay(self):
        mm = self.matchedMappings
        functionNiceName = self.functionNiceName
        i = self.i
        # lcd.display(mm[i][2], 1)
        lcd.display(str(i + 1) + ' ' + functionNiceName, 1)
        lcd.display(str(mm[i][0])[:8] + str(mm[i][1][:8]), 2)

    def left(self):
        if self.i > 0:
            self.i -= 1
            self.deleteDisplay()

    def right(self):
        if self.i < len(self.matchedMappings) - 1:
            self.i += 1
            self.deleteDisplay()

    def enter(self):
        a = {}

        mm = self.midimaps
        deviceName = self.matchedMappings[self.i][0]
        midiKey = self.matchedMappings[self.i][1]
        functionToUnmap = self.matchedMappings[self.i][2]
        try:

            for device in mm.iteritems():
                if deviceName in device:
                    device[1].pop(midiKey)

            import midimaps
            midimaps.MidiMapping().saveMaps(mm)

            self.cancel()  # Go back


        except:
            print 'failed for some reason'
            pass

    def cancel(self):
        # print devices
        lcd.display('----------------', 2)
        gvars.learningMode = False
        if len(self.menuCoords) > 1:
            self.menuCoords.pop()
            self.loadState(MenuNav)
        else:
            self.loadState(MenuNav)  # this will become the gvars.presets state


# ______________________________________________________________________________


class MaxPolyphonyConfig(Navigator):
    def __init__(self):
        self.MAX_POLYPHONY = gvars.MAX_POLYPHONY
        self.display()

    def display(self):
        lcd.display('Max polyphony', 1)
        lcd.display(str(self.MAX_POLYPHONY) + ' (1-128)', 2)

    def left(self):
        self.MAX_POLYPHONY = max(self.MAX_POLYPHONY - 1, 1)
        self.display()

    def right(self):
        self.MAX_POLYPHONY = min(self.MAX_POLYPHONY + 1, 128)
        self.display()

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'MAX_POLYPHONY', str(self.MAX_POLYPHONY))
        gvars.MAX_POLYPHONY = self.MAX_POLYPHONY
        print '-- requires a restart --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)

    def cancel(self):
        self.loadState(MenuNav)


# ______________________________________________________________________________

class MidiChannelConfig(Navigator):
    def __init__(self):
        print '-= MIDI Channel !IMPORTANT: All MIDI ports are open with rtmidi2 =-'
        self.MIDI_CHANNEL = gvars.MIDI_CHANNEL
        self.display()

    def display(self):
        lcd.display('MIDI Channel', 1)
        lcd.display(str(self.MIDI_CHANNEL) + ' (1-128)', 2)

    def left(self):
        self.MIDI_CHANNEL = max(self.MIDI_CHANNEL - 1, 1)
        print self.MIDI_CHANNEL

    def right(self):
        self.MIDI_CHANNEL = min(self.MIDI_CHANNEL + 1, 16)
        print self.MIDI_CHANNEL

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'MIDI_CHANNEL', str(self.MIDI_CHANNEL))
        gvars.MIDI_CHANNEL = self.MIDI_CHANNEL
        print '-- requires a restart (maybe?) --'  # or a reinstantiation of the audio device
        self.loadState(MenuNav)

    def cancel(self):
        self.loadState(MenuNav)


# ______________________________________________________________________________

class ChannelsConfig(Navigator):
    def __init__(self):
        self.CHANNELS = gvars.CHANNELS
        self.options = [1, 2, 4, 6, 8]
        self.i = 1
        for x in self.options:
            if x == self.CHANNELS:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        lcd.display('Audio Channels', 1)
        lcd.display('[' + str(self.CHANNELS) + ']' + ' (1,2,4,6,8)', 2)

    def left(self):
        if self.i > 0:
            self.i -= 1
        self.CHANNELS = max(self.options[self.i], self.options[0])
        self.display()

    def right(self):
        if self.i < len(self.options) - 1:
            self.i += 1
        self.CHANNELS = min(self.options[self.i], self.options[-1])
        self.display()

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'CHANNELS', str(self.CHANNELS))
        gvars.CHANNELS = self.CHANNELS
        print '-- requires a restart (maybe?) --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)

    def cancel(self):
        self.loadState(MenuNav)


# ______________________________________________________________________________

class BufferSizeConfig(Navigator):
    def __init__(self):
        self.BUFFERSIZE = gvars.BUFFERSIZE
        self.options = [16, 32, 64, 128, 256, 512, 1024, 2048]
        self.i = 3
        for x in self.options:
            if x == self.BUFFERSIZE:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        lcd.display('Buffer size', 1)
        lcd.display(str(self.BUFFERSIZE), 2)

    def left(self):
        if self.i > 0:
            self.i -= 1
        self.BUFFERSIZE = max(self.options[self.i], self.options[0])
        self.display()

    def right(self):
        if self.i < len(self.options) - 1:
            self.i += 1
        self.BUFFERSIZE = min(self.options[self.i], self.options[-1])
        self.display()

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'BUFFERSIZE', str(self.BUFFERSIZE))
        gvars.BUFFERSIZE = self.BUFFERSIZE
        print '-- requires a restart (maybe?) --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)

    def cancel(self):
        self.loadState(MenuNav)


# ______________________________________________________________________________

class SampleRateConfig(Navigator):
    def __init__(self):
        self.SAMPLERATE = gvars.SAMPLERATE
        self.options = [44100, 48000, 96000]
        self.i = 0
        for x in self.options:
            if x == self.SAMPLERATE:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        lcd.display('Sample rate', 1)
        lcd.display(str(self.SAMPLERATE), 2)

    def left(self):
        if self.i > 0:
            self.i -= 1
        self.SAMPLERATE = max(self.options[self.i], self.options[0])
        self.display()

    def right(self):
        if self.i < len(self.options) - 1:
            self.i += 1
        self.SAMPLERATE = min(self.options[self.i], self.options[-1])
        self.display()

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'SAMPLERATE', str(self.SAMPLERATE))
        gvars.SAMPLERATE = self.SAMPLERATE
        print '-- requires a restart (maybe?) --'  # or a reinstantiation of the sounddevice
        self.loadState(MenuNav)

    def cancel(self):
        self.loadState(MenuNav)


# ______________________________________________________________________________

import midicallback

class MasterVolumeConfig(Navigator):

    def __init__(self):
        self.display()

    def display(self):
        lcd.display('Master volume', 1)
        lcd.display(str(gvars.GLOBAL_VOLUME), 2)

    def left(self):
        gvars.GLOBAL_VOLUME = max(gvars.GLOBAL_VOLUME - 4, 0)
        midicallback.MasterVolume().setvolume(gvars.GLOBAL_VOLUME * 1.27)
        self.display()

    def right(self):
        gvars.GLOBAL_VOLUME = min(gvars.GLOBAL_VOLUME + 4, 100)
        midicallback.MasterVolume().setvolume(gvars.GLOBAL_VOLUME * 1.27)
        self.display()

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'GLOBAL_VOLUME', str(gvars.GLOBAL_VOLUME))
        self.loadState(MenuNav)

    def cancel(self):
        self.enter()

# _____________________________________________________________________________


