#########################################
# LOAD SAMPLES
#
#########################################
import threading
import navigator
import os
import re
import sound
import lcd
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


NOTES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
gvars.preset = 0
SampleLoading = False

def ActuallyLoad():

    global SampleLoading, LoadingThread

    setlistList = open(navigator.SETLIST_FILE_PATH).read().splitlines()
    print setlistList
    print '         ' + str(gvars.preset)

    gvars.playingsounds = []
    gvars.samples = {}
    # gvars.globalvolume = 10 ** (-6.0/20)  # -12dB default global volume
    gvars.globaltranspose = 0
    voices = []

    gvars.basename = setlistList[gvars.preset]

    if gvars.basename:
        dirname = os.path.join(gvars.SAMPLES_DIR, gvars.basename)
    if not gvars.basename:
        lcd.display('Preset empty: %s' % gvars.preset)
        return
    lcd.display('load: ' + gvars.basename, 1)

    SampleLoading = True

    definitionfname = os.path.join(dirname, "definition.txt")
    FileCnt = len(os.listdir(dirname))
    FileCntCur = 0

    if os.path.isfile(definitionfname):

        numberOfPatterns = len(list(enumerate(open(definitionfname, 'r'))))

        with open(definitionfname, 'r') as definitionfile:



            for i, pattern in enumerate(definitionfile):
                try:
                    if r'%%volume' in pattern:  # %%paramaters are global parameters
                        gvars.globalvolume *= 10 ** (float(pattern.split('=')[1].strip()) / 20)
                        continue
                    if r'%%transpose' in pattern:
                        gvars.globaltranspose = int(pattern.split('=')[1].strip())
                        continue
                    defaultparams = {'midinote': '0', 'velocity': '127', 'notename': '', 'voice': '1'}

                    if len(pattern.split(',')) > 1:
                        defaultparams.update(dict([item.split('=') for item in
                                                   pattern.split(',', 1)[1].replace(' ', '').replace('%', '').split(
                                                       ',')]))
                    pattern = pattern.split(',')[0]
                    pattern = re.escape(pattern.strip())
                    pattern = pattern.replace(r"\%midinote", r"(?P<midinote>\d+)") \
                        .replace(r"\%velocity", r"(?P<velocity>\d+)") \
                        .replace(r"\%voice", r"(?P<voice>\d+)") \
                        .replace(r"\%notename", r"(?P<notename>[A-Ga-g]#?[0-9])") \
                        .replace(r"\*", r".*?").strip()  # .*? => non greedy

                    for fname in os.listdir(dirname):


                        PercentLoaded = (FileCntCur * (100 / numberOfPatterns)) / FileCnt # more accurate loading progress
                        #s = str(gvars.preset) + ' ' + gvars.basename + "                  "
                        #lcd.display(s[:16], 1)
                        lcd.display(unichr(1) * int(PercentLoaded*0.16 + 1), 2)
                        FileCntCur += 1
                        if LoadingInterrupt:
                            SampleLoading = False
                            return
                        m = re.match(pattern, fname)
                        if m:
                            info = m.groupdict()
                            voice = int(info.get('voice', defaultparams['voice']))
                            voices.append(voice)
                            midinote = int(info.get('midinote', defaultparams['midinote']))
                            velocity = int(info.get('velocity', defaultparams['velocity']))
                            notename = info.get('notename', defaultparams['notename'])
                            if notename:
                                midinote = NOTES.index(notename[:-1].lower()) + (int(notename[-1]) + 2) * 12
                            gvars.samples[midinote, velocity, voice] = sound.Sound(os.path.join(dirname, fname), midinote, velocity)

                except:
                    print "Error in definition file, skipping line %s." % (i + 1)

    else:
        for midinote in range(0, 127):
            voices = [1]
            if LoadingInterrupt:
                SampleLoading = False
                return
            file = os.path.join(dirname, "%d.wav" % midinote)
            if os.path.isfile(file):
                gvars.samples[midinote, 127, 1] = sound.Sound(file, midinote, 127)

            PercentLoaded = (FileCntCur * 100 ) / FileCnt  # more accurate loading progress
            lcd.display(unichr(1) * int(PercentLoaded * 0.16 + 1), 2)
            FileCntCur += 1

    initial_keys = set(gvars.samples.keys())
    voices = list(set(voices))  # Remove duplicates by converting to a set
    total_voices = len(voices)

    for voice in xrange(total_voices):
        voice += 1
        for midinote in xrange(128):
            lastvelocity = None
            for velocity in xrange(128):
                if (midinote, velocity, voice) not in initial_keys:
                    gvars.samples[midinote, velocity, voice] = lastvelocity
                else:
                    if not lastvelocity:
                        for v in xrange(velocity):
                            gvars.samples[midinote, v, voice] = gvars.samples[midinote, velocity, voice]
                    lastvelocity = gvars.samples[midinote, velocity, voice]
            if not lastvelocity:
                for velocity in xrange(128):
                    try:
                        gvars.samples[midinote, velocity, voice] = gvars.samples[midinote - 1, velocity, voice]
                    except:
                        pass

    if len(initial_keys) == 0:
        lcd.display('Preset empty: ' + str(gvars.preset), 1)
    else:
        lcd.display('Loaded 100%', 1)
    SampleLoading = False
