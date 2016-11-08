#########################################
# LOAD SAMPLES
#
#########################################

import threading
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




#NOTES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
gvars.preset = 0
SampleLoading = False

def ActuallyLoad():

    global SampleLoading, LoadingThread

    setlistList = open(gvars.SETLIST_FILE_PATH).read().splitlines()
    #print setlistList

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
    lcd.display(str(gvars.preset+1) + unichr(2)+ gvars.basename, 1)

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

                    ###    # From Hans' changes
                    # if r'%%volume' in pattern:        # %%parameters are global parameters
                    #    volume = int(pattern.split('=')[1].strip())
                    #    amix.setvolume(volume)
                    #    getvolume()
                    #    continue
                    # if r'%%gain' in pattern:
                    #     gain = float(pattern.split('=')[1].strip())
                    #     continue
                    # if r'%%release' in pattern:
                    #     release = int(pattern.split('=')[1].strip())
                    #     continue
                    # if r'%%mode' in pattern:
                    #     mode = pattern.split('=')[1].strip().title()
                    #     # print 'found mode ' + mode
                    #     if mode == PLAYLIVE or mode == PLAYBACK or mode == PLAYSTOP or mode == PLAYLOOP or mode == PLAYLO2X: sample_mode = mode
                    #     # print 'sample mode = ' + sample_mode
                    #     continue
                    # if r'%%velmode' in pattern:
                    #     mode = pattern.split('=')[1].strip().title()
                    #     if mode == VELSAMPLE or mode == VELACCURATE: velocity_mode = mode
                    #     # print 'velocity mode = ' + velocity_mode
                    #     continue
                    defaultparams = {'midinote': '0', 'velocity': '127', 'notename': '', 'voice': '1', 'mode': 'keyb', 'velmode': 'accurate', 'release': '3', 'gain': '1', 'transpose': '0'}

                    if len(pattern.split(',')) > 1:
                        defaultparams.update(dict([item.split('=') for item in
                                                   pattern.split(',', 1)[1].replace(' ', '').replace('%', '').split(
                                                       ',')]))
                    pattern = pattern.split(',')[0]
                    pattern = re.escape(pattern.strip())
                    pattern = pattern.replace(r"\%midinote", r"(?P<midinote>\d+)") \
                        .replace(r"\%velocity", r"(?P<velocity>\d+)") \
                        .replace(r"\%voice", r"(?P<voice>\d+)") \
                        .replace(r"\%mode", r"(?P<mode>\d+)") \
                        .replace(r"\%velmode", r"(?P<velmode>\d+)") \
                        .replace(r"\%release", r"(?P<release>\d+)") \
                        .replace(r"\%gain", r"(?P<gain>\d+)") \
                        .replace(r"\%transpose", r"(?P<transpose>\d+)") \
                        .replace(r"\%notename", r"(?P<notename>[A-Ga-g]#?[0-9])") \
                        .replace(r"\*", r".*?").strip()  # .*? => non greedy

                    for fname in os.listdir(dirname):

                        PercentLoaded = (FileCntCur * (100 / numberOfPatterns)) / FileCnt # more accurate loading progress
                        #s = str(gvars.preset) + ' ' + gvars.basename + "                  "
                        #lcd.display(s[:16], 1)
                        lcd.display(unichr(1) * int(PercentLoaded * (lcd.LCD_COLS/100.0) + 1), 4)
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
                            mode = str(info.get('velocity', defaultparams['mode']))
                            mode = mode.strip(' \t\n\r')
                            velmode = str(info.get('velocity', defaultparams['velmode']))
                            velmode = velmode.strip(' \t\n\r')
                            release = int(info.get('release', defaultparams['release']))
                            gain = int(info.get('gain', defaultparams['gain']))
                            transpose = int(info.get('transpose', defaultparams['transpose']))
                            notename = info.get('notename', defaultparams['notename'])
                            if notename:
                                midinote = gvars.NOTES.index(notename[:-1].lower()) + (int(notename[-1]) + 2) * 12
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
            lcd.display(unichr(1) * int(PercentLoaded * (lcd.LCD_COLS/100) + 1), 4)
            FileCntCur += 1

    initial_keys = set(gvars.samples.keys())
    voices = list(set(voices))  # Remove duplicates by converting to a set
    gvars.totalVoices = len(voices)

    for voice in xrange(gvars.totalVoices):
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
        lcd.display(' Error loading ', 1)
        lcd.display(str(gvars.preset+1) + unichr(2)+ gvars.basename, 2)
    else:
        lcd.display('', 5, customTimeout=0) # as soon as the sample set is loaded, go straight to play screen
    SampleLoading = False
