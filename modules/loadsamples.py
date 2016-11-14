#########################################
# LOAD SAMPLES
#########################################
import os
import re
import threading
import numpy
import globalvars as gv
import displayer
import sound

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

    gv.playingsounds = []
    gv.samples = {}
    # gv.global_volume = 10 ** (-6.0/20)  # -12dB default global volume
    gv.globaltranspose = 0
    gv.voices = []

    # midicallback.AllNotesOff()
    mode = []
    gv.sample_mode = gv.PLAYLIVE
    gv.gain = 1
    gv.currvoice = 1
    gv.pitchnotes = gv.PITCHRANGE
    gv.samples = {}
    release = 3  # results in FADEOUTLENGTH=30000, the samplerbox default

    prevbase = gv.basename  # disp_changed from currbase. Hans, doens't this make more sense?

    if gv.SYSTEM_MODE == 1:
        setlist_list = open(gv.SETLIST_FILE_PATH).read().splitlines()
        gv.basename = setlist_list[gv.preset]
    elif gv.SYSTEM_MODE == 2:
        gv.basename = next((f for f in os.listdir(gv.SAMPLES_DIR) if f.startswith("%d " % gv.preset)),
                           None)  # or next(glob.iglob("blah*"), None)

    if gv.basename:
        if gv.basename == prevbase:  # don't waste time reloading a patch
            # print 'Kept preset %s' % basename
            # hd44780_20x4.display("Kept %s" % gv.basename)
            displayer.disp_change('preset')
            return
        dirname = os.path.join(gv.SAMPLES_DIR, gv.basename)
    if not gv.basename:
        # hd44780_20x4.display('Preset empty: %s' % gv.preset)
        displayer.disp_change('preset')
        return

    displayer.disp_change('preset')

    definitionfname = os.path.join(dirname, "definition.txt")
    file_count = len(os.listdir(dirname))
    file_current = 0

    if os.path.isfile(definitionfname):

        numberOfPatterns = len(list(enumerate(open(definitionfname, 'r'))))

        with open(definitionfname, 'r') as definitionfile:

            for i, pattern in enumerate(definitionfile):
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
                        if mode == gv.VELSAMPLE or mode == gv.VELACCURATE: gv.velocity_mode = mode
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
                        # hd44780_20x4.display(unichr(1) * int(percent_loaded * (hd44780_20x4.LCD_COLS / 100.0) + 1), hd44780_20x4.LCD_ROWS)
                        gv.percent_loaded = percent_loaded

                        displayer.disp_change('loading', timeout=0.5)

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
                                midinote = gv.NOTES.index(notename[:-1].lower()) + (int(notename[-1]) + 2) * 12
                            gv.samples[midinote, velocity, voice] = sound.Sound(os.path.join(dirname, fname),
                                                                                midinote, velocity)
                            # print "sample: %s, note: %d, voice: %d" %(fname, midinote, voice)
                except:
                    print "Error in definition file, skipping line %s." % (i + 1)

    else:
        for midinote in range(0, 127):
            if LoadingInterrupt:
                return
            gv.voices.append(1)
            file = os.path.join(dirname, "%d.wav" % midinote)
            # print "Trying " + file
            if os.path.isfile(file):
                # print "Processing " + file
                gv.samples[midinote, 127, 1] = sound.Sound(file, midinote, 127)

            percent_loaded = (file_current * 100) / file_count  # more accurate loading progress
            # hd44780_20x4.display(unichr(1) * int(percent_loaded * (hd44780_20x4.LCD_COLS / 100) + 1), 4)
            gv.percent_loaded = percent_loaded
            displayer.disp_change('loading')
            file_current += 1

    initial_keys = set(gv.samples.keys())

    if len(initial_keys) > 0:
        gv.voices = list(set(gv.voices))  # Remove duplicates by converting to a set

        for voice in gv.voices:

            for midinote in xrange(128):
                last_velocity = None
                for velocity in xrange(128):
                    if (midinote, velocity, voice) in initial_keys:
                        if not last_velocity:
                            for v in xrange(velocity):
                                gv.samples[midinote, v, voice] = gv.samples[midinote, velocity, voice]
                        last_velocity = gv.samples[midinote, velocity, voice]
                    else:
                        if last_velocity:
                            gv.samples[midinote, velocity, voice] = last_velocity

            initial_keys = set(gv.samples.keys())  # we got more keys, but not enough yet
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
                        gv.samples[midinote, velocity, voice] = gv.samples[m, velocity, voice]

        if not (release * 10000) == gv.FADEOUTLENGTH:
            gv.FADEOUTLENGTH = release * 10000
            # print 'Fadeoutlength disp_changed to ' + str(gv.FADEOUTLENGTH)
            gv.FADEOUT = numpy.linspace(1., 0., gv.FADEOUTLENGTH)  # by default, float64
            gv.FADEOUT = numpy.power(gv.FADEOUT, 6)
            gv.FADEOUT = numpy.append(gv.FADEOUT, numpy.zeros(gv.FADEOUTLENGTH, numpy.float32)).astype(
                numpy.float32)
            # print 'Preset loaded: ' + str(preset)
            # lcd.display("")

    elif len(initial_keys) == 0:
        # hd44780_20x4.display(' Error loading ', 1)
        # hd44780_20x4.display(str(gv.preset + 1) + unichr(2) + gv.basename, 2)
        displayer.disp_change('preset')
    else:
        # hd44780_20x4.display('', 5, timeout_custom=0)  # as soon as the sample set is loaded, go straight to play screen
        displayer.disp_change('')

    # in future we may not want to go to the preset mode as we might also navigating the menu
    displayer.disp_change('preset', timeout=0)
