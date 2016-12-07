#  SamplerBox Navigator
#
#  author:    Alex MacRae (alex.finlay.macrae@gmail.com)
#  url:       https://github.com/alexmacrae/
#  license:   Creative Commons ShareAlike 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)
#
#  samplerbox2.py: Main file

import threading
import time

import configparser

import configparser_samplerbox as cs
import globalvars as gv
import loadsamples as ls
import menudict


# ______________________________________________________________________________

class Navigator:
    menu = menudict.menu

    state = None
    menu_coords = [0]
    menu_pointer = 0
    function = None
    config = configparser.ConfigParser()

    def __init__(self, state_init):
        Navigator.state = state_init
        self.load_state(self.state)

    def load_state(self, which_class):
        Navigator.state = which_class()

    def get_menu_path_str(self):

        menu_message = self.get_menu().get(self.menu_pointer).get('name')
        return menu_message

    def get_menu(self, mc=None):
        if not mc:
            mc = self.menu_coords
        menu = self.menu.get('submenu')

        i = 0
        while i < len(mc):
            if i > 0:
                menu = menu.get(mc[i - 1]).get('submenu')
            i += 1
        return menu


# ______________________________________________________________________________





class PresetNav(Navigator):
    def __init__(self):

        print '-= Preset world =-'
        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE
        gv.displayer.disp_change(changed_var='preset')
        # gv.displayer.disp_change('preset') # already called in ActuallyLoad()

    def right(self):
        gv.preset += 1
        gv.displayer.LCD_SYS.reset_after_timeout()
        gv.currvoice = 1
        if (gv.preset >= gv.NUM_FOLDERS):
            gv.preset = 0
        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE  # need to set if interrupted by utils left/right
        gv.displayer.disp_change('preset')
        ls.LoadSamples()

    def left(self):
        gv.preset -= 1
        gv.displayer.LCD_SYS.reset_after_timeout()
        gv.currvoice = 1
        if (gv.preset < 0):
            gv.preset = gv.NUM_FOLDERS - 1
        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE  # need to set if interrupted by utils left/right
        gv.displayer.disp_change('preset')
        ls.LoadSamples()

    def enter(self):
        self.load_state(MenuNav)

    def cancel(self):  # can remove empty class methods
        self.load_state(UtilsView)


# ______________________________________________________________________________


class UtilsView(PresetNav):
    def __init__(self):

        print '-= Utils view =-'
        gv.displayer.menu_mode = gv.displayer.DISP_UTILS_MODE
        gv.displayer.disp_change(changed_var='util')
        self.timeout_start = time.time()
        self.UtilsThread = threading.Thread(target=self.display_utils)
        self.UtilsThread.daemon = True
        self.UtilsThread.start()

    def display_utils(self):
        looping = True
        while looping:
            now = time.time()
            if (now - self.timeout_start) < 3:
                gv.displayer.disp_change(changed_var='util')
                time.sleep(0.25)
            else:
                self.load_state(PresetNav)
                looping = False

            time.sleep(0.25)

    # def right(self):
    #     pass
    #
    # def left(self):
    #     pass

    def enter(self):
        self.load_state(MenuNav)

    def cancel(self):  # can remove empty class methods
        self.timeout_start = time.time()


# ______________________________________________________________________________

function_to_map = None
function_nice_name = None


class MenuNav(Navigator):
    def __init__(self):

        self.menu_pointer = self.menu_coords[-1]
        gv.displayer.menu_mode = gv.displayer.DISP_MENU_MODE
        gv.displayer.disp_change(changed_var=self.get_menu_path_str().center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(changed_var='-' * 20, line=2, timeout=0)
        gv.displayer.disp_change(changed_var='', line=3, timeout=0)
        gv.displayer.disp_change(changed_var='', line=4, timeout=0)

    def left(self):

        if self.menu_pointer > 0:
            self.menu_pointer -= 1
            self.menu_coords[-1] = self.menu_pointer
            gv.displayer.disp_change(self.get_menu().get(self.menu_pointer).get('name').center(gv.LCD_COLS, ' '), line=1, timeout=0)

    def right(self):

        if self.menu_pointer < len(self.get_menu()) - 1:
            self.menu_pointer += 1
            self.menu_coords[-1] = self.menu_pointer
            gv.displayer.disp_change((self.get_menu().get(self.menu_pointer).get('name')).center(gv.LCD_COLS, ' '), line=1, timeout=0)

    def enter(self):
        global function_to_map, function_nice_name
        menu = self.get_menu().get(self.menu_pointer)
        try:
            if menu.has_key('submenu'):
                # print '##### Entering submenu for [' + menu.get('name') + '] #####'
                if menu.has_key('function_to_map'):
                    function_to_map = menu.get('function_to_map')
                    function_nice_name = menu.get('name')
                self.menu_coords.append(0)
                self.load_state(MenuNav)
            if menu.has_key('fn'):
                if (menu.get('fn') == 'MidiLearn') or (menu.get('fn') == 'DeleteMidiMap'):
                    self.menu_coords.append(0)
                    Navigator.state = eval(menu.get('fn'))(function_to_map, function_nice_name)
                elif isinstance(menu.get('fn'), list):
                    Navigator.state = eval(menu.get('fn')[0])(eval(menu.get('fn')[1]))  # for SelectSong
                else:
                    Navigator.state = eval(menu.get('fn'))()


        except:
            pass

    def cancel(self):
        if len(self.menu_coords) > 1:
            self.menu_coords.pop()
            self.load_state(MenuNav)
        else:
            self.load_state(PresetNav)  # this will become the gv.presets state


# ______________________________________________________________________________


class SelectSong(Navigator):
    def __init__(self, next_state):
        self.setlist_list = open(gv.SETLIST_FILE_PATH).read().splitlines()
        self.next_state = next_state
        self.display()

    def display(self):
        gv.displayer.disp_change('Select song'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change((str(gv.preset + 1) + " " + str(self.setlist_list[gv.preset])).center(gv.LCD_COLS, ' '), line=2)

    # next song
    def right(self):
        if (gv.preset < len(self.setlist_list) - 1):
            gv.preset += 1
        self.display()

    # previous song
    def left(self):
        if (gv.preset > 0):
            gv.preset -= 1
        self.display()

    def enter(self):
        self.load_state(self.next_state)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class MoveSong(Navigator):
    def __init__(self):
        self.setlist_list = open(gv.SETLIST_FILE_PATH).read().splitlines()
        self.prev_state = SelectSong
        self.display()

    def display(self):
        gv.displayer.disp_change('Moving song'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change((str(gv.preset + 1) + " " + str(self.setlist_list[gv.preset])).center(gv.LCD_COLS, ' '), line=2)

    # Move song up the setlist
    def left(self):
        if (gv.preset > 0):
            self.setlist_list[gv.preset], \
            self.setlist_list[gv.preset - 1] = self.setlist_list[gv.preset - 1], self.setlist_list[gv.preset]
            gv.preset -= 1
            # write_setlist(self.setlist_list)
        self.display()

    # Move song down the setlist
    def right(self):
        if (gv.preset < len(self.setlist_list) - 1):
            self.setlist_list[gv.preset], \
            self.setlist_list[gv.preset + 1] = self.setlist_list[gv.preset + 1], self.setlist_list[gv.preset]
            gv.preset += 1
            # write_setlist(self.setlist_list)
        self.display()

    def enter(self):
        gv.setlist.write_setlist(self.setlist_list)
        Navigator.state = self.prev_state(MoveSong)

    def cancel(self):
        Navigator.state = self.prev_state(MoveSong)


# ______________________________________________________________________________

class SetlistRemoveMissing(Navigator):
    def __init__(self):

        gv.displayer.disp_change('Remove'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change('missing songs?'.center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def enter(self):

        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()
        i = 0
        for song in songs_in_setlist:
            if ('* ' in song):
                del songs_in_setlist[i]
                gv.setlist.write_setlist(songs_in_setlist)
            i += 1

        self.load_state(MenuNav)

    def right(self):
        pass

    def left(self):
        pass

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________


class DeleteSong(Navigator):
    def __init__(self):
        self.prev_state = eval(self.menu_position[self.menu_coords[-1]]['fn'][0])
        self.setlist_list = open(gv.SETLIST_FILE_PATH).read().splitlines()
        gv.displayer.disp_change('Are you sure? [Y/N]'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change('WARNING: will crash if we delete all songs'.center(gv.LCD_COLS, ' '), line=2)

    def enter(self):
        print self.setlist_list
        del self.setlist_list[gv.preset]
        gv.setlist.write_setlist(self.setlist_list)
        print self.setlist_list
        if gv.preset != 0:
            gv.preset -= 1

        self.load_state(self.prev_state)

    def cancel(self):
        self.load_state(self.prev_state)


# ______________________________________________________________________________



class MidiLearn(Navigator):
    def __init__(self, function_to_map, function_nice_name):

        self.midimaps = gv.midimaps
        gv.learningMode = True
        self.function_to_map = function_to_map
        self.function_nice_name = function_nice_name
        self.learnedMidiMessage = None
        self.learnedMidiDevice = None
        gv.displayer.disp_change('Learning', line=1, timeout=0)
        gv.displayer.disp_change('Select a control', line=2)

    def sendControlToMap(self, learnedMidiMessage, learnedMidiDevice):
        self.learnedMidiMessage = learnedMidiMessage
        self.learnedMidiDevice = learnedMidiDevice

        mapping_str = '%s,%s:%s' % (
            str(learnedMidiMessage[0]),
            str(learnedMidiMessage[1]),
            str(learnedMidiDevice)
        )

        gv.displayer.disp_change(mapping_str.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change('Save mapping?'.center(gv.LCD_COLS, ' '), line=2, timeout=0)
        # self.enter()  #

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
                print 'WARNING:', messageKey, 'is already mapped to:', mm.get(src).get(messageKey).get('name')
                print 'Do you want to overwrite? Well too bad - doing it anyway ;)'

            mm.get(src)[messageKey] = {'name': self.function_nice_name, 'fn': self.function_to_map}

            import midimaps
            midimaps.MidiMapping().save_maps(mm)

            self.cancel()  # Go back


        except:
            print 'failed for some reason'
            pass

    def cancel(self):
        # print devices
        gv.displayer.disp_change('-' * 20, line=2, timeout=0)
        gv.learningMode = False
        if len(self.menu_coords) > 1:
            self.menu_coords.pop()
            self.load_state(MenuNav)
        else:
            self.load_state(MenuNav)  # this will become the gv.presets state


# ______________________________________________________________________________

class DeleteMidiMap(Navigator):
    def __init__(self, functionToUnmap, function_nice_name):

        self.midimaps = gv.midimaps
        # src[:src.rfind(" "):] # use this to strip the port number off the end of src

        self.functionToUnmap = functionToUnmap
        self.function_nice_name = function_nice_name

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
        half_screen = gv.LCD_COLS / 2
        first_line = '%s DEL:[%s]' % (self.function_nice_name[:half_screen], str(self.i + 1))

        gv.displayer.disp_change(first_line.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(str(mm[self.i][0])[:half_screen] + str(mm[self.i][1][:half_screen]), line=2, timeout=0)

    def left(self):
        if self.i > 0:
            self.i -= 1
            self.deleteDisplay()

    def right(self):
        if self.i < len(self.matchedMappings) - 1:
            self.i += 1
            self.deleteDisplay()

    def enter(self):
        mm = self.midimaps
        deviceName = self.matchedMappings[self.i][0]
        midiKey = self.matchedMappings[self.i][1]
        try:
            for device in mm.iteritems():
                if deviceName in device:
                    device[1].pop(midiKey)

            import midimaps
            midimaps.MidiMapping().save_maps(mm)
            self.cancel()  # Go back

        except:
            print 'failed for some reason'
            pass

    def cancel(self):

        gv.learningMode = False
        if len(self.menu_coords) > 1:
            self.menu_coords.pop()
            self.load_state(MenuNav)
        else:
            self.load_state(MenuNav)  # this will become the gv.presets state


# ______________________________________________________________________________


class MaxPolyphonyConfig(Navigator):
    def __init__(self):
        self.MAX_POLYPHONY = gv.MAX_POLYPHONY
        self.display()

    def display(self):
        gv.displayer.disp_change('Max polyphony'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change((str(self.MAX_POLYPHONY) + ' [1-128]').center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        self.MAX_POLYPHONY = max(self.MAX_POLYPHONY - 1, 1)
        self.display()

    def right(self):
        self.MAX_POLYPHONY = min(self.MAX_POLYPHONY + 1, 128)
        self.display()

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'MAX_POLYPHONY', str(self.MAX_POLYPHONY))
        gv.MAX_POLYPHONY = self.MAX_POLYPHONY
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class MidiChannelConfig(Navigator):
    def __init__(self):
        print '-= MIDI Channel !IMPORTANT: All MIDI ports are open with rtmidi2 =-'
        self.MIDI_CHANNEL = gv.MIDI_CHANNEL
        self.display()

    def display(self):
        gv.displayer.disp_change('MIDI Channel'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change((str(self.MIDI_CHANNEL) + ' [1-16](0=ALL)').center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        self.MIDI_CHANNEL = max(self.MIDI_CHANNEL - 1, 0)
        self.display()

    def right(self):
        self.MIDI_CHANNEL = min(self.MIDI_CHANNEL + 1, 16)
        self.display()

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'MIDI_CHANNEL', str(self.MIDI_CHANNEL))
        gv.MIDI_CHANNEL = self.MIDI_CHANNEL
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class ChannelsConfig(Navigator):
    def __init__(self):
        self.CHANNELS = gv.CHANNELS
        self.options = [1, 2, 4, 6, 8]
        self.i = 1
        for x in self.options:
            if x == self.CHANNELS:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        gv.displayer.disp_change('Audio Channels'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(('[' + str(self.CHANNELS) + ']' + ' (1,2,4,6,8)').center(gv.LCD_COLS, ' '), line=2, timeout=0)

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
        import sound
        cs.update_config('SAMPLERBOX CONFIG', 'CHANNELS', str(self.CHANNELS))
        gv.CHANNELS = self.CHANNELS
        sound.close_stream()
        sound.start_stream()
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class BufferSizeConfig(Navigator):
    def __init__(self):
        self.BUFFERSIZE = gv.BUFFERSIZE
        self.options = [16, 32, 64, 128, 256, 512, 1024, 2048]
        self.i = 3
        for x in self.options:
            if x == self.BUFFERSIZE:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        gv.displayer.disp_change('Buffer size'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(str(self.BUFFERSIZE).center(gv.LCD_COLS, ' '), line=2, timeout=0)

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
        import sound
        cs.update_config('SAMPLERBOX CONFIG', 'BUFFERSIZE', str(self.BUFFERSIZE))
        gv.BUFFERSIZE = self.BUFFERSIZE
        sound.close_stream()
        sound.start_stream()
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class SampleRateConfig(Navigator):
    def __init__(self):
        self.SAMPLERATE = gv.SAMPLERATE
        self.options = [44100, 48000, 96000]
        self.i = 0
        for x in self.options:
            if x == self.SAMPLERATE:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        gv.displayer.disp_change('Sample rate'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(str(self.SAMPLERATE).center(gv.LCD_COLS, ' '), line=2, timeout=0)

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
        import sound
        cs.update_config('SAMPLERBOX CONFIG', 'SAMPLERATE', str(self.SAMPLERATE))
        gv.SAMPLERATE = self.SAMPLERATE
        sound.close_stream()
        sound.start_stream()
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________


class MasterVolumeConfig(Navigator):
    def __init__(self):
        self.display()

    def display(self):
        gv.displayer.disp_change('Master volume'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(str(gv.global_volume).center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        gv.global_volume = max(gv.global_volume - 4, 0)
        gv.ac.master_volume.setvolume(gv.global_volume * 1.27)
        self.display()

    def right(self):
        gv.global_volume = min(gv.global_volume + 4, 100)
        gv.ac.master_volume.setvolume(gv.global_volume * 1.27)
        self.display()

    def enter(self):
        cs.update_config('SAMPLERBOX CONFIG', 'GLOBAL_VOLUME', str(gv.global_volume))
        self.load_state(MenuNav)

    def cancel(self):
        self.enter()


# _____________________________________________________________________________

from modules import definitionparser


def set_global_from_keyword(keyword, value):
    keyword = keyword.strip('%%')
    if isinstance(value, str): value = value.title()
    for gvar, k in definitionparser.keywords_to_try:
        if k == keyword:
            if 'release' in keyword: value = value * 10000
            print '>>>>>>>Setting global from keyword. %s: %s' % (keyword, str(value))  # debug
            exec (gvar + '=value')  # set the global variable


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class EditDefinition(Navigator):
    def __init__(self):

        self.in_a_mode = False
        self.mode = 0
        self.selected_keyword = None
        self.allowed_values = None
        self.i = 0
        self.selected_keyword_value = None

        self.setlist_list = open(gv.SETLIST_FILE_PATH).read().splitlines()
        self.prev_state = SelectSong
        self.song_name = self.setlist_list[int(gv.preset)]
        self.dp = definitionparser.DefinitionParser(self.song_name)
        self.keywords_dict = self.dp.keywords_dict
        self.keywords_defaults_dict = self.dp.keywords_defaults_dict
        self.display()

    def display(self):
        if not self.in_a_mode:
            keyword_str = self.keywords_dict[self.mode].items()[0][0].strip('%%').title()
            gv.displayer.disp_change(self.song_name.center(gv.LCD_COLS, ' '), line=1, timeout=0)
            gv.displayer.disp_change(keyword_str.center(gv.LCD_COLS, ' '), line=2, timeout=0)
        else:
            keyword = self.keywords_dict[self.mode].items()[0][0]
            keyword_str = keyword.strip('%%').title()
            if isinstance(self.allowed_values, list):
                value_str = str(self.allowed_values[self.i])
            elif isinstance(self.allowed_values, tuple):
                value_str = str(self.i)
            line_str = keyword_str + ' ' + value_str
            gv.displayer.disp_change(self.song_name.center(gv.LCD_COLS, ' '), line=1, timeout=0)
            gv.displayer.disp_change(line_str.center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        if not self.in_a_mode:
            if not self.mode <= 0:
                self.mode -= 1
        else:
            if isinstance(self.allowed_values, list):
                if not self.i <= 0:
                    self.i -= 1
                    self.selected_keyword_value = self.allowed_values[self.i]
            elif isinstance(self.allowed_values, tuple):
                self.i = clamp(int(self.i) - 1, self.allowed_values[0], self.allowed_values[1])
                self.selected_keyword_value = self.i

            set_global_from_keyword(self.selected_keyword, self.selected_keyword_value)

        self.display()

    def right(self):
        if not self.in_a_mode:
            if not self.mode >= len(self.keywords_dict) - 1:
                self.mode += 1
        else:
            if isinstance(self.allowed_values, list):
                if not self.i >= len(self.allowed_values) - 1:
                    self.i += 1
                    self.selected_keyword_value = self.allowed_values[self.i]
            elif isinstance(self.allowed_values, tuple):
                self.i = clamp(int(self.i) + 1, self.allowed_values[0], self.allowed_values[1])
                self.selected_keyword_value = self.i

            set_global_from_keyword(self.selected_keyword, self.selected_keyword_value)

        self.display()

    def enter(self):
        if not self.in_a_mode:
            self.in_a_mode = True
            self.selected_keyword = self.keywords_dict[self.mode].items()[0][0]
            self.allowed_values = self.keywords_dict[self.mode].items()[0][1]
            if self.dp.existing_patterns.has_key(self.selected_keyword):

                self.selected_keyword_value = self.dp.existing_patterns[self.selected_keyword]
                if isinstance(self.allowed_values, list):
                    self.i = self.allowed_values.index(self.selected_keyword_value)
                elif isinstance(self.allowed_values, tuple):
                    self.i = self.selected_keyword_value

                print '### %s exists with a value of %s ###' \
                      % (self.selected_keyword.title(), str(self.selected_keyword_value).title())
            else:
                self.i = int(self.keywords_defaults_dict[self.selected_keyword])
                if isinstance(self.allowed_values, list):
                    self.selected_keyword_value = self.keywords_dict[self.i]
                elif isinstance(self.allowed_values, tuple):
                    self.selected_keyword_value = self.i
                print '### %s does not exist. Set default: %d ###' \
                      % (self.selected_keyword.title(), self.i)
            self.display()
        elif self.in_a_mode:

            if isinstance(self.allowed_values, list):
                self.dp.set_new_keyword(self.selected_keyword, str(self.selected_keyword_value))
            elif isinstance(self.allowed_values, tuple):
                self.dp.set_new_keyword(self.selected_keyword, int(self.selected_keyword_value))

            self.dp.compare_existing_patterns()
            self.dp.write_definition_file()

            self.load_state(EditDefinition)

    def cancel(self):
        if not self.in_a_mode:
            Navigator.state = self.prev_state(EditDefinition)
        elif self.in_a_mode:
            self.in_a_mode = False
            self.display()


class AudioDevice(Navigator):
    def __init__(self):
        import sound
        self.all_audio_devices = sound.get_all_audio_devices()
        self.i = 0
        self.device_name = str(self.all_audio_devices[self.i].get('name'))
        self.display(False)

    def display(self, changed=False):
        gv.displayer.disp_change('Choose new audio device'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        if changed:
            gv.displayer.disp_change('Device changed'.center(gv.LCD_COLS, ' '), line=2, timeout=0)
            gv.displayer.disp_change(self.device_name.center(gv.LCD_COLS, ' '), line=3, timeout=0)
        else:
            gv.displayer.disp_change(self.device_name.center(gv.LCD_COLS, ' '), line=2, timeout=0)
            gv.displayer.disp_change('', line=3, timeout=0)

    def left(self):
        if self.i > 0:
            self.i -= 1
            self.device_name = str(self.all_audio_devices[self.i].get('name'))
            self.display(False)

    def right(self):
        if self.i < len(self.all_audio_devices) - 1:
            self.i += 1
            self.device_name = str(self.all_audio_devices[self.i].get('name'))
            self.display(False)

    def enter(self):
        import sound
        sound.set_audio_device(self.device_name)
        cs.update_config('SAMPLERBOX CONFIG', 'AUDIO_DEVICE_NAME', self.device_name)
        self.display(changed=True)

    def cancel(self):
        self.load_state(MenuNav)


class ChordMode(Navigator):
    def __init__(self):

        self.AVAILABLE_CHORD_SETS = gv.ac.autochorder.AVAILABLE_CHORDS_SETS
        self.display()

    def display(self):
        if gv.ac.autochorder.chord_set_index == 1 or gv.ac.autochorder.chord_set_index == 2:
            first_line = 'Mode (Key:%s)' % gv.NOTES[gv.ac.autochorder.current_key_index].capitalize()
        else:
            first_line = 'Mode'
        chord_mode_name = self.AVAILABLE_CHORD_SETS[gv.ac.autochorder.chord_set_index][0]

        gv.displayer.disp_change(first_line.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(chord_mode_name.center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        if gv.ac.autochorder.chord_set_index > 0:
            gv.ac.autochorder.chord_set_index -= 1
            gv.ac.autochorder.change_mode(gv.ac.autochorder.chord_set_index)
            self.display()

    def right(self):
        if gv.ac.autochorder.chord_set_index < len(self.AVAILABLE_CHORD_SETS) - 1:
            gv.ac.autochorder.chord_set_index += 1
            gv.ac.autochorder.change_mode(gv.ac.autochorder.chord_set_index)
            self.display()

    def enter(self):
        self.cancel()

    def cancel(self):
        self.load_state(MenuNav)


class ChordKey(Navigator):
    def __init__(self):
        self.display()

    def display(self):
        key_name = gv.NOTES[gv.ac.autochorder.current_key_index].capitalize()
        gv.displayer.disp_change('Key'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(key_name.center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        if gv.ac.autochorder.current_key_index > 0:
            gv.ac.autochorder.current_key_index -= 1
            gv.ac.autochorder.change_key(gv.ac.autochorder.current_key_index)
            self.display()

    def right(self):
        if gv.ac.autochorder.current_key_index < len(gv.NOTES) - 1:
            gv.ac.autochorder.current_key_index += 1
            gv.ac.autochorder.change_key(gv.ac.autochorder.current_key_index)
            self.display()

    def enter(self):
        self.cancel()

    def cancel(self):
        self.load_state(MenuNav)


class ToggleReverb(Navigator):
    def __init__(self):

        self.freeverb_state = gv.USE_FREEVERB
        self.display()

    def display(self):

        if self.freeverb_state:
            on_or_off_str = '[ON]/OFF'
        else:
            on_or_off_str = 'ON/[OFF]'

        gv.displayer.disp_change('Reverb'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(on_or_off_str.center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        self.freeverb_state = True
        self.display()

    def right(self):
        self.freeverb_state = False
        self.display()

    def enter(self):
        import sound
        gv.USE_FREEVERB = self.freeverb_state
        cs.update_config('SAMPLERBOX CONFIG', 'USE_FREEVERB', str(self.freeverb_state))
        sound.close_stream()
        sound.start_stream()
        self.cancel()

    def cancel(self):
        self.load_state(MenuNav)