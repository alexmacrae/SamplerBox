import os
import re
import threading
import time
import numpy
import psutil
import globalvars as gv
import sound
from modules import definitionparser as dp


class LoadingSamples:
    def __init__(self):

        self.LoadingThread = None
        self.LoadingInterrupt = False
        self.preset_current_is_loaded = False
        self.preset_current_loading = gv.samples_indices[gv.preset]
        self.preset_change_triggered = False
        self.all_presets_loaded = False

        # gv.setlist.update()

        # Create empty dicts for every sample-set. This is necessary for setlist rearrangement
        for i in xrange(len(gv.SETLIST_LIST)):
            self.init_sampleset_dict(i)

    #################################
    # Init a single sample-set dict #
    #################################

    def init_sampleset_dict(self, i):
        gv.samples[i] = {}
        gv.samples[i]['keywords'] = {}

    ###########################
    # Initiate sample loading #
    ###########################

    def LoadSamples(self):

        self.preset_current_is_loaded = False
        self.preset_current_loading = gv.samples_indices[gv.preset]
        self.preset_change_triggered = True

        if self.LoadingThread:
            self.LoadingInterrupt = True
            self.LoadingThread.join()
            self.LoadingThread = None

        self.LoadingInterrupt = False
        self.LoadingThread = threading.Thread(target=self.ActuallyLoad)
        self.LoadingThread.daemon = True
        self.LoadingThread.start()

    ############################
    # Pause loading script if  #
    # there are sounds playing #
    ############################

    def pause_if_playingsounds(self):
        if self.LoadingInterrupt:
            return

        if self.preset_current_is_loaded and self.preset_current_loading != gv.samples_indices[gv.preset]:
            if gv.playingsounds:
                print '########\n-- Initiate pause on sample loading --'
                for i in xrange(999999):
                    if not gv.playingsounds or self.preset_change_triggered:
                        print 'No more playingsounds (or new preset triggered)\nContinue loading\n########'
                        self.preset_change_triggered = False
                        return
                    print '// loading paused //'
                    time.sleep(0.02)
            else:
                # print '++ Keep loading ++'
                return

    #####################
    # Memory management #
    #####################

    def is_memory_too_high(self):
        RAM_usage_percentage = psutil.virtual_memory().percent
        if RAM_usage_percentage > gv.RAM_LIMIT_PERCENTAGE:
            return True, RAM_usage_percentage
        else:
            return False, RAM_usage_percentage

    def kill_one_before(self):
        prev_preset = self.get_prev_preset(gv.samples_indices[gv.preset])

        # Kill previous preset (if it exists)
        if gv.samples.has_key(prev_preset):
            print 'Killing samples in previous preset [%d: %s]' % (prev_preset, gv.SETLIST_LIST[prev_preset])  # debug
            self.init_sampleset_dict(prev_preset)
            self.all_presets_loaded = False
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
            return True
        else:
            print 'No samples loaded in two presets previous - do nothing'  # debug
            return False

    def is_all_presets_loaded(self):
        i = 0
        for s in gv.samples.keys():
            if gv.samples[s].has_key('loaded'):
                i += 1
        if len(gv.SONG_FOLDERS_LIST) == i:
            print '///// All presets are now loaded into memory /////'
            self.all_presets_loaded = True
        else:
            print '///// Not all presets have been loaded into memory /////'

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
        if gv.samples[gv.samples_indices[gv.preset]].has_key('keywords'):
            preset_keywords_dict = gv.samples[gv.samples_indices[gv.preset]]['keywords']

            for global_var, keyword in dp.keywords_to_try:
                if preset_keywords_dict.has_key(keyword):
                    value = preset_keywords_dict.get(keyword)
                    print '>>>>>>>Keyword found. %s: %s' % (keyword, str(value))  # debug
                    exec (global_var + '=value')  # set the global variable

    def reset_global_defaults(self):
        # gv.global_volume = 10 ** (-6.0/20)  # -12dB default global volume
        gv.basename = gv.SETLIST_LIST[self.preset_current_loading]
        keywords_defaults = dp.keywords_defaults_dict
        gv.voices = []
        gv.globaltranspose = keywords_defaults['%%transpose']
        gv.sample_mode = keywords_defaults['%%mode'].title()
        gv.velocity_mode = keywords_defaults['%%velmode'].title()
        gv.PRERELEASE = keywords_defaults['%%release']
        gv.gain = keywords_defaults['%%gain']
        gv.PITCHBEND = keywords_defaults['%%pitchbend']
        gv.currvoice = 1
        # prevbase = gv.basename  # disp_changed from currbase

    def set_global_fadeout(self):
        # if not (gv.FADEOUTLENGTH) == gv.FADEOUTLENGTH_DEFAULT:
        #     # print 'Fadeoutlength disp_changed to ' + str(gv.FADEOUTLENGTH)
        #     gv.FADEOUT = numpy.linspace(1., 0., gv.FADEOUTLENGTH)  # by default, float64
        #     gv.FADEOUT = numpy.power(gv.FADEOUT, 6)
        #     gv.FADEOUT = numpy.append(gv.FADEOUT, numpy.zeros(gv.FADEOUTLENGTH, numpy.float32)).astype(
        #         numpy.float32)
            # print 'Preset loaded: ' + str(preset)

        pass # Temporary ban on fadeouts until we can figure what the hell is going on

    ###################
    # The mother load #
    ###################

    def ActuallyLoad(self):



        self.reset_global_defaults()
        # Check if all presets are in memory.
        # This is possible if the total size of all sample-sets are smaller that the percentage of
        # RAM allocated to samples (RAM_LIMIT_PERCENTAGE in config.ini)
        if self.all_presets_loaded:
            print 'LOADED NOTHING: all samples have been loaded into memory'
            self.set_globals_from_keywords()
            self.set_global_fadeout()
            return

        preset_focus_is_loaded = False

        if self.preset_current_loading == gv.samples_indices[gv.preset]:

            print '\nCurrent preset: [%d: %s]' % (
            self.preset_current_loading, gv.SETLIST_LIST[self.preset_current_loading])  # debug

            self.preset_current_is_loaded = False
            self.preset_change_triggered = False

            if self.is_memory_too_high()[0] == True:
                if self.kill_two_before() == False: # Kill 2 presets previous (if exists)
                    if self.kill_one_before() == False: # Kill 1 preset previous (if exists)
                        pass
                self.reset_global_defaults()

        self.pause_if_playingsounds()

        if gv.samples.has_key(self.preset_current_loading):  # If key exists, preset has started to load at some point
            if gv.samples[self.preset_current_loading].has_key('loaded'):  # If 'loaded' key exists, preset is fully loaded
                print '[%d: %s] has already been loaded. Skipping.' % (
                    self.preset_current_loading, gv.SETLIST_LIST[self.preset_current_loading])
                preset_focus_is_loaded = True
            else:
                # Preset seems to have been partially loaded at some point.
                # Stop all playing sounds to avoid pops and finish loading.
                # gv.playingsounds = []  # clear/stop all currently playing samples
                pass
        else:
            # Preset has never been loaded. Initialize its dict and load samples.
            self.init_sampleset_dict([self.preset_current_loading])
            # gv.playingsounds = [] # clear/stop all currently playing samples


        # Reset defaults
        current_basename = gv.SETLIST_LIST[self.preset_current_loading]
        voices_local = []
        channel = gv.MIDI_CHANNEL
        gv.pitchnotes = gv.PITCHRANGE_DEFAULT  # fallback to the samplerbox default
        gv.PRERELEASE = gv.BOXRELEASE  # fallback to the samplerbox default for the preset release time

        dirname = os.path.join(gv.SAMPLES_DIR, current_basename)

        definitionfname = os.path.join(dirname, "definition.txt")
        file_count = len(os.listdir(dirname))
        file_current = 0


        if preset_focus_is_loaded == False:

            if os.path.isfile(definitionfname):

                print '---------- LOADING: [%d] %s' % (self.preset_current_loading, current_basename)  # debug

                definition_list = list(enumerate(open(definitionfname, 'r')))
                wav_definitions_list = [x for x in definition_list if
                                        "%%" not in x[1]]  # remove list entries containing %%

                with open(definitionfname, 'r') as definitionfile:

                    self.pause_if_playingsounds()

                    for i, pattern in enumerate(definitionfile):
                        self.pause_if_playingsounds()
                        try:

                            ##########################
                            # Global-level definitions
                            ##########################

                            # Add any found keywords to preset's samples dict without applying to globals

                            if r'%%gain' in pattern:
                                gv.samples[self.preset_current_loading]['keywords']['gain'] = abs(
                                    float(pattern.split('=')[1].strip()))
                                continue
                            if r'%%transpose' in pattern:
                                gv.samples[self.preset_current_loading]['keywords']['transpose'] = int(
                                    pattern.split('=')[1].strip())
                                continue
                            if r'%%release' in pattern:
                                release = (int(pattern.split('=')[1].strip()))
                                if release > 127:
                                    print "Release of %d limited to %d" % (release, 127)
                                    release = 127
                                gv.samples[self.preset_current_loading]['keywords']['release'] = release
                                continue
                            if r'%%fillnote' in pattern:
                                m = pattern.split('=')[1].strip().title()
                                if m == 'Y' or m == 'N':
                                    gv.fillnote = m
                                continue
                            if r'%%pitchbend' in pattern:
                                pitchnotes = abs(int(pattern.split('=')[1].strip()))
                                if pitchnotes > 12:
                                    print "Pitchbend of %d limited to 12 (higher values produce inaccurate pitching)" \
                                          % pitchnotes
                                    pitchnotes = 12
                                pitchnotes *= 2 # actually it is 12 up and 12 down
                                gv.samples[self.preset_current_loading]['keywords']['pitchbend'] = pitchnotes
                                continue
                            if r'%%mode' in pattern:
                                mode = pattern.split('=')[1].strip().title()
                                if mode == gv.PLAYLIVE \
                                        or mode == gv.PLAYBACK \
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

                            ##########################
                            # Sample-level definitions
                            ##########################

                            defaultparams = {'midinote': '0', 'velocity': '127', 'notename': '',
                                             'voice': '1', 'seq': 1, 'channel':gv.MIDI_CHANNEL, 'release': '128', 'fillnote':'Y'}

                            if len(pattern.split(',')) > 1:
                                defaultparams.update(dict([item.split('=') for item in
                                                           pattern.split(',', 1)[1].replace(' ', '').replace('%',
                                                                                                             '').split(
                                                               ',')]))
                            pattern = pattern.split(',')[0]
                            pattern = re.escape(pattern.strip())
                            pattern = pattern \
                                .replace(r"\%midinote", r"(?P<midinote>\d+)") \
                                .replace(r"\%channel", r"(?P<channel>\d+)") \
                                .replace(r"\%velocity", r"(?P<velocity>\d+)") \
                                .replace(r"\%voice", r"(?P<voice>\d+)") \
                                .replace(r"\%release", r"(?P<release>\d+)") \
                                .replace(r"\%fillnote", r"(?P<fillnote>[YNyn]") \
                                .replace(r"\%seq", r"(?P<seq>\d+)") \
                                .replace(r"\%notename", r"(?P<notename>[A-Ga-g]#?[0-9])") \
                                .replace(r"\*", r".*?").strip()  # .*? => non greedy

                            for fname in os.listdir(dirname):
                                self.pause_if_playingsounds()
                                # print 'Processing ' + fname
                                if self.LoadingInterrupt:
                                    # print 'Loading % s interrupted...' % dirname
                                    return
                                percent_loaded = (file_current * (100 / len(wav_definitions_list))) / file_count
                                # Send percent loaded of sample-set to be displayed
                                if self.preset_current_loading == gv.samples_indices[gv.preset]:
                                    gv.percent_loaded = percent_loaded
                                    gv.displayer.disp_change('loading', timeout=0.5)

                                file_current += 1
                                if self.LoadingInterrupt:
                                    return
                                m = re.match(pattern, fname)
                                if m:
                                    info = m.groupdict()
                                    voice = int(info.get('voice', defaultparams['voice']))
                                    voices_local.append(voice)
                                    release = int(info.get('release', defaultparams['release']))
                                    voicefillnote = str(info.get('fillnote', defaultparams['fillnote'])).title().rstrip()
                                    if self.preset_current_loading == gv.samples_indices[
                                        gv.preset]: gv.voices = voices_local
                                    midinote = int(info.get('midinote', defaultparams['midinote']))
                                    channel = int(info.get('channel', defaultparams['channel']))
                                    velocity = int(info.get('velocity', defaultparams['velocity']))
                                    seq = int(info.get('seq', defaultparams['seq']))
                                    notename = info.get('notename', defaultparams['notename'])
                                    # next statement places note 60 on C3/C4/C5 with the +0/1/2. So now it is C4:
                                    if notename:
                                        midinote = gv.NOTES.index(notename[:-1].lower()) + (int(notename[-1]) + 2) * 12
                                    if gv.samples[self.preset_current_loading].has_key((midinote, velocity, voice, channel)):
                                        # Find samples marked for randomization (seq).
                                        # Check existing list of sound objects if s.seq == seq
                                        if any(s.seq == seq for s in
                                               gv.samples[self.preset_current_loading][midinote, velocity, voice, channel]):
                                            print 'Sequence:%i, File:%s already loaded' % (seq, fname)
                                            break
                                        else:
                                            if (midinote, velocity, voice, channel) in gv.samples[self.preset_current_loading]:
                                                gv.samples[self.preset_current_loading][
                                                    midinote, velocity, voice, channel].append(sound.Sound(
                                                    os.path.join(dirname, fname), midinote, velocity, seq, channel, release))
                                                print 'Sample randomization: found seq:%i (%s) >> loading' % (
                                                seq, fname)
                                    else:

                                        gv.samples[self.preset_current_loading][midinote, velocity, voice, channel] = [
                                            sound.Sound(
                                                os.path.join(dirname, fname), midinote, velocity, seq, channel, release)]

                                        gv.fillnotes[midinote, voice] = voicefillnote
                                        # print "sample: %s, note: %d, voice: %d, channel: %d" %(fname, midinote, voice, channel)
                        except:
                            print "Error in definition file, skipping line %s." % (i + 1)

            # If no definition.txt file found in folder, look for numbered files (eg 64.wav, 65.wav etc)
            else:

                for midinote in range(0, 127):
                    self.pause_if_playingsounds()
                    if self.LoadingInterrupt:
                        return
                    voices_local.append(1)
                    if self.preset_current_loading == gv.samples_indices[gv.preset]: gv.voices = voices_local

                    file_ = os.path.join(dirname, "%d.wav" % midinote)
                    # print "Trying " + file_
                    if os.path.isfile(file_):
                        # print "Processing " + file_
                        gv.samples[self.preset_current_loading][midinote, 127, 1, channel] = sound.Sound(file_, midinote, 127, channel, gv.BOXRELEASE)

                    percent_loaded = (file_current * 100) / file_count  # more accurate loading progress
                    gv.percent_loaded = percent_loaded
                    gv.displayer.disp_change('loading')
                    file_current += 1

            initial_keys = set(gv.samples[self.preset_current_loading].keys())

            # NOTE: Only gv.MIDI_CHANNEL notes will be filled across all keys.
            # eg. pad samples on channel 9 will not be filled across all notes in channel 9

            if len(initial_keys) > 0:
                voices_local = list(set(voices_local))  # Remove duplicates by converting to a set
                if self.preset_current_loading == gv.samples_indices[gv.preset]: gv.voices = voices_local

                for voice in voices_local:
                    for midinote in xrange(128):
                        last_velocity = None
                        for velocity in xrange(128):
                            if (midinote, velocity, voice, gv.MIDI_CHANNEL) in initial_keys: # only process default channel
                                if not last_velocity:
                                    for v in xrange(velocity):
                                        self.pause_if_playingsounds()
                                        gv.samples[self.preset_current_loading][midinote, v, voice, gv.MIDI_CHANNEL] = \
                                            gv.samples[self.preset_current_loading][
                                                midinote, velocity, voice, gv.MIDI_CHANNEL]
                                last_velocity = gv.samples[self.preset_current_loading][midinote, velocity, voice, gv.MIDI_CHANNEL]
                            else:
                                if last_velocity:
                                    gv.samples[self.preset_current_loading][midinote, velocity, voice, gv.MIDI_CHANNEL] = last_velocity

                    initial_keys = set(gv.samples[self.preset_current_loading].keys())  # we got more keys, but not enough yet
                    last_low = -130  # force lowest unfilled notes to be filled with the next_high
                    next_high = None  # next_high not found yet
                    for midinote in xrange(128):  # and start filling the missing notes
                        if (midinote, 1, voice, gv.MIDI_CHANNEL) in initial_keys: # only process default midi channel
                            if gv.fillnotes[midinote, voice] == 'Y':  # can we use this note for filling?
                                next_high = None  # passed next_high
                                last_low = midinote  # but we got fresh low info
                        else:
                            if not next_high:
                                next_high = 260  # force highest unfilled notes to be filled with the last_low
                                for m in xrange(midinote + 1, 128):
                                    if (m, 1, voice, gv.MIDI_CHANNEL) in initial_keys:
                                        if gv.fillnotes[m, voice] == 'Y':  # can we use this note for filling?
                                            if m < next_high:
                                                next_high = m
                            if (next_high - last_low) > 260:  # did we find a note valid for filling?
                                break  # no, stop trying
                            if midinote <= 0.5 + (next_high + last_low) / 2:
                                m = last_low
                            else:
                                m = next_high
                            print "Note %d will be generated from %d" % (midinote, m)
                            for velocity in xrange(128):
                                self.pause_if_playingsounds()
                                gv.samples[self.preset_current_loading][midinote, velocity, voice, gv.MIDI_CHANNEL] = \
                                    gv.samples[self.preset_current_loading][m, velocity, voice, gv.MIDI_CHANNEL]
            elif len(initial_keys) == 0:
                gv.displayer.disp_change('preset')
                pass
            else:
                gv.displayer.disp_change('')
                pass

            gv.samples[self.preset_current_loading]['loaded'] = True  # flag this preset's dict item as loaded

        print '++++++++++ LOADED: [%d] %s' % (self.preset_current_loading, current_basename)  # debug

        self.is_all_presets_loaded()
        is_memory_too_high_bool = self.is_memory_too_high()[0]
        is_memory_too_high_percentage = self.is_memory_too_high()[1]

        if self.preset_current_loading == gv.samples_indices[gv.preset]:
            self.set_globals_from_keywords()
            self.set_global_fadeout()
            print '################################'

            self.pause_if_playingsounds()

        if is_memory_too_high_bool == False:

            if self.preset_current_loading == gv.samples_indices[gv.preset]:
                gv.displayer.disp_change('preset', timeout=0)
                self.preset_next_to_load = self.get_next_preset(gv.preset)
                self.preset_current_is_loaded = True
            else:
                self.preset_next_to_load = self.get_next_preset(self.preset_current_loading)
                if self.preset_next_to_load == gv.preset: return

            print '++ RAM usage is ok (%d%%) \n++ Load next preset' % is_memory_too_high_percentage  # debug
            self.preset_current_loading = self.preset_next_to_load
            self.ActuallyLoad()  # load next preset

        else:
            print '-- RAM usage has reach limit (%d%%) \n-- Stop loading other presets' \
                  % is_memory_too_high_percentage  # debug
            return
