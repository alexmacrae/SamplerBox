#########################################
# LOAD SAMPLES
#########################################
import os
import re
import threading
import numpy
import globalvars as gv
import sound
import time
import psutil

LoadingThread = None
LoadingInterrupt = False

setlist_list = open(gv.SETLIST_FILE_PATH).read().splitlines()

preset_current_is_loaded = False
preset_change_triggered = False
preset_current_loading = gv.preset


RAM_usage_limit = 75 # Percentage of RAM we should allow samples to be loaded into before killing

#####################
# Initiate sample loading
#####################

def LoadSamples():
    global LoadingThread, LoadingInterrupt, preset_current_is_loaded, preset_current_loading, preset_change_triggered

    preset_current_is_loaded = False
    preset_current_loading = gv.preset
    preset_change_triggered = True

    if LoadingThread:
        LoadingInterrupt = True
        LoadingThread.join()
        LoadingThread = None

    LoadingInterrupt = False
    LoadingThread = threading.Thread(target=ActuallyLoad)
    LoadingThread.daemon = True
    LoadingThread.start()

#####################
#
#####################

def pause_if_playingsounds():
    if preset_current_is_loaded:
        if len(gv.playingsounds) > 0:
            print '########\n-- Initiate pause on sample loading --'
            for i in xrange(999999):
                print '(in pause loop)'
                if len(gv.playingsounds) == 0 or preset_change_triggered:
                    print 'No more playingsounds (or new preset triggered)\nContinue loading\n########'
                    return
                time.sleep(0.02)
        else:
            # print '++ FAST sample loading ++'
            return

#####################
# Memory management
#####################

def is_memory_too_high():
    RAM_usage_percentage = psutil.virtual_memory().percent
    if RAM_usage_percentage > RAM_usage_limit:
        return True, RAM_usage_percentage
    else:
        return False, RAM_usage_percentage

def free_up_memory():

    print '########\nRAM usage too high (%dpercent) so let\'s kill something >:)' % is_memory_too_high()[1] # debug
    prev_preset = get_prev_preset(gv.preset)

    # Kill previous preset (if it exists)
    if gv.samples.has_key(prev_preset):
        print 'Killing samples in previous preset [%d: %s]' % (prev_preset, setlist_list[prev_preset-1]) # debug
        gv.samples.pop(prev_preset)
    else:
        print 'No samples loaded in previous preset slot - do nothing' # debug
    print '########' # debug


def kill_two_before():
    print '########'
    two_preset_prev = get_prev_preset(get_prev_preset(gv.preset))
    # Kill previous preset (if it exists)
    if gv.samples.has_key(two_preset_prev):
        print 'Killing two presets previous [%d: %s]' % (two_preset_prev, setlist_list[two_preset_prev - 1])  # debug
        gv.samples.pop(two_preset_prev)
    else:
        print 'No samples loaded in two presets previous - do nothing'  # debug
    print '########'  # debug

#####################
#
#####################

def get_next_preset(current_preset):
    if current_preset < len(gv.SONG_FOLDERS_LIST) - 1:
        preset_next_to_load = current_preset + 1
    else:
        preset_next_to_load = 0
    return preset_next_to_load

def get_prev_preset(current_preset):
    if current_preset > 0:
        preset_prev_to_load = current_preset - 1
    else:
        preset_prev_to_load = len(gv.SONG_FOLDERS_LIST) - 1
    return preset_prev_to_load

#####################
#
#####################

def ActuallyLoad():
    global LoadingThread, preset_current_is_loaded, preset_current_loading, preset_change_triggered

    preset_focus_is_loaded = False

    if preset_current_loading == gv.preset:
        print '\nCurrent preset: [%d: %s]' % (preset_current_loading, setlist_list[preset_current_loading]) # debug
        print 'Keys loaded before:\n',gv.samples.keys() # debug
        kill_two_before()
        print 'Keys loaded after:\n',gv.samples.keys() # debug
        preset_current_is_loaded = False
        preset_change_triggered = False

        if is_memory_too_high()[0]:
            free_up_memory()
            print gv.samples.keys()

    pause_if_playingsounds()

    if gv.samples.has_key(preset_current_loading):
        if gv.samples[preset_current_loading].has_key('loaded'):
            # Preset has been fully loaded into memory so no need to load again!
            print '[%d: %s] has already been loaded. Skipping.' % (preset_current_loading, setlist_list[preset_current_loading])
            preset_focus_is_loaded = True
            #return
        else:
            # Preset seems to have been partially loaded at some point. Stop all playing sounds to avoid pops.
            gv.playingsounds = []  # clear/stop all currently playing samples
    else:
        # Preset has never been loaded. Init its dict and stop all playing sounds.
        gv.samples[preset_current_loading] = {}
        gv.playingsounds = []

    # gv.global_volume = 10 ** (-6.0/20)  # -12dB default global volume
    gv.globaltranspose = 0
    gv.voices = []
    gv.sample_mode = gv.PLAYLIVE
    gv.velocity_mode = gv.VELOCITY_MODE_DEFAULT
    gv.gain = 1
    gv.currvoice = 1
    gv.pitchnotes = gv.PITCHRANGE
    release = 3  # results in FADEOUTLENGTH=30000, the samplerbox default

    # prevbase = gv.basename  # disp_changed from currbase

    gv.basename = setlist_list[gv.preset]
    current_basename = gv.basename

    if gv.SYSTEM_MODE == 1:
        current_basename = setlist_list[preset_current_loading]
    elif gv.SYSTEM_MODE == 2:
        current_basename = next((f for f in os.listdir(gv.SAMPLES_DIR) if f.startswith("%d " % preset_current_loading)),
                           None)  # or next(glob.iglob("blah*"), None)

    # if gv.basename:
    #     if gv.basename == prevbase:  # don't waste time reloading a patch
    #         # print 'Kept preset %s' % basename
    #         # hd44780_20x4.display("Kept %s" % gv.basename)
    #         gv.displayer.disp_change('preset')
    #         return
    #     dirname = os.path.join(gv.SAMPLES_DIR, gv.basename)
    # if not gv.basename:
    #     gv.displayer.disp_change('preset')
    #     return

    dirname = os.path.join(gv.SAMPLES_DIR, current_basename)

    # gv.displayer.disp_change('preset')

    definitionfname = os.path.join(dirname, "definition.txt")
    file_count = len(os.listdir(dirname))
    file_current = 0

    if os.path.isfile(definitionfname) and preset_focus_is_loaded == False:
        print '---------- LOADING: [%d] %s' % (preset_current_loading, current_basename)  # debug
        numberOfPatterns = len(list(enumerate(open(definitionfname, 'r'))))

        with open(definitionfname, 'r') as definitionfile:

            pause_if_playingsounds()

            for i, pattern in enumerate(definitionfile):
                pause_if_playingsounds()
                try:
                    if r'%%gain' in pattern:
                        gv.gain = abs(float(pattern.split('=')[1].strip()))
                        continue
                    if r'%%transpose' in pattern:
                        gv.globaltranspose = int(pattern.split('=')[1].strip())
                        continue
                    # We might want to decide which samples go to which voice without editing the filenames
                    # if r'%%voice' in pattern:
                    #     gv.voices.append(abs(float(pattern.split('=')[1].strip())))
                    #     continue
                    if r'%%release' in pattern:
                        release = abs(int(pattern.split('=')[1].strip()))
                    if r'%%pitchbend' in pattern:
                        gv.pitchnotes = abs(int(pattern.split('=')[1].strip()))
                        if gv.pitchnotes > 12:
                            print "Pitchbend of %d limited to 12" % gv.pitchnotes
                            gv.pitchnotes = 12
                        continue
                    if r'%%mode' in pattern:
                        mode = pattern.split('=')[1].strip().title()
                        if mode == gv.PLAYLIVE \
                                or mode == gv.PLAYBACK \
                                or mode == gv.PLAYSTOP \
                                or mode == gv.PLAYLOOP \
                                or mode == gv.PLAYLO2X:
                            gv.sample_mode = mode
                        continue
                    if r'%%velmode' in pattern:
                        mode = pattern.split('=')[1].strip().title()
                        if mode == gv.VELSAMPLE or mode == gv.VELACCURATE:
                            gv.velocity_mode = mode
                        continue
                    defaultparams = {'midinote': '0', 'velocity': '127', 'notename': '',
                                     'voice': '1', 'mode': 'keyb', 'velmode': 'accurate', 'release': '3', 'gain': '1',
                                     'transpose': '0'}

                    if len(pattern.split(',')) > 1:
                        defaultparams.update(dict([item.split('=') for item in
                                                   pattern.split(',', 1)[1].replace(' ', '').replace('%', '').split(
                                                       ',')]))
                    pattern = pattern.split(',')[0]
                    pattern = re.escape(pattern.strip())
                    pattern = pattern \
                        .replace(r"\%midinote", r"(?P<midinote>\d+)") \
                        .replace(r"\%velocity", r"(?P<velocity>\d+)") \
                        .replace(r"\%voice", r"(?P<voice>\d+)") \
                        .replace(r"\%%voice", r"(?P<voice>\d+)") \
                        .replace(r"\%%mode", r"(?P<mode>\d+)") \
                        .replace(r"\%%velmode", r"(?P<velmode>\d+)") \
                        .replace(r"\%%release", r"(?P<release>\d+)") \
                        .replace(r"\%%gain", r"(?P<gain>\d+)") \
                        .replace(r"\%%transpose", r"(?P<transpose>\d+)") \
                        .replace(r"\%notename", r"(?P<notename>[A-Ga-g]#?[0-9])") \
                        .replace(r"\*", r".*?").strip()  # .*? => non greedy

                    for fname in os.listdir(dirname):
                        pause_if_playingsounds()
                        # print 'Processing ' + fname
                        if LoadingInterrupt:
                            # print 'Loading % s interrupted...' % dirname
                            return
                        percent_loaded = (file_current * (
                            100 / numberOfPatterns)) / file_count  # more accurate loading progress
                        # Visual percentage loading with blocks. Load on last row of LCD
                        # hd44780_20x4.display(unichr(1) * int(percent_loaded * (hd44780_20x4.LCD_COLS / 100.0) + 1), hd44780_20x4.LCD_ROWS)

                        if preset_current_loading == gv.preset:
                            gv.percent_loaded = percent_loaded
                            gv.displayer.disp_change('loading', timeout=0.5)

                        file_current += 1
                        if LoadingInterrupt:
                            return
                        m = re.match(pattern, fname)
                        if m:
                            info = m.groupdict()
                            voice = int(info.get('voice', defaultparams['voice']))
                            gv.voices.append(voice)
                            midinote = int(info.get('midinote', defaultparams['midinote']))
                            velocity = int(info.get('velocity', defaultparams['velocity']))

                            notename = info.get('notename', defaultparams['notename'])
                            # next statement places note 60 on C3/C4/C5 with the +0/1/2. So now it is C4:
                            if notename:
                                midinote = gv.NOTES.index(notename[:-1].lower()) + (int(notename[-1]) + 2) * 12

                            if gv.samples[preset_current_loading].has_key((midinote, velocity, voice)):
                                print 'sample already loaded!'
                            else:
                                gv.samples[preset_current_loading][midinote, velocity, voice] = sound.Sound(
                                    os.path.join(dirname, fname),
                                    midinote, velocity)
                                # print "sample: %s, note: %d, voice: %d" %(fname, midinote, voice)
                except:
                    print "Error in definition file, skipping line %s." % (i + 1)

    else:
        for midinote in range(0, 127):
            pause_if_playingsounds()
            if LoadingInterrupt:
                return
            gv.voices.append(1)
            file = os.path.join(dirname, "%d.wav" % midinote)
            # print "Trying " + file
            if os.path.isfile(file):
                # print "Processing " + file
                gv.samples[preset_current_loading][midinote, 127, 1] = sound.Sound(file, midinote, 127)

            percent_loaded = (file_current * 100) / file_count  # more accurate loading progress
            # hd44780_20x4.display(unichr(1) * int(percent_loaded * (hd44780_20x4.LCD_COLS / 100) + 1), 4)
            gv.percent_loaded = percent_loaded
            gv.displayer.disp_change('loading')
            file_current += 1

    initial_keys = set(gv.samples[preset_current_loading].keys())

    if len(initial_keys) > 0:
        gv.voices = list(set(gv.voices))  # Remove duplicates by converting to a set

        for voice in gv.voices:
            for midinote in xrange(128):
                last_velocity = None
                for velocity in xrange(128):
                    if (midinote, velocity, voice) in initial_keys:
                        if not last_velocity:
                            for v in xrange(velocity):
                                pause_if_playingsounds()
                                gv.samples[preset_current_loading][midinote, v, voice] = gv.samples[preset_current_loading][
                                    midinote, velocity, voice]
                        last_velocity = gv.samples[preset_current_loading][midinote, velocity, voice]
                    else:
                        if last_velocity:
                            gv.samples[preset_current_loading][midinote, velocity, voice] = last_velocity

            initial_keys = set(gv.samples[preset_current_loading].keys())  # we got more keys, but not enough yet
            last_low = -130  # force lowest unfilled notes to be filled with the next_high
            next_high = None  # next_high not found yet
            for midinote in xrange(128):  # and start filling the missing notes
                if (midinote, 1, voice) in initial_keys:
                    next_high = None  # passed next_high
                    last_low = midinote  # but we got fresh low info
                else:
                    if not next_high:
                        next_high = 260  # force highest unfilled notes to be filled with the last_low
                        for m in xrange(midinote + 1, 128):
                            if (m, 1, voice) in initial_keys:
                                if m < next_high: next_high = m
                    if midinote <= 0.5 + (next_high + last_low) / 2:
                        m = last_low
                    else:
                        m = next_high
                    # print "Note %d will be generated from %d" % (midinote, m)
                    for velocity in xrange(128):
                        pause_if_playingsounds()
                        gv.samples[preset_current_loading][midinote, velocity, voice] = gv.samples[preset_current_loading][
                            m, velocity, voice]

        if not (release * 10000) == gv.FADEOUTLENGTH:
            gv.FADEOUTLENGTH = release * 10000
            # print 'Fadeoutlength disp_changed to ' + str(gv.FADEOUTLENGTH)
            gv.FADEOUT = numpy.linspace(1., 0., gv.FADEOUTLENGTH)  # by default, float64
            gv.FADEOUT = numpy.power(gv.FADEOUT, 6)
            gv.FADEOUT = numpy.append(gv.FADEOUT, numpy.zeros(gv.FADEOUTLENGTH, numpy.float32)).astype(
                numpy.float32)
            # print 'Preset loaded: ' + str(preset)
            # lcd.display("")





        print '++++++++++ LOADED: [%d] %s' % (preset_current_loading, current_basename)  # debug
        gv.samples[preset_current_loading]['loaded'] = True  # flag this preset's dict item as loaded

        if is_memory_too_high()[0] == False:

            if preset_current_loading == gv.preset:
                gv.displayer.disp_change('preset', timeout=0)
                preset_next_to_load = get_next_preset(gv.preset)
                preset_current_is_loaded = True
            else:
                preset_next_to_load = get_next_preset(preset_current_loading)
                if preset_next_to_load == gv.preset: return

            print '++ Memory usage is ok (%dpercent) \n++ Load next preset' % is_memory_too_high()[1]  # debug
            preset_current_loading = preset_next_to_load
            ActuallyLoad()  # load next preset

        else:
            print '-- Memory usage is high (%dpercent) \n-- Stop loading other presets' % is_memory_too_high()[
                1]  # debug
            return





    elif len(initial_keys) == 0:
        gv.displayer.disp_change('preset')
        pass
    else:
        gv.displayer.disp_change('')
        pass


