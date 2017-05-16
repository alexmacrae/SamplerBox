import time
import os
import glob
import re
import threading
import psutil
import globalvars as gv
import sound
from modules import definitionparser as dp
from sfzparser import SFZParser
import sys
import gc  # garbage collector


class LoadingSamples:
    def __init__(self):

        self.LoadingThread = None
        self.LoadingInterrupt = False
        self.loading_paused = False
        self.preset_current_loading = gv.samples_indices[gv.preset]
        self.all_presets_loaded = False
        self.memory_limit_reached = False
        self.loading_paused = False
        self.midi_detected = False
        self.pause_sleep = 0.1
        self.last_memory_reading = 0
        # gv.setlist.update()

        # Create empty dicts for every sample-set. This is necessary for setlist rearrangement
        for i in xrange(len(gv.SETLIST_LIST)):
            self.init_sampleset_dict(i)

    #################################
    # Init a single sample-set dict #
    #################################

    def init_sampleset_dict(self, i):
        if gv.samples.has_key(i): gv.samples.pop(i)
        gv.samples[i] = {}
        gv.samples[i]['keywords'] = {}
        gv.samples[i]['fillnotes'] = {}
        gv.samples[i]['keywords']['voices'] = {}
        gv.samples[i]['samples_loaded'] = False
        gv.samples[i]['notes_filled'] = False

    ###########################
    # Initiate sample loading #
    ###########################

    def load_preset(self):

        if self.LoadingThread:
            self.LoadingInterrupt = True
            self.LoadingThread.join()
            self.LoadingThread = None

        self.preset_current_loading = gv.samples_indices[gv.preset]
        self.preset_current_selected = gv.samples_indices[gv.preset]  # same as loading. load_samples() will change _loading, but _selected remains

        self.LoadingInterrupt = False
        self.LoadingThread = threading.Thread(target=self.actually_load)
        self.LoadingThread.daemon = True
        self.LoadingThread.start()

    ######################
    # Update LCD display #
    ######################

    def update_display(self, type, timeout=0.0):

        if gv.displayer.menu_mode == 'preset':

            gv.displayer.disp_change(type, timeout=timeout)


    ############################
    # Pause loading script if  #
    # there are sounds playing #
    ############################

    def pause_if_playingsounds_or_midi(self):

        if self.LoadingInterrupt:
            return

        # pause_time = 1 #secs
        # print gv.samples[self.preset_current_loading].get('samples_loaded'),gv.samples[self.preset_current_loading].get('notes_filled')
        if gv.samples[self.preset_current_selected].get('samples_loaded') == True and gv.samples[self.preset_current_selected].get('notes_filled') == True:

            # if gv.playingsounds or self.midi_detected or gv.displayer.menu_mode != gv.displayer.DISP_PRESET_MODE: # menu_mode breaks definition editor. TODO: find better way
            if gv.playingsounds or self.midi_detected:  # are there sounds or midi playing?

                print '####################################'
                print '# Initiate pause on sample loading #'

                self.loading_paused = True

                self.update_display('preset')

                while True:

                    if not gv.playingsounds or self.LoadingInterrupt: # playing sounds or preset changed

                        # time_start = time.time()
                        #
                        # if self.midi_detected:
                        #
                        #     while True:
                        #         if self.LoadingInterrupt:
                        #             self.midi_detected = False
                        #             return
                        #         elif time.time() - time_start > pause_time:
                        #             time.sleep(self.pause_sleep)
                        #             break

                        print '\r\n#----------------------------------#'
                        print '#   No more playingsounds or MIDI  #'
                        print '#         Continue loading         #'
                        print '####################################'
                        self.midi_detected = False
                        self.loading_paused = False
                        self.update_display('preset')
                        time.sleep(self.pause_sleep)
                        return

                    sys.stdout.write('\r[!] LOADING PAUSED: sounds or MIDI is playing')
                    sys.stdout.flush()
                    time.sleep(self.pause_sleep)

            else:
                self.loading_paused = False
                self.update_display('preset')
                return

    #####################
    # Memory management #
    #####################

    def check_memory_usage(self):
        RAM_usage_percentage = psutil.virtual_memory().percent
        self.last_memory_reading = RAM_usage_percentage
        if RAM_usage_percentage > gv.RAM_LIMIT_PERCENTAGE:

            print '     RAM usage = %d%%' % RAM_usage_percentage
            print '     RAM limit = %d%%' % gv.RAM_LIMIT_PERCENTAGE
            print ' x   RAM usage has reached limit (in config.ini)'
            print '     STOP LOADING PRESETS'
            self.memory_limit_reached = True
            return True

        else:

            print '     RAM usage = %d%%' % RAM_usage_percentage
            print '     RAM limit = %d%%' % gv.RAM_LIMIT_PERCENTAGE
            print ' +   RAM usage is OK - can load next preset'
            self.memory_limit_reached = False
            return False

    def kill_preset(self, preset):

        if gv.samples.has_key(preset):
            print 'Killing samples in preset [%d: %s]' % (preset, gv.SETLIST_LIST[preset])  # debug
            self.init_sampleset_dict(preset)
            self.all_presets_loaded = False
            gc.collect()
            return True
        else:
            print 'No samples loaded in previous preset slot - do nothing'  # debug
            return False

    def kill_one_before(self):
        prev_preset = self.get_prev_preset(gv.samples_indices[gv.preset])

        # Kill previous preset (if it exists)
        if gv.samples.has_key(prev_preset):
            print 'Killing samples in previous preset [%d: %s]' % (prev_preset, gv.SETLIST_LIST[prev_preset])  # debug
            self.init_sampleset_dict(prev_preset)
            self.all_presets_loaded = False
            gc.collect()
            return True
        else:
            print 'No samples loaded in previous preset slot - do nothing'  # debug
            return False

    def kill_two_before(self):
        two_preset_prev = self.get_prev_preset(self.get_prev_preset(gv.samples_indices[gv.preset]))
        # Kill previous preset (if it exists)
        if gv.samples.has_key(two_preset_prev):
            print 'Killing two presets previous [%d: %s]' % (two_preset_prev, gv.SETLIST_LIST[two_preset_prev])  # debug
            self.init_sampleset_dict(two_preset_prev)
            self.all_presets_loaded = False
            gc.collect()
            return True
        else:
            print 'No samples loaded in two presets previous - do nothing'  # debug
            return False

    def is_all_presets_loaded(self):
        i = 0
        for s in gv.samples.keys():
            if gv.samples[s].get('samples_loaded') == True and gv.samples[s].get('notes_filled') == True:
                i += 1
        if len(gv.setlist.song_folders_list) == i:
            print '///// All presets are now loaded into memory /////'
            self.all_presets_loaded = True
        else:
            print '///// Not all presets have been loaded into memory /////'
            self.all_presets_loaded = False

    ####################################
    # Next and previous preset getters #
    ####################################

    def get_next_preset(self, current_preset):
        if current_preset < len(gv.samples_indices) - 1:
            preset_next_to_load = gv.samples_indices[current_preset + 1]
        else:
            preset_next_to_load = 0
        return preset_next_to_load

    def get_prev_preset(self, current_preset):
        if current_preset > 0:
            preset_prev_to_load = gv.samples_indices[current_preset - 1]
        else:
            preset_prev_to_load = gv.samples_indices[-1]
        return preset_prev_to_load

    ##########################################
    # Set globals from dict from definitions #
    ##########################################

    def set_globals_from_keywords(self):

        gv.voices = gv.samples[gv.samples_indices[gv.preset]]['keywords']['voices']

        if gv.samples[gv.samples_indices[gv.preset]].has_key('keywords'):
            preset_keywords_dict = gv.samples[gv.samples_indices[gv.preset]]['keywords']

            for global_var, keyword in dp.keywords_to_try:
                if preset_keywords_dict.has_key(keyword):
                    value = preset_keywords_dict.get(keyword)
                    print '>>>> Global keyword found in definition -> %%%%%s=%s' % (keyword, str(value))  # debug
                    exec (global_var + '=value')  # set the global variable

    def reset_global_defaults(self):

        # gv.global_volume = 10 ** (-6.0/20)  # -12dB default global volume
        gv.basename = gv.SETLIST_LIST[gv.preset]
        gv.globaltranspose = dp.get_default('%%transpose')
        gv.sample_mode = dp.get_default('%%mode')
        gv.velocity_mode = dp.get_default('%%velmode')
        gv.PRERELEASE = dp.get_default('%%release')
        gv.gain = dp.get_default('%%gain')
        gv.PITCHBEND = dp.get_default('%%pitchbend')
        gv.currvoice = 1
        #### prevbase = gv.basename  # disp_changed from currbase


    def load_next_preset(self):

        self.update_display('preset')

        if len(gv.SETLIST_LIST) > 1:

            if self.preset_current_loading == gv.samples_indices[gv.preset]:

                self.preset_next_to_load = self.get_next_preset(gv.preset)

            else:

                self.preset_next_to_load = self.get_next_preset(self.preset_current_loading)

                if self.preset_next_to_load == gv.preset:
                    return True

            self.preset_current_loading = self.preset_next_to_load
            # time.sleep(0.05)  # allow a tiny pause before loading next preset for LCD

            # if gv.displayer.menu_mode == 'preset':
            #     gv.displayer.disp_change('preset') # force display to update

            self.actually_load()  # load next preset


    ###################################


    def load_samples(self):

        # Reset defaults
        current_basename = gv.SETLIST_LIST[self.preset_current_loading]
        voices_this_preset = []
        channel = gv.MIDI_CHANNEL
        gv.pitchnotes = gv.PITCHRANGE_DEFAULT  # fallback to the samplerbox default
        gv.PRERELEASE = gv.BOXRELEASE  # fallback to the samplerbox default for the preset release time

        dirname = os.path.join(gv.SAMPLES_DIR, current_basename)

        definitionfname = os.path.join(dirname, "definition.txt")

        sfzfname = glob.glob(os.path.join(dirname, '*.sfz'))
        sfzfname = sfzfname[0].replace('\\', '/') if sfzfname else ''

        # file_count = float(len(os.listdir(dirname)))
        file_count = len(glob.glob1(dirname, "*.wav"))
        file_current = 1.0

        gv.samples[self.preset_current_loading]['keywords']['fillnotes'] = 'Y'  # set fillnotes global default because it's needed in this iteration later

        if os.path.isfile(definitionfname):

            print 'START LOADING: [%d] %s' % (self.preset_current_loading, current_basename)  # debug

            definition_list = list(enumerate(open(definitionfname, 'r')))
            wav_definitions_list = [x for x in definition_list if "%%" not in x[1]]  # remove list entries containing %%
            wav_definitions_list = [x for x in wav_definitions_list if "\n" != x[1]]  # remove blank lines

            with open(definitionfname, 'r') as definitionfile:

                if self.preset_current_loading != self.preset_current_selected:
                    self.pause_if_playingsounds_or_midi()
                    if self.LoadingInterrupt:
                        return

                ############################
                # Global-level definitions #
                ############################

                for i, pattern in enumerate(definitionfile):  # iterate every line


                    if self.preset_current_loading != self.preset_current_selected:
                        self.pause_if_playingsounds_or_midi()
                        if self.LoadingInterrupt:
                            return

                    if r'%%' not in pattern:
                        continue

                    try:

                        # Add any found keywords to preset's samples dict without applying to globals

                        if r'%%gain' in pattern:
                            gv.samples[self.preset_current_loading]['keywords']['gain'] = abs(float(pattern.split('=')[1].strip()))
                            continue
                        if r'%%transpose' in pattern:
                            gv.samples[self.preset_current_loading]['keywords']['transpose'] = int(pattern.split('=')[1].strip())
                            continue
                        if r'%%release' in pattern:
                            release = (int(pattern.split('=')[1].strip()))
                            if release > 127:
                                print "Release of %d limited to %d" % (release, 127)
                                release = 127
                            gv.samples[self.preset_current_loading]['keywords']['release'] = release
                            continue
                        if r'%%fillnotes' in pattern:
                            m = pattern.split('=')[1].strip().title()
                            if m == 'Y' or m == 'N':
                                fillnotes = m
                                gv.samples[self.preset_current_loading]['keywords']['fillnotes'] = fillnotes
                                continue
                        if r'%%pitchbend' in pattern:
                            pitchnotes = abs(int(pattern.split('=')[1].strip()))
                            pitchnotes = sorted([0, pitchnotes, 24])[1]  # limit value to within the range 0-24
                            gv.samples[self.preset_current_loading]['keywords']['pitchbend'] = pitchnotes
                            continue
                        if r'%%mode' in pattern:
                            mode = pattern.split('=')[1].strip().title()
                            if mode == gv.PLAYLIVE \
                                    or mode == gv.PLAYONCE \
                                    or mode == gv.PLAYSTOP \
                                    or mode == gv.PLAYLOOP \
                                    or mode == gv.PLAYLO2X:
                                gv.samples[self.preset_current_loading]['keywords']['mode'] = mode
                                continue
                        if r'%%velmode' in pattern:
                            velmode = pattern.split('=')[1].strip().title()
                            if velmode == gv.VELSAMPLE or velmode == gv.VELACCURATE:
                                gv.samples[self.preset_current_loading]['keywords']['velmode'] = velmode
                                continue

                                # End of global definitions

                    except Exception as e:
                        if pattern != '':
                            print "Error in definition file, skipping line %s." % (i + 1)
                            print "Line %d contents: %s" % (i + 1, pattern)
                            # exc_info = sys.exc_info()
                            # print exc_info
                            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)

                # Set global variables from definitions or defaults

                if self.preset_current_loading == self.preset_current_selected:
                    self.set_globals_from_keywords()
                    print '################################'

                if self.preset_current_loading != self.preset_current_selected:
                    self.pause_if_playingsounds_or_midi()
                    if self.LoadingInterrupt:
                        return

            with open(definitionfname, 'r') as definitionfile:

                if self.preset_current_loading != self.preset_current_selected:
                    self.pause_if_playingsounds_or_midi()
                    if self.LoadingInterrupt:
                        return

                ############################
                # Sample-level definitions #
                ############################

                file_list = []  # used for accurate loading percentage feedback

                for i, pattern in enumerate(definitionfile):  # iterate every line (again)

                    if self.preset_current_loading != self.preset_current_selected:
                        self.pause_if_playingsounds_or_midi()
                        if self.LoadingInterrupt:
                            return

                    try:

                        defaultparams = {'midinote': '0', 'velocity': '127', 'notename': '',
                                         'voice': '1', 'seq': '1', 'channel': gv.MIDI_CHANNEL, 'release': '128',
                                         'fillnote': 'G', 'mode': 'Keyb', 'mutegroup': '0'}

                        if len(pattern.split(',')) > 1:
                            defaultparams.update(dict([item.split('=') for item in pattern.split(',', 1)[1].replace(' ', '').replace('%', '').split(',')]))
                        pattern = pattern.split(',')[0]
                        pattern = re.escape(pattern.strip())
                        pattern = pattern \
                            .replace(r"\%midinote", r"(?P<midinote>\d+)") \
                            .replace(r"\%channel", r"(?P<channel>\d+)") \
                            .replace(r"\%velocity", r"(?P<velocity>\d+)") \
                            .replace(r"\%voice", r"(?P<voice>\d+)") \
                            .replace(r"\%release", r"(?P<release>[a-zA-Z0-9_])") \
                            .replace(r"\%fillnote", r"(?P<fillnote>[YNGyng])") \
                            .replace(r"\%mode", r"(?P<mode>\w+)") \
                            .replace(r"\%seq", r"(?P<seq>\d+)") \
                            .replace(r"\%notename", r"(?P<notename>[A-Ga-g]#?[0-9])") \
                            .replace(r"\%mutegroup", r"(?P<mutegroup>\d+)") \
                            .replace(r"\*", r".*?").strip()  # .*? => non greedy

                        for fname in glob.glob1(dirname, "*.wav"):  # iterate over .wav files in the dir

                            if self.preset_current_loading != self.preset_current_selected:
                                self.pause_if_playingsounds_or_midi()
                                if self.LoadingInterrupt:
                                    return

                            m = re.match(pattern, fname)

                            if m:

                                ############################
                                # DISPLAY LOADING PROGRESS #
                                ############################
                                if self.preset_current_loading == gv.samples_indices[gv.preset]:

                                    if fname not in file_list:
                                        file_list.append(fname)
                                        percent_loaded = (file_current / file_count) * 100.0
                                        file_current += 1
                                        gv.percent_loaded = percent_loaded
                                        # Send percent loaded of sample-set to be displayed
                                        self.update_display('loading', timeout=0.3)

                                ############################

                                info = m.groupdict()
                                voice = int(info.get('voice', defaultparams['voice']))
                                voices_this_preset.append(voice)
                                release = int(info.get('release', defaultparams['release']))
                                fillnote = str(info.get('fillnote', defaultparams['fillnote'])).title().rstrip()
                                midinote = int(info.get('midinote', defaultparams['midinote']))
                                channel = int(info.get('channel', defaultparams['channel']))
                                velocity = int(info.get('velocity', defaultparams['velocity']))
                                seq = int(info.get('seq', defaultparams['seq']))
                                notename = info.get('notename', defaultparams['notename'])
                                mode = info.get('mode', defaultparams['mode']).rstrip()
                                mutegroup = int(info.get('mutegroup', defaultparams['mutegroup']))
                                # next statement places note 60 on C3/C4/C5 with the +0/1/2. So now it is C4:
                                if notename:
                                    midinote = gv.NOTES.index(notename[:-1].lower()) + (int(notename[-1]) + 2) * 12

                                # Ignore loops at the sample level, overriding the global sample_mode
                                mode_prop = None
                                if mode.title() == 'Once' or gv.sample_mode.title() == 'Once':
                                    mode_prop = mode.title()

                                if gv.samples[self.preset_current_loading].has_key((midinote, velocity, voice, channel)):
                                    """
                                    Sample Randomization by David Hilowitz
                                    """
                                    # Find samples marked for randomization (seq).
                                    # Check existing list of sound objects if s.seq == seq
                                    if any(s.seq == seq for s in gv.samples[self.preset_current_loading][midinote, velocity, voice, channel]):
                                        # print 'Sequence:%i, File:%s already loaded' % (seq, fname)
                                        continue
                                    else:
                                        if (midinote, velocity, voice, channel) in gv.samples[self.preset_current_loading]:
                                            gv.samples[self.preset_current_loading][midinote, velocity, voice, channel] \
                                                .append(sound.Sound(os.path.join(dirname, fname), midinote, velocity, seq, channel, release, mode_prop, mutegroup))
                                            print 'Sample randomization: found seq:%i (%s) >> loading' % (seq, fname)
                                else:

                                    gv.samples[self.preset_current_loading][midinote, velocity, voice, channel] = [
                                        sound.Sound(os.path.join(dirname, fname), midinote, velocity, seq, channel, release, mode_prop, mutegroup)]
                                    # gv.fillnotes[midinote, voice] = fillnote
                                    gv.samples[self.preset_current_loading]['fillnotes'][midinote, voice] = fillnote
                                    # print "sample: %s, note: %d, voice: %d, channel: %d" %(fname, midinote, voice, channel)

                    except Exception as e:
                        if pattern != '':
                            print "Error in definition file, skipping line %s." % (i + 1)
                            print "Line %d contents: %s" % (i + 1, pattern)
                            # exc_info = sys.exc_info()
                            # print exc_info
                            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)

        ###############
        # SFZ support #
        ###############

        elif os.path.isfile(sfzfname):

            if self.LoadingInterrupt:
                return

            # SFZParser by SpotlightKid. https://github.com/SpotlightKid/sfzparser
            # LICENCE: https://github.com/SpotlightKid/sfzparser/blob/master/LICENSE
            sfz = SFZParser(sfzfname)

            # Set globals
            release = int((float(sfz.sections[0][1].get('ampeg_release')) * 1000) / 17)
            release = sorted([0, release, 127])[1]  # limit value to within the range 0-127
            gain = float(sfz.sections[0][1].get('volume')) + 1.0
            sustain = int(sfz.sections[0][1].get('ampeg_sustain'))  # unused
            decay = float(sfz.sections[0][1].get('ampeg_decay'))  # unused
            attack = float(sfz.sections[0][1].get('ampeg_attack'))  # unused
            gv.samples[self.preset_current_loading]['keywords']['release'] = release
            gv.samples[self.preset_current_loading]['keywords']['gain'] = gain
            print '>>>> Global release:', release
            print '>>>> Global gain:', gain

            voices_this_preset.append(1)

            file_list = []  # Used for accurate loading percentage feedback

            for section in sfz.sections:

                if self.preset_current_loading != self.preset_current_selected:
                    self.pause_if_playingsounds_or_midi()
                    if self.LoadingInterrupt:
                        return

                if type(section[0]) == unicode:
                    if section[0] == 'region':

                        sample_fname = section[1].get('sample')
                        sample_path = os.path.join(dirname, sample_fname)
                        hivel = int(section[1].get('hivel'))
                        lovel = int(section[1].get('lovel'))  # unused
                        midinote = int(section[1].get('pitch_keycenter'))
                        hikey = int(section[1].get('hikey'))  # unused
                        lokey = int(section[1].get('lokey'))  # unused

                        gv.samples[self.preset_current_loading][midinote, hivel, 1, 1] = [sound.Sound(sample_path, midinote, hivel, 1, 1, release, None, 0)]
                        gv.samples[self.preset_current_loading]['fillnotes'][midinote, 1] = 'Y'

                        ############################
                        # DISPLAY LOADING PROGRESS #
                        ############################
                        if self.preset_current_loading == gv.samples_indices[gv.preset]:

                            if sample_fname not in file_list:
                                file_list.append(sample_fname)
                                percent_loaded = (file_current / file_count) * 100.0
                                file_current += 1
                                gv.percent_loaded = percent_loaded
                                # Send percent loaded of sample-set to be displayed
                                self.update_display('loading', timeout=0.2)

                                ############################

        # If no definition.txt or *.sfz file found in folder, look for numbered files (64.wav, 65.wav etc) or notenamed files (C1.wav, D3.wav etc)
        else:

            for midinote in range(0, 127):

                if self.preset_current_loading != self.preset_current_selected:
                    self.pause_if_playingsounds_or_midi()
                    if self.LoadingInterrupt:
                        return

                voices_this_preset.append(1)

                file_midinote = os.path.join(dirname, "%d.wav" % midinote)

                notename_index = midinote % 12
                octave = str((midinote / 12))
                notename = gv.NOTES[notename_index] + octave
                file_notename = os.path.join(dirname, "%s.wav" % notename)

                if os.path.isfile(file_midinote):
                    # print "Processing " + file_midinote
                    gv.samples[self.preset_current_loading][midinote, 127, 1, channel] = [sound.Sound(file_midinote, midinote, 127, 1, channel, gv.BOXRELEASE, None, 0)]

                elif os.path.isfile(file_notename):
                    # print "Processing " + file_notename
                    gv.samples[self.preset_current_loading][midinote, 127, 1, channel] = [sound.Sound(file_notename, midinote, 127, 1, channel, gv.BOXRELEASE, None, 0)]

                gv.samples[self.preset_current_loading]['fillnotes'][midinote, 1] = 'Y'

                ############################
                # DISPLAY LOADING PROGRESS #
                ############################
                if self.preset_current_loading == gv.samples_indices[gv.preset]:
                    percent_loaded = float((midinote + 1) / 128) * 100.0
                    gv.percent_loaded = percent_loaded
                    # Send percent loaded of sample-set to be displayed
                    self.update_display('loading', timeout=0.2)

                    ############################

            if self.preset_current_loading != gv.samples_indices[gv.preset]:
                time.sleep(0.01)

        # Record number of voices because if preset is loaded into mem, its voices don't get detected again
        # Remove duplicates by converting to a set. ie [1, 1, 1, 2, 2, 1, 4, 3] => [1, 2, 4, 3]
        gv.samples[self.preset_current_loading]['keywords']['voices'] = list(set(voices_this_preset))

        if self.preset_current_loading != self.preset_current_selected:
            self.pause_if_playingsounds_or_midi()
            if self.LoadingInterrupt:
                return

        # All samples loaded - mark as True
        gv.samples[self.preset_current_loading]['samples_loaded'] = True

    ###################################

    def fill_notes(self):

        ################
        # NOTE FILLING #
        ################
        """
        Fill unassigned notes with the closest sample
        """

        initial_keys = set(gv.samples[self.preset_current_loading].keys())

        # NOTE: Only gv.MIDI_CHANNEL notes will be filled across all keys.
        # eg. pad samples on channel 9 will not be filled across all notes in channel 9

        if len(initial_keys) > 0:
            voices = gv.samples[self.preset_current_loading]['keywords']['voices']
            fillnotes_global = gv.samples[self.preset_current_loading]['keywords']['fillnotes']
            fillnotes = gv.samples[self.preset_current_loading]['fillnotes']
            for voice in voices:
                for midinote in xrange(128):
                    last_velocity = None
                    for velocity in xrange(128):
                        # if self.preset_current_loading != self.preset_current_selected:
                        #     self.pause_if_playingsounds_or_midi()
                        #     if self.LoadingInterrupt:
                        #         return
                        if (midinote, velocity, voice, gv.MIDI_CHANNEL) in initial_keys:  # only process default channel
                            if not last_velocity:
                                for v in xrange(velocity):
                                    gv.samples[self.preset_current_loading][midinote, v, voice, gv.MIDI_CHANNEL] = gv.samples[self.preset_current_loading][
                                        midinote, velocity, voice, gv.MIDI_CHANNEL]

                            last_velocity = gv.samples[self.preset_current_loading][midinote, velocity, voice, gv.MIDI_CHANNEL]
                        else:
                            if last_velocity:
                                gv.samples[self.preset_current_loading][midinote, velocity, voice, gv.MIDI_CHANNEL] = last_velocity

                # we got more keys, but not enough yet
                initial_keys = set(gv.samples[self.preset_current_loading].keys())

                last_low = -130  # force lowest unfilled notes to be filled with the next_high
                next_high = None  # next_high not found yet
                for midinote in xrange(128):  # and start filling the missing notes
                    # if self.preset_current_loading != self.preset_current_selected:
                    #     self.pause_if_playingsounds_or_midi()
                    #     if self.LoadingInterrupt:
                    #         return
                    if (midinote, 1, voice, gv.MIDI_CHANNEL) in initial_keys:  # only process default midi channel
                        try:
                            if fillnotes.has_key((midinote, voice)):
                                # can we use this note for filling? Look for: sample-level = Y, or sample-level = D (default) AND global = Y
                                if fillnotes[midinote, voice] == 'Y' or (fillnotes[midinote, voice] == 'G' and fillnotes_global == 'Y'):
                                    next_high = None  # passed next_high
                                    last_low = midinote  # but we got fresh low info
                        except Exception as e:
                            print "fillnotes[%d, %d] doesn't exist." % (midinote, voice)
                            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)
                    else:
                        if not next_high:
                            next_high = 260  # force highest unfilled notes to be filled with the last_low
                            for m in xrange(midinote + 1, 128):
                                if (m, 1, voice, gv.MIDI_CHANNEL) in initial_keys:
                                    # can we use this note for filling? Look for: sample-level = Y, or sample-level = D (default) AND global = Y
                                    if fillnotes[m, voice] == 'Y' or (fillnotes[m, voice] == 'G' and fillnotes_global == 'Y'):
                                        if m < next_high:
                                            next_high = m

                        if (next_high - last_low) > 260:  # did we find a note valid for filling?
                            continue  # no, stop trying
                        if float(midinote) <= 0.5 + (next_high + last_low) / 2:
                            m = last_low
                        else:
                            m = next_high
                        # print "Note %d will be generated from %d" % (midinote, m)
                        for velocity in xrange(128):
                            gv.samples[self.preset_current_loading][midinote, velocity, voice, gv.MIDI_CHANNEL] = gv.samples[self.preset_current_loading][m, velocity, voice, gv.MIDI_CHANNEL]

        elif len(initial_keys) == 0:
            self.update_display('preset')
            pass
        else:
            gv.displayer.disp_change('')  # Force the display to update
            pass

        if self.preset_current_loading != self.preset_current_selected:
            self.pause_if_playingsounds_or_midi()
            if self.LoadingInterrupt:
                return

        # All valid notes have been filled - mark as True
        gv.samples[self.preset_current_loading]['notes_filled'] = True

    ###################################


    ###################
    # The mother load #
    ###################

    def actually_load(self):

        print 'RAM check at START of preset load'
        self.check_memory_usage()

        if self.preset_current_loading == gv.samples_indices[gv.preset]:
            self.reset_global_defaults()

        # Check if all presets are in memory.
        # This is possible if the total size of all sample-sets are smaller that the percentage of
        # RAM allocated to samples (RAM_LIMIT_PERCENTAGE in config.ini)
        if self.all_presets_loaded:
            print '\r\nLOADED NOTHING: all presets have been loaded into memory'
            self.set_globals_from_keywords()
            self.update_display('preset')  # Force the display to update
            return  # all is loaded, no need to proceed further from here

        if self.preset_current_loading == gv.samples_indices[gv.preset]:

            print '\r\nCurrent preset: [%d: %s]' % (self.preset_current_loading, gv.SETLIST_LIST[self.preset_current_loading])  # debug

            if self.memory_limit_reached == True:
                if self.kill_two_before() == False:  # Free up RAM - kill 2 presets previous (if exists)
                    if self.kill_one_before() == False:  # Free up RAM - kill 1 preset previous (if exists)
                        pass
                self.reset_global_defaults()

        if self.preset_current_loading != self.preset_current_selected:
            self.pause_if_playingsounds_or_midi()
            if self.LoadingInterrupt:
                return

        if gv.samples.has_key(self.preset_current_loading):
            # If key exists, preset is fully or partially loaded
            pass
        else:
            # Preset has never been loaded, or has been unloaded at some point. Initialize its dict and load samples.
            self.init_sampleset_dict([self.preset_current_loading])

        print '\r\nPreset [%d: %s]' % (self.preset_current_loading, gv.SETLIST_LIST[self.preset_current_loading])

        # Samples are loaded and notes are filled: apply definition rules
        if gv.samples[self.preset_current_loading]['samples_loaded'] == True and gv.samples[self.preset_current_loading]['notes_filled'] == True:

            print ' +   Samples are loaded\r\n +   Notes are filled'
            pass

        # Samples are loaded, but notes are not filled: load samples, fill notes, apply definition rules
        elif gv.samples[self.preset_current_loading]['samples_loaded'] == True and gv.samples[self.preset_current_loading]['notes_filled'] == False:

            self.fill_notes()

            print ' +   Samples are loaded\r\n x   Notes are not filled > filling'
            pass

        # Nothing is loaded or filled: load samples, fill notes, apply definition rules
        elif gv.samples[self.preset_current_loading]['samples_loaded'] == False:

            self.load_samples()

            self.fill_notes()

            print ' x   Samples are not loaded > loading\r\n x   Notes are not filled > filling'
            self.update_display('preset')  # Force the display to update
            pass


        print 'END LOADING: [%d] %s' % (self.preset_current_loading, gv.SETLIST_LIST[self.preset_current_loading])  # preset number, folder name

        self.is_all_presets_loaded() # determine whether all presets have been loaded

        if self.preset_current_loading == gv.samples_indices[gv.preset]:
            self.set_globals_from_keywords()

        self.update_display('preset')  # Force the display to update

        print 'RAM check at END of preset load'
        self.check_memory_usage() # check memory again to see if we can load the next preset

        if self.memory_limit_reached == False:
            self.load_next_preset()
        else:
            self.update_display('preset')
