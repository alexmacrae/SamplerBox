#########################################
# LOAD SAMPLES
#
#########################################

import threading
import os
import re
import sound
import lcd
import numpy
import midicallback
import globalvars as gvars

LoadingThread = None
LoadingInterrupt = False


def LoadSamples():
    global LoadingThread
    global LoadingInterrupt

    if LoadingThread:
        LoadingInterrupt = True
        LoadingThread.join()
        LoadingThread = None

    LoadingInterrupt = False
    LoadingThread = threading.Thread(target=ActuallyLoad)
    LoadingThread.daemon = True
    LoadingThread.start()


def ActuallyLoad():
    global LoadingThread

    gvars.playingsounds = []
    gvars.samples = {}
    # gvars.globalvolume = 10 ** (-6.0/20)  # -12dB default global volume
    gvars.globaltranspose = 0
    gvars.voices = []

    # midicallback.AllNotesOff()
    mode = []
    gvars.sample_mode = gvars.PLAYLIVE
    gvars.gain = 1
    gvars.currvoice = 1
    gvars.pitchnotes = gvars.PITCHRANGE
    gvars.samples = {}
    release = 3  # results in FADEOUTLENGTH=30000, the samplerbox default

    prevbase = gvars.basename  # changed from currbase. Hans, doens't this make more sense?

    setlist_list = open(gvars.SETLIST_FILE_PATH).read().splitlines()
    gvars.basename = setlist_list[gvars.preset]

    if gvars.basename:
        if gvars.basename == prevbase:  # don't waste time reloading a patch
            # print 'Kept preset %s' % basename
            lcd.display("Kept %s" % gvars.basename)
            return
        dirname = os.path.join(gvars.SAMPLES_DIR, gvars.basename)
    if not gvars.basename:
        lcd.display('Preset empty: %s' % gvars.preset)
        return

    lcd.display(str(gvars.preset + 1) + unichr(2) + gvars.basename, 1)

    definitionfname = os.path.join(dirname, "definition.txt")
    file_count = len(os.listdir(dirname))
    file_current = 0

    if os.path.isfile(definitionfname):

        numberOfPatterns = len(list(enumerate(open(definitionfname, 'r'))))

        with open(definitionfname, 'r') as definitionfile:

            for i, pattern in enumerate(definitionfile):
                try:
                    if r'%%gain' in pattern:
                        gvars.gain = abs(float(pattern.split('=')[1].strip()))
                        continue
                    if r'%%transpose' in pattern:
                        gvars.globaltranspose = int(pattern.split('=')[1].strip())
                        continue
                    # We might want to decide which samples go to which voice without editing the filenames
                    # if r'%%voice' in pattern:
                    #     gvars.voices.append(abs(float(pattern.split('=')[1].strip())))
                    #     continue
                    if r'%%release' in pattern:
                        release = abs(int(pattern.split('=')[1].strip()))
                    if r'%%pitchbend' in pattern:
                        gvars.pitchnotes = abs(int(pattern.split('=')[1].strip()))
                        if gvars.pitchnotes > 12:
                            print "Pitchbend of %d limited to 12" % gvars.pitchnotes
                            gvars.pitchnotes = 12
                        continue
                    if r'%%mode' in pattern:
                        mode = pattern.split('=')[1].strip().title()
                        if mode == gvars.PLAYLIVE \
                                or mode == gvars.PLAYBACK \
                                or mode == gvars.PLAYSTOP \
                                or mode == gvars.PLAYLOOP \
                                or mode == gvars.PLAYLO2X:
                            gvars.sample_mode = mode
                        continue
                    if r'%%velmode' in pattern:
                        mode = pattern.split('=')[1].strip().title()
                        if mode == gvars.VELSAMPLE or mode == gvars.VELACCURATE: gvars.velocity_mode = mode
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
                        # print 'Processing ' + fname
                        if LoadingInterrupt:
                            # print 'Loading % s interrupted...' % dirname
                            return
                        percent_loaded = (file_current * (
                            100 / numberOfPatterns)) / file_count  # more accurate loading progress
                        # Visual percentage loading with blocks. Load on last row of LCD
                        lcd.display(unichr(1) * int(percent_loaded * (lcd.LCD_COLS / 100.0) + 1), lcd.LCD_ROWS)
                        file_current += 1
                        if LoadingInterrupt:
                            return
                        m = re.match(pattern, fname)
                        if m:
                            info = m.groupdict()
                            voice = int(info.get('voice', defaultparams['voice']))
                            gvars.voices.append(voice)
                            midinote = int(info.get('midinote', defaultparams['midinote']))
                            velocity = int(info.get('velocity', defaultparams['velocity']))
                            # - Commented out for now; can't be sample-level variables yet 
                            # mode = str(info.get('velocity', defaultparams['mode']))
                            # mode = mode.strip(' \t\n\r')
                            # velmode = str(info.get('velocity', defaultparams['velmode']))
                            # velmode = velmode.strip(' \t\n\r')
                            # release = int(info.get('release', defaultparams['release']))
                            # gain = int(info.get('gain', defaultparams['gain']))
                            # transpose = int(info.get('transpose', defaultparams['transpose']))
                            notename = info.get('notename', defaultparams['notename'])
                            # next statement places note 60 on C3/C4/C5 with the +0/1/2. So now it is C4:
                            if notename:
                                midinote = gvars.NOTES.index(notename[:-1].lower()) + (int(notename[-1]) + 2) * 12
                            gvars.samples[midinote, velocity, voice] = sound.Sound(os.path.join(dirname, fname),
                                                                                   midinote, velocity)
                            # print "sample: %s, note: %d, voice: %d" %(fname, midinote, voice)
                except:
                    print "Error in definition file, skipping line %s." % (i + 1)

    else:
        for midinote in range(0, 127):
            if LoadingInterrupt:
                return
            gvars.voices.append(1)
            file = os.path.join(dirname, "%d.wav" % midinote)
            # print "Trying " + file
            if os.path.isfile(file):
                # print "Processing " + file
                gvars.samples[midinote, 127, 1] = sound.Sound(file, midinote, 127)

            percent_loaded = (file_current * 100) / file_count  # more accurate loading progress
            lcd.display(unichr(1) * int(percent_loaded * (lcd.LCD_COLS / 100) + 1), 4)
            file_current += 1

    initial_keys = set(gvars.samples.keys())

    if len(initial_keys) > 0:
        gvars.voices = list(set(gvars.voices))  # Remove duplicates by converting to a set

        for voice in gvars.voices:
            voice += 1
            for midinote in xrange(128):
                last_velocity = None
                for velocity in xrange(128):
                    if (midinote, velocity, voice) in initial_keys:
                        if not last_velocity:
                            for v in xrange(velocity):
                                gvars.samples[midinote, v, voice] = gvars.samples[midinote, velocity, voice]
                        last_velocity = gvars.samples[midinote, velocity, voice]
                    else:
                        if last_velocity:
                            gvars.samples[midinote, velocity, voice] = last_velocity
            ###################
            # Error: Filling missing notes not buggy
            ###################
            initial_keys = set(gvars.samples.keys())  # we got more keys, but not enough yet
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
                        ######################
                        # print "Note %d will be generated from %d" % (midinote, m)
                        # for velocity in xrange(128):
                        #     gvars.samples[midinote, velocity, voice] = gvars.samples[m, velocity, voice]
                        ######################

        if not (release * 10000) == gvars.FADEOUTLENGTH:
            gvars.FADEOUTLENGTH = release * 10000
            # print 'Fadeoutlength changed to ' + str(gvars.FADEOUTLENGTH)
            gvars.FADEOUT = numpy.linspace(1., 0., gvars.FADEOUTLENGTH)  # by default, float64
            gvars.FADEOUT = numpy.power(gvars.FADEOUT, 6)
            gvars.FADEOUT = numpy.append(gvars.FADEOUT, numpy.zeros(gvars.FADEOUTLENGTH, numpy.float32)).astype(
                numpy.float32)
            # print 'Preset loaded: ' + str(preset)
            # lcd.display("")

    elif len(initial_keys) == 0:
        lcd.display(' Error loading ', 1)
        lcd.display(str(gvars.preset + 1) + unichr(2) + gvars.basename, 2)
    else:
        lcd.display('', 5, customTimeout=0)  # as soon as the sample set is loaded, go straight to play screen
