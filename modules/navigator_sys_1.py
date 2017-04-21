#  SamplerBox Navigator
#
#  author:    Alex MacRae (alex.finlay.macrae@gmail.com)
#  url:       https://github.com/alexmacrae/
#  license:   Creative Commons ShareAlike 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)
#
#  samplerbox.py: Main file

import threading
import time
import configparser
# import configparser_samplerbox as cs
import globalvars as gv
import menudict


# ______________________________________________________________________________

class Navigator:
    menu = menudict.menu

    state = None
    menu_coords = [0]
    menu_pointer = 0
    config = configparser.ConfigParser()
    text_scroller = None

    def __init__(self, state_init):
        Navigator.state = state_init
        Navigator.text_scroller = TextScroller()
        self.load_state(self.state)

    def load_state(self, which_class, params=None):
        if params != None:
            Navigator.state = which_class(params)
        else:
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
        self.text_scroller.stop()
        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE
        gv.displayer.disp_change('preset')

    def right(self):
        gv.preset += 1
        gv.displayer.LCD_SYS.reset_after_timeout()
        gv.currvoice = 1
        if gv.preset >= len(gv.samples_indices):
            gv.preset = 0
        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE  # need to set if interrupted by utils left/right
        gv.ls.load_samples()
        # gv.displayer.disp_change('preset') # load_samples calls this

    def left(self):
        gv.preset -= 1
        gv.displayer.LCD_SYS.reset_after_timeout()
        gv.currvoice = 1
        if gv.preset < 0:
            gv.preset = len(gv.samples_indices) - 1
        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE  # need to set if interrupted by utils left/right
        gv.ls.load_samples()
        # gv.displayer.disp_change('preset') # load_samples calls this

    def enter(self):
        self.load_state(MenuNav)

    def cancel(self):
        # self.load_state(UtilsView)
        pass


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

class TextScroller:
    def __init__(self):

        self.init_sleep = 1.5
        self.line = 0
        self.is_error = False
        self.num_cols = gv.LCD_COLS
        self.delay = 0.2
        self.change_triggered = False
        self.s_first_run = ''
        self.s_all_others = ''
        self.s = ''
        self.is_looping = False
        self.string_loop_thread = threading.Thread(target=self.loop_thread)
        self.string_loop_thread.daemon = True
        self.string_loop_thread.start()

    def set_string(self, string, line=2, delay=0.2, is_error=False):

        self.change_triggered = True
        self.line = line
        self.is_error = is_error
        self.delay = delay
        padding = ' ' * self.num_cols
        self.s_first_run = string + padding  # First string fills the screen
        self.s_all_others = padding + self.s_first_run  # Second onwards comes in from the right
        self.s = self.s_first_run
        self.is_looping = True

    def stop(self):
        self.change_triggered = True
        self.is_looping = False

    def loop_thread(self):
        while True:
            if self.is_looping:
                for i in range(len(self.s) - self.num_cols + 1):
                    if self.change_triggered:
                        self.change_triggered = False
                        break
                    framebuffer = self.s[i:i + self.num_cols]
                    gv.displayer.disp_change(framebuffer, line=self.line, timeout=0, is_error=self.is_error)
                    if i == 0:
                        time.sleep(self.init_sleep)
                    else:
                        time.sleep(self.delay)
            else:
                time.sleep(0.05)


# ______________________________________________________________________________

function_to_map = None
function_nice_name = None


class MenuNav(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        self.menu_pointer = self.menu_coords[-1]
        gv.displayer.menu_mode = gv.displayer.DISP_MENU_MODE
        self.display()
        # title = self.get_menu_path_str().upper().center(gv.LCD_COLS, ' ')
        # gv.displayer.disp_change(changed_var=title, line=1, timeout=0)
        # gv.displayer.disp_change(changed_var='-' * 20, line=2, timeout=0)
        # gv.displayer.disp_change(changed_var='', line=3, timeout=0)
        # gv.displayer.disp_change(changed_var='', line=4, timeout=0)

    def display(self):

        menu_dict_item = self.get_menu().get(self.menu_pointer)
        title = menu_dict_item.get('name').center(gv.LCD_COLS, ' ').upper()

        gv.displayer.disp_change(title, line=1, timeout=0)

        if menu_dict_item.has_key('desc'):

            desc = menu_dict_item.get('desc')

            if len(desc) > gv.LCD_COLS:  # make it scroll
                Navigator.text_scroller.set_string(string=desc)
            else:
                Navigator.text_scroller.stop()
                gv.displayer.disp_change(changed_var=desc.center(gv.LCD_COLS, ' '), line=2, timeout=0)
        else:
            Navigator.text_scroller.stop()
            gv.displayer.disp_change(changed_var='', line=2, timeout=0)

        gv.displayer.disp_change(changed_var='', line=3, timeout=0)
        gv.displayer.disp_change(changed_var='', line=4, timeout=0)

    def kill_thread(self):
        global do_string_loop
        do_string_loop = False

    def left(self):
        self.kill_thread()
        if self.menu_pointer > 0:
            self.menu_pointer -= 1
            self.menu_coords[-1] = self.menu_pointer
            self.display()

    def right(self):
        self.kill_thread()
        if self.menu_pointer < len(self.get_menu()) - 1:
            self.menu_pointer += 1
            self.menu_coords[-1] = self.menu_pointer
            self.display()

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
        self.text_scroller.stop()
        self.next_state = next_state
        self.preset = gv.preset
        self.display()

    def display(self):

        line_2 = '[%s] %s' % (str(self.preset + 1), str(gv.SETLIST_LIST[gv.samples_indices[self.preset]]))

        gv.displayer.disp_change('SELECT SONG'.center(gv.LCD_COLS, ' '), line=1)
        gv.displayer.disp_change(line_2.ljust(gv.LCD_COLS, ' '), line=2)

    # next song
    def right(self):
        if (self.preset < len(gv.SETLIST_LIST) - 1):
            self.preset += 1
            self.display()

    # previous song
    def left(self):
        if (self.preset > 0):
            self.preset -= 1
            self.display()

    def enter(self):
        self.load_state(self.next_state, self.preset)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class MoveSong(Navigator):
    def __init__(self, preset):
        self.text_scroller.stop()
        self.prev_state = SelectSong
        self.setlist_list = gv.SETLIST_LIST[:]
        self.samples_indices = gv.samples_indices[:]
        self.orig_samples_indices = gv.samples_indices[:]
        self.starting_preset = preset
        self.preset = preset
        self.display()

    def display(self):
        line_1 = 'MOVING FROM [%d]' % (self.starting_preset + 1)
        line_2 = '[%s] %s' % (str(self.preset + 1), str(gv.SETLIST_LIST[gv.samples_indices[self.starting_preset]]))

        gv.displayer.disp_change(line_1.ljust(gv.LCD_COLS, ' '), line=1)
        gv.displayer.disp_change(line_2.ljust(gv.LCD_COLS, ' '), line=2)

    # Move song up the setlist
    # TODO: move to setlist.py class
    def left(self):
        if (self.preset > 0):
            self.setlist_list[self.preset], \
            self.setlist_list[self.preset - 1] = self.setlist_list[self.preset - 1], self.setlist_list[self.preset]

            self.samples_indices[self.preset], \
            self.samples_indices[self.preset - 1] = \
                self.samples_indices[self.preset - 1], self.samples_indices[self.preset]

            self.preset -= 1
        self.display()

    # Move song down the setlist
    def right(self):
        if (self.preset < len(self.setlist_list) - 1):
            self.setlist_list[self.preset], \
            self.setlist_list[self.preset + 1] = \
                self.setlist_list[self.preset + 1], self.setlist_list[self.preset]

            self.samples_indices[self.preset], \
            self.samples_indices[self.preset + 1] = \
                self.samples_indices[self.preset + 1], self.samples_indices[self.preset]

            self.preset += 1
        self.display()

    def enter(self):
        # Stay on the same preset/sample-set as before the setlist rearrangement
        if self.starting_preset == gv.preset:
            gv.preset = self.preset
        elif self.preset == gv.preset:
            if self.starting_preset > self.preset:
                gv.preset += 1
            elif self.starting_preset < self.preset:
                gv.preset -= 1
        gv.ls.all_presets_loaded = False
        gv.samples_indices = self.samples_indices
        gv.setlist.write_setlist(self.setlist_list)
        gv.ls.load_samples()
        self.cancel()

    def cancel(self):
        Navigator.state = self.prev_state(MoveSong)


# ______________________________________________________________________________

class SetlistRemoveMissing(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        gv.displayer.disp_change('REMOVE'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change('MISSING SONGS?'.center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def enter(self):
        gv.setlist.remove_missing_setlist_songs()

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
        self.text_scroller.stop()
        self.prev_state = eval(self.menu_position[self.menu_coords[-1]]['fn'][0])
        self.setlist_list = open(gv.SETLIST_FILE_PATH).read().splitlines()
        gv.displayer.disp_change('Are you sure? [Y/N]'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change('WARNING: will crash if we delete all songs'.center(gv.LCD_COLS, ' '), line=2)

    def enter(self):
        print gv.SETLIST_LIST
        del gv.SETLIST_LIST[gv.samples_indices[gv.preset]]
        gv.setlist.write_setlist(self.setlist_list)
        # TODO: need to reset sample_indices and update SETLIST_LIST
        if gv.preset > 0:
            gv.preset -= 1

        self.load_state(self.prev_state)

    def cancel(self):
        self.load_state(self.prev_state)


# ______________________________________________________________________________



class MidiLearn(Navigator):
    def __init__(self, function_to_map, function_nice_name):
        self.text_scroller.stop()
        self.midimaps = gv.midimaps
        gv.learningMode = True
        self.function_to_map = function_to_map
        self.function_nice_name = function_nice_name
        self.learnedMidiMessage = None
        self.learnedMidiDevice = None
        gv.displayer.disp_change('LEARNING'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change('Select a control'.center(gv.LCD_COLS, ' '), line=2)

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
        self.text_scroller.stop()
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
        self.text_scroller.stop()
        self.MAX_POLYPHONY = gv.MAX_POLYPHONY
        self.display()

    def display(self):
        gv.displayer.disp_change('MAX POLYPHONY'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change((str(self.MAX_POLYPHONY) + ' [1-128]').center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        self.MAX_POLYPHONY = max(self.MAX_POLYPHONY - 1, 1)
        self.display()

    def right(self):
        self.MAX_POLYPHONY = min(self.MAX_POLYPHONY + 1, 128)
        self.display()

    def enter(self):
        gv.cp.update_config('SAMPLERBOX CONFIG', 'MAX_POLYPHONY', str(self.MAX_POLYPHONY))
        gv.MAX_POLYPHONY = self.MAX_POLYPHONY
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class MidiChannelConfig(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        print '-= MIDI Channel !IMPORTANT: All MIDI ports are open with rtmidi2 =-'
        self.MIDI_CHANNEL = gv.MIDI_CHANNEL
        self.display()

    def display(self):
        gv.displayer.disp_change('MIDI CHANNEL'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change((str(self.MIDI_CHANNEL) + ' [1-16](0=ALL)').center(gv.LCD_COLS, ' '), line=2,
                                 timeout=0)

    def left(self):
        self.MIDI_CHANNEL = max(self.MIDI_CHANNEL - 1, 0)
        self.display()

    def right(self):
        self.MIDI_CHANNEL = min(self.MIDI_CHANNEL + 1, 16)
        self.display()

    def enter(self):
        gv.cp.update_config('SAMPLERBOX CONFIG', 'MIDI_CHANNEL', str(self.MIDI_CHANNEL))
        gv.MIDI_CHANNEL = self.MIDI_CHANNEL
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class ChannelsConfig(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        self.CHANNELS = gv.CHANNELS
        self.options = [1, 2, 4, 6, 8]
        self.i = 1
        for x in self.options:
            if x == self.CHANNELS:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        gv.displayer.disp_change('AUDIO CHANNELS'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        gv.displayer.disp_change(('[' + str(self.CHANNELS) + ']' + ' (1,2,4,6,8)').center(gv.LCD_COLS, ' '), line=2,
                                 timeout=0)

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
        gv.cp.update_config('SAMPLERBOX CONFIG', 'CHANNELS', str(self.CHANNELS))
        gv.CHANNELS = self.CHANNELS
        gv.sound.close_stream()
        gv.sound.start_sounddevice_stream()
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class BufferSizeConfig(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        self.BUFFERSIZE = gv.BUFFERSIZE
        self.options = [16, 32, 64, 128, 256, 512, 1024, 2048]
        self.i = 3
        for x in self.options:
            if x == self.BUFFERSIZE:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        gv.displayer.disp_change('BUFFER SIZE'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
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
        gv.cp.update_config('SAMPLERBOX CONFIG', 'BUFFERSIZE', str(self.BUFFERSIZE))
        gv.BUFFERSIZE = self.BUFFERSIZE
        gv.sound.close_stream()
        gv.sound.start_sounddevice_stream()
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

class SampleRateConfig(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        self.SAMPLERATE = gv.SAMPLERATE
        self.options = [44100, 48000, 96000]
        self.i = 0
        for x in self.options:
            if x == self.SAMPLERATE:
                self.i = self.options.index(x)
        self.display()

    def display(self):
        gv.displayer.disp_change('SAMPLE RATE'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
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
        gv.cp.update_config('SAMPLERBOX CONFIG', 'SAMPLERATE', str(self.SAMPLERATE))
        gv.SAMPLERATE = self.SAMPLERATE
        gv.sound.close_stream()
        gv.sound.start_sounddevice_stream()
        self.load_state(MenuNav)

    def cancel(self):
        self.load_state(MenuNav)


# ______________________________________________________________________________

# TODO: Find best way to modify ALSA mixer volume

# class MasterVolumeConfig(Navigator):
#     def __init__(self):
#         self.text_scroller.stop()
#         self.display()
#
#     def display(self):
#         gv.displayer.disp_change('MASTER VOLUME'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
#         gv.displayer.disp_change(str(gv.global_volume).center(gv.LCD_COLS, ' '), line=2, timeout=0)
#
#     def left(self):
#         gv.global_volume = max(gv.global_volume - 4, 0)
#         gv.ac.master_volume.setvolume(gv.global_volume * 1.27)
#         self.display()
#
#     def right(self):
#         gv.global_volume = min(gv.global_volume + 4, 100)
#         gv.ac.master_volume.setvolume(gv.global_volume * 1.27)
#         self.display()
#
#     def enter(self):
#         cs.update_config('SAMPLERBOX CONFIG', 'GLOBAL_VOLUME', str(gv.global_volume))
#         self.load_state(MenuNav)
#
#     def cancel(self):
#         self.enter()


# _____________________________________________________________________________

from modules import definitionparser


def set_global_from_keyword(keyword, value):
    keyword = keyword.strip('%%')
    if isinstance(value, str): value = value.title()
    for gvar, k in definitionparser.keywords_to_try:
        if k == keyword:
            # if 'release' in keyword: value = value * 10000
            print '\r>>>> Setting global from keyword. %s: %s' % (keyword, str(value))  # debug
            exec (gvar + '=value')  # set the global variable


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class EditDefinition(Navigator):
    def __init__(self, preset):
        self.text_scroller.stop()
        self.in_a_mode = False
        self.mode = 0
        self.selected_keyword = None
        self.allowed_values = None
        self.i = 0
        self.selected_keyword_value = None
        self.prev_state = SelectSong
        self.song_name = gv.SETLIST_LIST[gv.samples_indices[preset]]
        self.dp = definitionparser.DefinitionParser(self.song_name)
        self.keywords_dict = self.dp.keywords_dict
        self.keywords_defaults_dict = self.dp.keywords_defaults_dict
        self.display()

    def display(self):
        if not self.in_a_mode:
            keyword_str = self.keywords_dict[self.mode].items()[0][0].strip('%%').title()
            gv.displayer.disp_change(self.song_name.center(gv.LCD_COLS, ' '), line=1, timeout=0)
            gv.displayer.disp_change(keyword_str.center(gv.LCD_COLS, ' '), line=2, timeout=0)
        elif self.in_a_mode:
            keyword_str = self.keywords_dict[self.mode].items()[0][0].strip('%%').title()
            if isinstance(self.allowed_values, list):
                value_str = str(self.allowed_values[self.i])
            elif isinstance(self.allowed_values, tuple):
                num = self.i
                if 'Release' in keyword_str:
                    num = float(num) / 58.82  # convert to seconds
                    value_str = '%ss' % str(num)[:4]  # display like: 1.23s
                else:
                    value_str = str(num)
            gv.displayer.disp_change(keyword_str.center(gv.LCD_COLS, ' '), line=1, timeout=0)
            gv.displayer.disp_change(value_str.center(gv.LCD_COLS, ' '), line=2, timeout=0)

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

            # In a mode -> save to definition.txt
            if isinstance(self.allowed_values, list):
                self.dp.set_new_keyword(self.selected_keyword, str(self.selected_keyword_value))
            elif isinstance(self.allowed_values, tuple):
                self.dp.set_new_keyword(self.selected_keyword, int(self.selected_keyword_value))

            self.dp.compare_existing_patterns()
            self.dp.write_definition_file()
            # Update existing patterns in memory
            self.dp.existing_patterns = self.dp.get_patterns_from_file(self.dp.definitionfname, self.dp.keywords_dict)
            # self.load_state(EditDefinition)

            self.in_a_mode = False

            self.display()

    def cancel(self):
        if not self.in_a_mode:
            Navigator.state = self.prev_state(EditDefinition)  # go back up a menu tier
        elif self.in_a_mode:
            self.enter()  # save even if we have pressed cancel. Not saving requires to revert to initial value.
            # self.in_a_mode = False
            # self.display()


class AudioDevice(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        self.i = 0
        # refresh audio devices. However RPi doesn't hotplug USB devices  TODO: find a way to hotplug audio devices
        gv.sound.all_audio_devices = gv.sound.get_all_audio_devices()
        self.device_name = str(gv.sound.all_audio_devices[self.i].get('name'))
        self.display(False)

    def display(self, changed=False):

        if changed:
            gv.displayer.disp_change('DEVICE CHANGED!'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
            gv.displayer.disp_change(self.device_name.center(gv.LCD_COLS, ' '), line=2, timeout=0)
            time.sleep(2)
            self.display()
        else:
            gv.displayer.disp_change('CHOOSE NEW AUDIO DEVICE'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
            self.text_scroller.set_string(self.device_name.center(gv.LCD_COLS, ' '), line=2)
            gv.displayer.disp_change('', line=3, timeout=0)

    def left(self):
        if self.i > 0:
            self.i -= 1
            self.device_name = str(gv.sound.all_audio_devices[self.i].get('name'))
            self.display(changed=False)

    def right(self):
        if self.i < len(gv.sound.all_audio_devices) - 1:
            self.i += 1
            self.device_name = str(gv.sound.all_audio_devices[self.i].get('name'))
            self.display(changed=False)

    def enter(self):
        gv.cp.update_config('SAMPLERBOX CONFIG', 'AUDIO_DEVICE_NAME', self.device_name)
        gv.AUDIO_DEVICE_ID = -1 # sound.py prioritises searching AUDIO_DEVICE_ID if it is 0 or greater
        gv.sound.set_audio_device(self.device_name)
        self.display(changed=True)

    def cancel(self):
        self.load_state(MenuNav)


class ChordMode(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        self.AVAILABLE_CHORD_SETS = gv.ac.autochorder.AVAILABLE_CHORDS_SETS
        self.display()

    def display(self):
        if gv.ac.autochorder.chord_set_index == 1 or gv.ac.autochorder.chord_set_index == 2:
            first_line = 'Mode [Key:%s]' % gv.NOTES[gv.ac.autochorder.current_key_index].upper()
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
        self.text_scroller.stop()
        self.display()

    def display(self):
        key_name = gv.NOTES[gv.ac.autochorder.current_key_index].upper()
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
        self.text_scroller.stop()
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
        gv.USE_FREEVERB = self.freeverb_state
        gv.cp.update_config('SAMPLERBOX CONFIG', 'USE_FREEVERB', str(self.freeverb_state))
        gv.sound.close_stream()
        gv.sound.start_sounddevice_stream()
        self.cancel()

    def cancel(self):
        self.load_state(MenuNav)


class SetRAMLimit(Navigator):
    def __init__(self):
        self.text_scroller.stop()
        self.ram_limit = gv.RAM_LIMIT_PERCENTAGE
        self.limit_min = gv.cp.configdefaults['RAM_LIMIT_PERCENTAGE']['min']
        self.limit_max = gv.cp.configdefaults['RAM_LIMIT_PERCENTAGE']['max']
        self.display()

    def display(self):
        gv.displayer.disp_change('Set RAM limit'.center(gv.LCD_COLS, ' '), line=1, timeout=0)
        ram_percentage = '%d%%' % self.ram_limit
        gv.displayer.disp_change(ram_percentage.center(gv.LCD_COLS, ' '), line=2, timeout=0)

    def left(self):
        if self.ram_limit > self.limit_min:
            self.ram_limit -= 5
        else:
            self.ram_limit = self.limit_min
        self.display()

    def right(self):
        if self.ram_limit < self.limit_max:
            self.ram_limit += 5
        else:
            self.ram_limit = self.limit_max
        self.display()

    def enter(self):
        gv.cp.update_config('SAMPLERBOX CONFIG', 'RAM_LIMIT_PERCENTAGE', str(self.ram_limit))
        gv.RAM_LIMIT_PERCENTAGE = self.ram_limit
        gv.ls.load_samples() # perhaps we increased the RAM, so go ahead and load more samples now!
        self.cancel()

    def cancel(self):
        self.load_state(MenuNav)
