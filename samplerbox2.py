#  SamplerBox
#
#  author:    Joseph Ernest (twitter: @JosephErnest, mail: contact@samplerbox.org)
#  url:       http://www.samplerbox.org/
#  license:   Creative Commons ShareAlike 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)
#
#  samplerbox.py: Main file
#

#########################################
# LOCAL
# CONFIG
#########################################

AUDIO_DEVICE_ID = 4                     # change this number to use another soundcard
AUDIO_DEVICE_NAME = "USB Audio DAC"     # If we know the name (or part of the name), match by name instead
#SAMPLES_DIR = "../../media"                       # The root directory containing the sample-sets. Example: "/media/" to look for samples on a USB stick / SD card
SAMPLES_DIR = "media"                       # The root directory containing the sample-sets. Example: "/media/" to look for samples on a USB stick / SD card
USE_SERIALPORT_MIDI = False             # Set to True to enable MIDI IN via SerialPort (e.g. RaspberryPi's GPIO UART pins)
USE_I2C_7SEGMENTDISPLAY = False         # Set to True to use a 7-segment display via I2C
USE_BUTTONS = False                     # Set to True to use momentary buttons (connected to RaspberryPi's GPIO pins) to change preset
MAX_POLYPHONY = 80                      # This can be set higher, but 80 is a safe value
MIDI_CHANNEL = 1
USE_HD44780_16x2_LCD = False             # Set to True to use a HD44780 based 16x2 LCD
USE_FREEVERB = False			# Set to True to enable FreeVerb
USE_TONECONTOL = False			# Set to True to enable Tonecontrol (also remove comments in code
CHANNELS = 2				# set to 2 for normal stereo output, 4 for 4 channel playback
BUFFERSIZE = 128                        # Buffersize: lower means less latency, higher more polyphony and stability
SAMPLERATE = 44100
VERSION1 = " -=SAMPLER-BOX=- "
VERSION2 = "V2.0.1 15-06-2016"


# settings for ToneControl
LOW_EQ_FREQ = 80.0
HIGH_EQ_FREQ = 8000.0
HIGH_EQ = (2 * HIGH_EQ_FREQ) / SAMPLERATE
LOW_EQ = (2 * LOW_EQ_FREQ) / SAMPLERATE

#########################################
# IMPORT
# MODULES
#########################################
import time
import wave
usleep = lambda x: time.sleep(x / 1000000.0)
msleep = lambda x: time.sleep(x / 1000.0)
#import curses
import numpy
import os
import glob
import re
import pyaudio
import sounddevice
import threading
from chunk import Chunk
import struct
#import rtmidi_python as rtmidi
import rtmidi2               # Use rtmidi2 instead. Make sure when installing rtmidi2 to change RPI date: $sudo date -s "Sept 23 18:31 2016". Then installing takes a while

import ctypes # For freeverb
import samplerbox_audio
#from filters import FilterType, Filter, FilterChain
#from utility import byteToPCM, floatToPCM, pcmToFloat, sosfreqz
from collections import OrderedDict
from time import sleep
import psutil



##################################################################################
# link for freeverb C++ lib
##################################################################################
'''
from ctypes import *
freeverb = cdll.LoadLibrary('./freeverb/revmodel.so')

fvsetroomsize = freeverb.setroomsize
fvsetroomsize.argtypes = [c_float]
fvgetroomsize = freeverb.getroomsize
fvgetroomsize.restype = c_float
def setroomsize(val):
  fvsetroomsize(val/127.0)
  display('Roomsize: '+str(val))

fvsetdamp = freeverb.setdamp
fvsetdamp.argtypes = [c_float]
fvgetdamp = freeverb.getdamp
fvgetdamp.restype = c_float
def setdamp(val):
  fvsetdamp(val/127.0)
  display('Damping: '+str(val))

fvsetwet = freeverb.setwet
fvsetwet.argtypes = [c_float]
fvgetwet = freeverb.getwet
fvgetwet.restype = c_float
def setwet(val):
  fvsetwet(val/127.0)
  display('Wet: '+str(val))

fvsetdry = freeverb.setdry
fvsetdry.argtypes = [c_float]
fvgetdry = freeverb.getdry
fvgetdry.restype = c_float
def setdry(val):
  fvsetdry(val/127.0)
  display('Dry: '+str(val))

fvsetwidth = freeverb.setwidth
fvsetwidth.argtypes = [c_float]
fvgetwidth = freeverb.getwidth
fvgetwidth.restype = c_float
def setwidth(val):
  fvsetwidth(val/127.0)
  display('Width: '+str(val))

fvsetmode = freeverb.setmode
fvsetmode.argtypes = [c_float]
fvgetmode = freeverb.getmode
fvgetmode.restype = c_float

c_float_p = ctypes.POINTER(ctypes.c_float)
c_short_p = ctypes.POINTER(ctypes.c_short)
freeverbprocess = freeverb.process
freeverbprocess.argtypes = [c_float_p, c_float_p, c_int]


# no used:
freeverbmix = freeverb.mix
freeverbmix.argtypes = [c_short_p, c_float_p, c_float, c_int]
freeverbmixback = freeverb.mixback
freeverbmixback.argtypes = [c_float_p, c_float_p, c_float, c_short_p, c_float, c_short_p, c_float, c_int]
'''
# END FREEVERB


# backingTrack vars
wf_back = None
wf_click = None
BackingRunning = False

# fade parameter sampler
FADEOUTLENGTH = 30000
FADEOUT = numpy.linspace(1., 0., FADEOUTLENGTH)            # by default, float64
FADEOUT = numpy.power(FADEOUT, 6)
FADEOUT = numpy.append(FADEOUT, numpy.zeros(FADEOUTLENGTH, numpy.float32)).astype(numpy.float32)
SPEED = numpy.power(2, numpy.arange(0.0, 84.0) / 12).astype(numpy.float32)

# administration Sampler
samples = {}
playingnotes = {}
sustainplayingnotes = []
sustain = False
playingsounds = []
globaltranspose = 0
basename = "<Empty>"


VelocitySelectionOffset = 0		#add to selection of samples, not to Velocity Volume

globalvolume = 0 
globalvolumeDB = 0 
backvolume = 0
backvolumeDB = 0
clickvolume = 0
clickvolumeDB = 0


# Volumes from 0-127 0=-20db, 127=0db

# Set Sampler volume
def setSamplerVol(vol):                 # volume in db
    global globalvolume, globalvolumeDB
    vol = (vol * 20.0 / 127.0) - 20
    globalvolumeDB = vol
    globalvolume = 10 ** (vol / 20.0)

# Set Backing volume
def setBackVol(vol):                 # volume in db
    global backvolume, backvolumeDB
    vol = (vol * 20.0 / 127.0) - 20
    backvolumeDB = vol
    backvolume = 10 ** (vol / 20.0)

# Set Click volume
def setClickVol(vol):                 # volume in db
    global clickvolume, clickvolumeDB
    vol = (vol * 20.0 / 127.0) - 20
    clickvolumeDB = vol
    clickvolume = 10 ** (vol / 20.0)

setSamplerVol(50)
setBackVol(50)
setClickVol(50)

#########################################
##  based on 16x2 LCD interface code by Rahul Kar, see:
##  http://www.rpiblog.com/2012/11/interfacing-16x2-lcd-with-raspberry-pi.html
#########################################

class HD44780:

    def __init__(self, pin_rs=7, pin_e=8, pins_db=[25, 24, 23, 18]):  
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)

        self.clear()

    def clear(self):
        """ Blank / Reset LCD """
        
        self.cmd(0x33) # Initialization by instruction
        msleep(5)
        self.cmd(0x33)
        usleep(100)
        self.cmd(0x32) # set to 4-bit mode
        self.cmd(0x28) # Function set: 4-bit mode, 2 lines
        #self.cmd(0x38) # Function set: 8-bit mode, 2 lines
        self.cmd(0x0C) # Display control: Display on, cursor off, cursor blink off
        self.cmd(0x06) # Entry mode set: Cursor moves to the right
        self.cmd(0x01) # Clear Display: Clear & set cursor position to line 1 column 0
        
    def cmd(self, bits, char_mode=False):
        """ Send command to LCD """

        sleep(0.002)
        bits = bin(bits)[2:].zfill(8)

        GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        #for i in range(8):       # use range 4 for 4-bit operation
        for i in range(4):       # use range 4 for 4-bit operation
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)

        GPIO.output(self.pin_e, True)
        usleep(1)      # command needs to be > 450 nsecs to settle
        GPIO.output(self.pin_e, False)
        usleep(100)    # command needs to be > 37 usecs to settle

        """ 4-bit operation start """
        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4, 8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i-4], True)

        GPIO.output(self.pin_e, True)
        usleep(1)      # command needs to be > 450 nsecs to settle
        GPIO.output(self.pin_e, False)
        usleep(100)    # command needs to be > 37 usecs to settle
        """ 4-bit operation end """

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""

        self.cmd(0x02) # Home Display: set cursor position to line 1 column 0
        x = 0
        for char in text:
            if char == '\n':
                self.cmd(0xC0) # next line
                x = 0
            else:
                x += 1
                if x < 17: self.cmd(ord(char), True)


#########################################
# SLIGHT MODIFICATION OF PYTHON'S WAVE MODULE
# TO READ CUE MARKERS & LOOP MARKERS
#########################################

class waveread(wave.Wave_read):

    def initfp(self, file):
        self._convert = None
        self._soundpos = 0
        self._cue = []
        self._loops = []
        self._ieee = False
        self._file = Chunk(file, bigendian=0)
        if self._file.getname() != 'RIFF':
            raise Error, 'file does not start with RIFF id'
        if self._file.read(4) != 'WAVE':
            raise Error, 'not a WAVE file'
        self._fmt_chunk_read = 0
        self._data_chunk = None
        while 1:
            self._data_seek_needed = 1
            try:
                chunk = Chunk(self._file, bigendian=0)
            except EOFError:
                break
            chunkname = chunk.getname()
            if chunkname == 'fmt ':
                self._read_fmt_chunk(chunk)
                self._fmt_chunk_read = 1
            elif chunkname == 'data':
                if not self._fmt_chunk_read:
                    raise Error, 'data chunk before fmt chunk'
                self._data_chunk = chunk
                self._nframes = chunk.chunksize // self._framesize
                self._data_seek_needed = 0
            elif chunkname == 'cue ':
                numcue = struct.unpack('<i', chunk.read(4))[0]
                for i in range(numcue):
                    id, position, datachunkid, chunkstart, blockstart, sampleoffset = struct.unpack('<iiiiii', chunk.read(24))
                    self._cue.append(sampleoffset)
            elif chunkname == 'smpl':
                manuf, prod, sampleperiod, midiunitynote, midipitchfraction, smptefmt, smpteoffs, numsampleloops, samplerdata = struct.unpack(
                                                                                                                                              '<iiiiiiiii', chunk.read(36))
                for i in range(numsampleloops):
                    cuepointid, type, start, end, fraction, playcount = struct.unpack('<iiiiii', chunk.read(24))
                    self._loops.append([start, end])
            chunk.skip()
        if not self._fmt_chunk_read or not self._data_chunk:
            raise Error, 'fmt chunk and/or data chunk missing'

    def getmarkers(self):
        return self._cue

    def getloops(self):
        return self._loops


#########################################
# MIXER CLASSES
#########################################

class PlayingSound:

    def __init__(self, sound, note, vel):
        self.sound = sound
        self.pos = 0
        self.fadeoutpos = 0
        self.isfadeout = False
        self.note = note
        self.vel = vel

    def fadeout(self, i):
        self.isfadeout = True

    def stop(self):
        try:
            playingsounds.remove(self)
        except:
            pass


class Sound:

    def __init__(self, filename, midinote, velocity):
        wf = waveread(filename)
        self.fname = filename
        self.midinote = midinote
        self.velocity = velocity
        if wf.getloops():
            self.loop = wf.getloops()[0][0]
            self.nframes = wf.getloops()[0][1] + 2
        else:
            self.loop = -1
            self.nframes = wf.getnframes()

        self.data = self.frames2array(wf.readframes(self.nframes), wf.getsampwidth(), wf.getnchannels())

        wf.close()

    def play(self, note, vel):
        snd = PlayingSound(self, note, vel)
        print 'fname: ' + self.fname + ' note/vel: ' + str(note) + '/' + str(vel) + ' midinote: ' + str(self.midinote) + ' vel: ' + str(self.velocity)
        playingsounds.append(snd)
        return snd


    def frames2array(self, data, sampwidth, numchan):
        if sampwidth == 2:
            npdata = numpy.fromstring(data, dtype=numpy.int16)
        elif sampwidth == 3:
            npdata = samplerbox_audio.binary24_to_int16(data, len(data) / 3)
        if numchan == 1:
            npdata = numpy.repeat(npdata, 2)
        return npdata




#########################################
# AUDIO CALLBACK
#########################################



def AudioCallback(outdata, frame_count, time_info, status):
    global playingsounds, SampleLoading
    global BackingRunning
    global BackWav, BackIndex, ClickWav, ClickIndex
    global globalvolume, backvolume, clickvolume
    rmlist = []
    #print "sounds: " +str(len(playingsounds)) + " notes: " + str(len(playingnotes)) + " sust: " + str(len(sustainplayingnotes))
    playingsounds = playingsounds[-MAX_POLYPHONY:]
    
    b = samplerbox_audio.mixaudiobuffers(playingsounds, rmlist, frame_count, FADEOUT, FADEOUTLENGTH, SPEED)
    
    for e in rmlist:
        try:
            playingsounds.remove(e)
        except:
            pass

    #b *= globalvolume

    #
    '''
    if USE_FREEVERB:    
        b_temp = b
        freeverbprocess(b_temp.ctypes.data_as(c_float_p), b.ctypes.data_as(c_float_p), frame_count)

    if USE_TONECONTOL
    #	b = numpy.array(chain.filter(bb))
    #	b=bb
    '''
    #

    if CHANNELS == 4: # 4 channel playback   

        #if backingtrack running: add in the audio        
        if BackingRunning:
            BackData = BackWav[BackIndex:BackIndex + 2 * frame_count]
            ClickData = ClickWav[ClickIndex:ClickIndex + 2 * frame_count]
            BackIndex += 2 * frame_count
            ClickIndex += 2 * frame_count
            if len(b) != len(BackData) or len(b) != len(ClickData):
                BackingRunning = False
                BackData = None
                BackIndex = 0
                ClickData = None
                ClickIndex = 0

        if BackingRunning:
            newdata = (backvolume * BackData + b * globalvolume)
            Click = ClickData * clickvolume
        else:
            Click = numpy.zeros(frame_count * 2, dtype=numpy.float32)
            newdata = b * globalvolume

        #putting streams in 4 channel audio by magic in numpy reshape
        a1 = newdata.reshape(frame_count, 2)
        a2 = Click.reshape(frame_count, 2)
        ch4 = numpy.hstack((a1, a2)).reshape(1, frame_count * 4) 

        #mute while loading Sample or BackingTrack, otherwise there could be dirty hick-ups
        if SampleLoading or (BackLoadingPerc > 0 and BackLoadingPerc < 100): 
            ch4 *= 0
        return (ch4.astype(numpy.int16).tostring(), pyaudio.paContinue)
    
    else:  # 2 Channel playback

        #if backingtrack running: add in the audio        
        if BackingRunning:
            BackData = BackWav[BackIndex:BackIndex + 2 * frame_count]
            BackIndex += 2 * frame_count
            if len(b) != len(BackData):
                BackingRunning = False
                BackData = None
                BackIndex = 0

        if BackingRunning:
            newdata = (backvolume * BackData + b * globalvolume)
        else:
            newdata = b * globalvolume

        return (newdata.astype(numpy.int16).tostring(), pyaudio.paContinue)

#########################################
# MIDI CALLBACK
# MIDI DEVICE MAPPINGS FROM FILES
# MIDI LEARN MAPPING
#########################################

total_voices = int()
current_voice = 1

def LoadMidiDeviceMappings (opened_midi_ports):
    print 'Match midi port names with list of midi mapping config files'

def MidiLearn():
    print 'Definition to learn and assign midi controls to SamplerBox functions (write to files)'

def MidiCallback(src, message, time_stamp):
    global current_voice
    global playingnotes, sustain, sustainplayingnotes
    global preset, VelocitySelectionOffset, globalvolume, globalvolumeDB

    messagetype = message[0] >> 4
    if messagetype == 13:
        return
    
    messagechannel = (message[0] & 15) + 1
   
    note = message[1] if len(message) > 1 else None
    midinote = note
    velocity = message[2] if len(message) > 2 else None

    #if (messagetype != 14):
    #    print "ch: " + str(messagechannel) + " type: " + str(messagetype) + " raw: " + str(message) + " SRC: " + str(src)

 
    # special keys from Kurzweil
    if len(message) == 1 and message[0] == 250:  # playbutton Kurzweil
        StartTrack()

    if len(message) == 1 and message[0] == 252: # stopbutton Kurzweil
        StopTrack()

    if messagechannel == MIDI_CHANNEL:
        if messagetype == 9 and velocity == 0:
            messagetype = 8
        elif messagetype == 9:    # Note on
            midinote += globaltranspose

            # scale the selected sample based on velocity, the volume will be kept, this will normally make the sound brighter
            SelectVelocity = (velocity * (127-VelocitySelectionOffset) / 127) + VelocitySelectionOffset

            for n in  sustainplayingnotes:
                if n.note == midinote:
                    n.fadeout(500)
            try:
                playingnotes.setdefault(midinote, []).append(samples[midinote, SelectVelocity, current_voice].play(midinote, velocity))
            except:
                pass

        elif messagetype == 8:  # Note off
            midinote += globaltranspose
            if midinote in playingnotes:
                for n in playingnotes[midinote]:
                    if sustain:
                        sustainplayingnotes.append(n)
                    else:
                        n.fadeout(50)
                playingnotes[midinote] = []

        elif messagetype == 12:  # Program change
            #print 'Program change ' + str(note)
            if preset != note:
                preset = note
                LoadSamples()
  
    # PRESET
        elif (messagetype == 11) and (velocity == 127) and (note != 64):
            numFolders = len(os.walk(SAMPLES_DIR).next()[1])
            print str(message) + " - " + str(numFolders)

            if (note == 71):
                print "NEXT PRESET"
                preset += 1
                current_voice = 1
                if(preset >= numFolders):
                    preset = 0
                LoadSamples()
            if (note == 70):
                print "PREV PRESET"
                preset -= 1
                current_voice = 1
                if(preset < 0):
                    preset = numFolders-1
                LoadSamples()
    
    # VOICE CHANGE
        if (messagetype == 11) and (velocity == 127):
            
            if (note == 64): #careful, this is sustain pedal
                current_voice = 1
            if (note == 65):
                current_voice = 2
            if (note == 66):
                current_voice = 3
            if (note == 67):
                current_voice = 4
            print current_voice
   


    # SUSTAIN PEDAL
        elif ((messagetype == 11) and (note == 64) and (velocity < 64)) or (("microKEY" in src) and (messagetype == 14) and (note == 64 or note == 0) and (velocity >= 28)) and (sustain == True):  # sustain pedal off

            for n in sustainplayingnotes:
                n.fadeout(50)
            sustainplayingnotes = []
            sustain = False
            #print "up"

        elif ((messagetype == 11) and (note == 64) and (velocity >= 64)) or (("microKEY" in src) and (messagetype == 14) and (note == 64 or note == 0) and (velocity <= 25)) and (sustain == False):  # sustain pedal on
            sustain = True
            #print "down"
        
    # GLOBAL VOLUME
        elif (messagetype == 11) and (note == 7) and ("nanoKONTROL" in src):
            globalvolume = (10.0 ** (-12.0 / 20.0)) * (float(velocity) / 127.0)
            print globalvolume

    # STARTBACKING TRACK
    #  elif (message[0]==176) and (message[1]==29) and (message[2]==127):
    #    StartTrack()


 


#########################################
# LOAD SAMPLES
#
#########################################

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

SampleLoading = False

def ActuallyLoad():
    #global total_voices
    global preset
    global samples
    global playingsounds, SampleLoading
    global globalvolume, globaltranspose, basename
    

    playingsounds = []
    samples = {}
    #globalvolume = 10 ** (-6.0/20)  # -12dB default global volume
    globaltranspose = 0
    voices = []

    basename = next((f for f in os.listdir(SAMPLES_DIR) if f.startswith("%d " % preset)), None)      # or next(glob.iglob("blah*"), None)
    if basename:
        dirname = os.path.join(SAMPLES_DIR, basename)
    if not basename:
        display('Preset empty: %s' % preset)
        return
    display('load: ' + basename)
    
    SampleLoading = True

    definitionfname = os.path.join(dirname, "definition.txt")
    if os.path.isfile(definitionfname):
        with open(definitionfname, 'r') as definitionfile:
            for i, pattern in enumerate(definitionfile):
                try:
                    if r'%%volume' in pattern:        # %%paramaters are global parameters
                        globalvolume *= 10 ** (float(pattern.split('=')[1].strip()) / 20)
                        continue
                    if r'%%transpose' in pattern:
                        globaltranspose = int(pattern.split('=')[1].strip())
                        continue
                    defaultparams = {'midinote': '0', 'velocity': '127', 'notename': '', 'voice': '1'}
                    if len(pattern.split(',')) > 1:
                        defaultparams.update(dict([item.split('=') for item in pattern.split(',', 1)[1].replace(' ', '').replace('%', '').split(',')]))
                    pattern = pattern.split(',')[0]
                    pattern = re.escape(pattern.strip())
                    pattern = pattern.replace(r"\%midinote", r"(?P<midinote>\d+)")\
                        .replace(r"\%velocity", r"(?P<velocity>\d+)")\
                        .replace(r"\%voice", r"(?P<voice>\d+)")\
                        .replace(r"\%notename", r"(?P<notename>[A-Ga-g]#?[0-9])")\
                        .replace(r"\*", r".*?").strip()    # .*? => non greedy   
                    FileCnt = len(os.listdir(dirname))
                    FileCntCur = 0
                    PercentLoaded = 0
                    for fname in os.listdir(dirname):
                        s = basename + "                  "
                        PercentLoaded = FileCntCur * 100 / FileCnt
                        #display(s[:12] + "%3d%%" % (PercentLoaded))
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
                            samples[midinote, velocity, voice] = Sound(os.path.join(dirname, fname), midinote, velocity)
                             
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
                samples[midinote, 127, 1] = Sound(file, midinote, 127)

    
    initial_keys = set(samples.keys())
    voices = list(set(voices)) # Remove duplicates by turning into a set
    total_voices = len(voices)
    
    for voice in xrange(total_voices):
        voice += 1
        for midinote in xrange(128):
            lastvelocity = None
            for velocity in xrange(128):
                if (midinote, velocity, voice) not in initial_keys: 
                   samples[midinote, velocity, voice] = lastvelocity
                else:
                    if not lastvelocity:
                        for v in xrange(velocity):
                            samples[midinote, v, voice] = samples[midinote, velocity, voice]
                    lastvelocity = samples[midinote, velocity, voice]
            if not lastvelocity:
                for velocity in xrange(128):
                    try:
                        samples[midinote, velocity, voice] = samples[midinote-1, velocity, voice]
                    except:
                        pass
    
    
    if len(initial_keys) == 0:
        display('Preset empty: ' + str(preset))
    else:
        display('Loaded 100%')
    SampleLoading = False


########################################################################
# EN background playing
########################################################################

BackWav = 0
BackIndex = 0
BackLoaded = False
BackLoadingPerc = 0
Backbasename = 'Backing: Empty'
ClickWav = 0
ClickIndex = 0
BackNr = 0

BackLoadNr = -1


def LoadTrack(nr):
    global BackLoadNr
    print 'load: ' + str(nr)
    BackLoadNr = nr

def LoadTrackProcess():
    
    global BackWav, BackIndex
    global ClickWav, ClickIndex
    global BackingRunning, BackLoadingPerc, BackNr, BackLoaded, BackLen, Backbasename, BackLoadNr

    while True:
        
        while BackLoadNr == BackNr:  
            sleep(0.1) 

        print ('loading: ' + str(BackNr))

        BackLoaded = False
        BackLoadingPerc = 0
        BackNr = BackLoadNr
        BackingRunning = False
        BackIndex = 0     # nothing loaded
        ClickIndex = 0

        print 'a'
        BackName = glob.glob("./samples/" + str(BackNr) + "b*.wav")
        ClickName = glob.glob("./samples/" + str(BackNr) + "c*.wav")
        print 'b'

        if not BackName or not ClickName:
            #print 'Backing Track %s not found' % nr
            continue

        print 'c'

        Backbasenamefull = os.path.basename(BackName[0])
        Backbasename = (((Backbasenamefull)[3:-4]) + "     ")[:6]
        display('Load: ' + Backbasenamefull)
        print 'd'

        BackingRunning = False
        time.sleep(1)
        print 'e'
    
        wf_back = wave.open(BackName[0], 'rb')
        BackWav = None
        CHUNCK = 1024 * 1024
        filesize = wf_back.getnframes()
        fileremain = filesize - CHUNCK
        print 'f'
        BackWav = numpy.fromstring(wf_back.readframes(CHUNCK), dtype=numpy.int16)
        while fileremain > 0:
            if BackLoadNr != BackNr:
                break
            BackWav = numpy.append(BackWav, numpy.fromstring(wf_back.readframes(CHUNCK), dtype=numpy.int16))
            BackLoadingPerc = ((50 * (filesize-fileremain)) / filesize)
            fileremain -= CHUNCK
        print 'g'

        #BackWav = numpy.fromstring(wf_back.readframes(wf_back.getnframes()), dtype=numpy.int16)
        BackLen = len(BackWav)
        wf_back.close()

        if CHANNELS == 4:
            wf_click = wave.open(ClickName[0], 'rb')
            filesize = wf_click.getnframes()
            fileremain = filesize - CHUNCK
            ClickWav = numpy.fromstring(wf_click.readframes(CHUNCK), dtype=numpy.int16)
            print 'h'

            while fileremain > 0:
                if BackLoadNr != BackNr:
                    break
                ClickWav = numpy.append(ClickWav, numpy.fromstring(wf_click.readframes(CHUNCK), dtype=numpy.int16))
                BackLoadingPerc = 50 + ((50 * (filesize-fileremain)) / filesize)
                fileremain -= CHUNCK
                print 'i'

            #ClickWav = numpy.fromstring(wf_click.readframes(wf_click.getnframes()), dtype=numpy.int16)
            #print "click: " + str(wf_click.getparams()) 
            wf_click.close()
        print 'j'

        if BackLoadNr == BackNr:
            BackLoaded = True
            BackLoadingPerc = 100
        else:
            print ('Early stop')
            BackLoaded = False
            BackLoadedPerc = 0
        display('')


BackLoadThread = threading.Thread(target=LoadTrackProcess)
BackLoadThread.deamon = True
BackLoadThread.start()

def LoadTrackOld(nr):
    
    global BackWav, BackIndex
    global ClickWav, ClickIndex
    global BackingRunning, BackLoadingPerc, BackNr, BackLoaded, BackLen, Backbasename

    
    if nr == BackNr:  
        return

    print ('loading: ' + str(nr))

    BackLoaded = False
    BackLoadingPerc = 0
    BackNr = nr
    BackingRunning = False
    BackIndex = 0     # nothing loaded
    ClickIndex = 0

    BackName = glob.glob("./samples/" + str(nr) + "b*.wav")
    ClickName = glob.glob("./samples/" + str(nr) + "c*.wav")

    if not BackName or not ClickName:
        #print 'Backing Track %s not found' % nr
        return

    Backbasenamefull = os.path.basename(BackName[0])
    Backbasename = (((Backbasenamefull)[3:-4]) + "     ")[:6]
    display('Load: ' + Backbasenamefull)
    
    #print "load Track: " + str(nr) + " " + BackName[0]
    #print "load Click: " + str(nr) + " " + ClickName[0]
    BackingRunning = False
    time.sleep(1)
    
    wf_back = wave.open(BackName[0], 'rb')
    BackWav = None
    CHUNCK = 1024 * 1024
    filesize = wf_back.getnframes()
    fileremain = filesize - CHUNCK
    BackWav = numpy.fromstring(wf_back.readframes(CHUNCK), dtype=numpy.int16)
    while fileremain > 0:
        BackWav = numpy.append(BackWav, numpy.fromstring(wf_back.readframes(CHUNCK), dtype=numpy.int16))
        BackLoadingPerc = ((50 * (filesize-fileremain)) / filesize)
        fileremain -= CHUNCK

    #BackWav = numpy.fromstring(wf_back.readframes(wf_back.getnframes()), dtype=numpy.int16)
    BackLen = len(BackWav)
    wf_back.close()

    if CHANNELS == 4:
        wf_click = wave.open(ClickName[0], 'rb')
        filesize = wf_click.getnframes()
        fileremain = filesize - CHUNCK
        ClickWav = numpy.fromstring(wf_click.readframes(CHUNCK), dtype=numpy.int16)
        while fileremain > 0:
            ClickWav = numpy.append(ClickWav, numpy.fromstring(wf_click.readframes(CHUNCK), dtype=numpy.int16))
            BackLoadingPerc = 50 + ((50 * (filesize-fileremain)) / filesize)
            fileremain -= CHUNCK

        #ClickWav = numpy.fromstring(wf_click.readframes(wf_click.getnframes()), dtype=numpy.int16)
        #print "click: " + str(wf_click.getparams()) 
        wf_click.close()

    BackLoaded = True
    BackLoadingPerc = 100
    display('')

def StartTrack():
    global BackingRunning, BackLoaded, BackIndex
    #print "start Track: "
    if BackLoaded == True and BackIndex == 0:
        BackingRunning = True
        display('Playing Backing')
    else:
        #print 'No Backingtrack Loaded or already running'
        display('No File Loaded')

def StopTrack():
    global BackingRunning, BackIndex, ClickIndex
    #print "stop Track: "
    if BackingRunning == True:
        display('Stop Backing')
        BackingRunning = False
        BackIndex = 0
        ClickIndex = 0

# EQ

'''
filterTypes = OrderedDict({
    FilterType.LPButter: 'Low Pass (Flat)', 
    FilterType.LPBrickwall: 'Low Pass (Brickwall)',
    FilterType.HPButter: 'High Pass (Flat)',
    FilterType.HPBrickwall: 'High Pass (Brickwall)',
    FilterType.LShelving: 'Low Shelf',
    FilterType.HShelving: 'High Shelf',
    FilterType.Peak: 'Peak'})


#fs = 44100
fs = 48000
eps = 0.0000001

class Params:
    TYPE = 1
    F = 2
    G = 3
    Q = 4


deffs = [80, 1000, 3000, 5000, 15000]


chain = None 

def initFilter():
    global deffs, chain, fs
        
    chain = FilterChain()
    chain._filters.append(Filter(FilterType.LShelving, LOW_EQ, 0, 1, enabled = True))
    #chain._filters.append(Filter(FilterType.HShelving, deffs[4], 0, 1, enabled = True))
    #chain._filters.append(Filter(FilterType.Peak, deffs[0], 0, 1, enabled = True))
    chain._filters.append(Filter(FilterType.Peak, HIGH_EQ, 0, 1, enabled = True))
    #chain._filters.append(Filter(FilterType.LPButter, deffs[3], 0, 1, enabled = True))
    #chain._filters.append(Filter(FilterType.HPButter, deffs[3], 0, 1, enabled = True))
    chain.reset()
        
      
def updateFilter(i, fc, g ,Q ):
    global chain
    global fs
    oldf = chain._filters[i]
    type = oldf._type
    #print oldf._type, oldf._fc, oldf._g, oldf._Q

    #fc_val = fc * 2 / fs    
    #print fc_val, g, Q

    f = Filter(type, fc, g, Q)
    chain.updateFilt(i, f)
    #chain.changeFilt(i, type, fc, g, Q)
    chain.reset()

'''
#




#########################################
# OPEN AUDIO DEVICE
#########################################

#   
'''
try:
    sd = sounddevice.OutputStream(device=AUDIO_DEVICE_ID, blocksize=512, samplerate=44100, channels=2, dtype='int16', callback=AudioCallback)
    sd.start()
    print sd.active
    print 'Opened audio device #%i' % AUDIO_DEVICE_ID
except:
    print 'Invalid audio device #%i' % AUDIO_DEVICE_ID
    exit(1)


'''
#

p = pyaudio.PyAudio()

#initFilter()
#updateFilter(0, 1000.0, 12.0, 1.0)

print "Here is a list of audio devices:"

for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    s = ""
    if i == AUDIO_DEVICE_ID:
        s += " <--- USED"
    if (AUDIO_DEVICE_NAME in dev['name']):
        AUDIO_DEVICE_ID = i
        s += " <--- ACTUALLY, THIS ONE IS USED"
    if dev['maxOutputChannels'] > 0:
        print str(i) + ": " + dev['name'] + s
    if (s != ""):
        break
    else:
        continue


try:
    stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=SAMPLERATE, frames_per_buffer=BUFFERSIZE, output=True,
                    output_device_index=AUDIO_DEVICE_ID, stream_callback=AudioCallback)
except:
    print "Sample audio:  Invalid Audio Device ID"
    exit(1)

#



#########################################
##  LCD DISPLAY 
##  (HD44780 based 16x2)
#########################################

if USE_HD44780_16x2_LCD:
    import RPi.GPIO as GPIO
    lcd = HD44780()
    DS1 = "Starting..."
    DS1Cur = "--"
    DS2 = "  "
    DS2Cur = "  "

    def display(s):
        global DS1, DS2

        DS2 = s
        if DS2 == "": DS2 = basename
        print DS2


    TimeOutReset = 30   # 3 sec
    TimeOut = TimeOutReset
    DisplaySamplerName = True

    def LCD_Process():
        global DS1, DS1Cur, DS2, DS2Cur
        global TimeOut, TimeOutReset, basename
        global basename, MIDI_CHANNEL, globalvolumeDB, backvolumeDB, clickvolumeDB, BackingRunning, BackLoaded, BackLoadingPerc, BackLen, BackIndex
          
        lcd.message('{:<16}'.format(VERSION1) + "\n" + '{:<16}'.format(VERSION2))
        sleep(3)

        while True:
            if TimeOut > 0:
                TimeOut -= 1

            if BackingRunning: 
                ttotsec = (BackLen-BackIndex) / 48000 / 2
                tmin = ttotsec / 60
                tsec = ttotsec % 60
                ba = " %02d:%02d" % (tmin, tsec)
            elif BackLoaded: 
                ba = Backbasename[-6:] #" Ready"
            elif BackLoadingPerc > 0:
                ba = "  %3d%%" % BackLoadingPerc
            else: 
                ba = " Empty"

            DS1 = "%03d%03d%03d %s" % (globalvolumeDB, backvolumeDB, clickvolumeDB, ba)

            if TimeOut == 1:
                DS2 = basename

            if (DS2Cur != DS2) or (DS1Cur != DS1):
                if (DS2Cur != DS2): 
                    TimeOut = TimeOutReset
                lcd.message(DS1 + "\n" + '{:<16}'.format(DS2))
                DS1Cur = DS1
                DS2Cur = DS2
            sleep(0.1)

    LCDThread = threading.Thread(target=LCD_Process)
    LCDThread.deamon = True
    LCDThread.start()


else:

    def display(s):
        print s
        #pass    


#########################################

if USE_BUTTONS:
    import RPi.GPIO as GPIO

    lastbuttontime = 0

    def Buttons():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        global preset, lastbuttontime
        while True:
            now = time.time()
            if not GPIO.input(18) and (now - lastbuttontime) > 0.2:
                lastbuttontime = now
                preset -= 1
                if preset < 0:
                    preset = 127
                LoadSamples()

            elif not GPIO.input(17) and (now - lastbuttontime) > 0.2:
                lastbuttontime = now
                preset += 1
                if preset > 127:
                    preset = 0
                LoadSamples()

            time.sleep(0.020)

    ButtonsThread = threading.Thread(target=Buttons)
    ButtonsThread.daemon = True
    ButtonsThread.start()




#########################################
# MIDI IN via SERIAL PORT
#########################################

if USE_SERIALPORT_MIDI:
    import serial

    ser = serial.Serial('/dev/ttyAMA0', baudrate=38400)       # see hack in /boot/cmline.txt : 38400 is 31250 baud for MIDI!

    def MidiSerialCallback():
        message = [0, 0, 0]
        while True:
            i = 0
            while i < 3:
                data = ord(ser.read(1))  # read a byte
                if data >> 7 != 0:
                    i = 0      # status byte!   this is the beginning of a midi message: http://www.midi.org/techspecs/midimessages.php
                message[i] = data
                i += 1
                if i == 2 and message[0] >> 4 == 12:  # program change: don't wait for a third byte: it has only 2 bytes
                    message[2] = 0
                    i = 3
            MidiCallback(message, None)

    MidiThread = threading.Thread(target=MidiSerialCallback)
    MidiThread.daemon = True
    MidiThread.start()



#########################################
# LOAD FIRST SOUNDBANK
#
#########################################
'''
fvsetdry(0.7)
print 'freeverb Roomsize: ' + str(fvgetroomsize())
print 'freeverb Damp: ' + str(fvgetdamp())
print 'freeverb Wet: ' + str(fvgetwet())
print 'freeverb Dry: ' + str(fvgetdry())
print 'freeverb Width: ' + str(fvgetwidth())
'''
#

preset = 0
LoadSamples()


#########################################
# MIDI DEVICES DETECTION
# MAIN LOOP
#########################################


####ALEX TESTING WITH RTMIDI2

stopit = False
midi_in = rtmidi2.MidiInMulti()#.open_ports("*")
curr_ports = []
prev_ports = []
first_loop = True
display('Running')
while True:
    #System info
    print 'CPU: '+ str (psutil.cpu_percent(None)) + '%', 'MEM: ' + str(float(psutil.virtual_memory().percent)) + '%'
    
    if stopit:
        break
    curr_ports = rtmidi2.get_in_ports()
    #print curr_ports
    if (len(prev_ports) != len(curr_ports)):
        midi_in.close_ports()
        prev_ports = []
    for port in curr_ports:
        if port not in prev_ports and 'Midi Through' not in port and (len(prev_ports) != len(curr_ports)):
            midi_in.open_ports(port)
            midi_in.callback = MidiCallback
            if first_loop:
                print 'Opened MIDI port: ' + port
            else:
                print 'Reopening MIDI port: ' + port
    prev_ports = curr_ports    
    first_loop = False
    time.sleep(2)
    



###### ORIGINAL:


#stopit = False
#midi_in = [rtmidi.MidiIn()]
#previous = []
#
#display('Running')
#try:
#  while True:
#    if stopit:
#        break
#    
#    
#    for port in midi_in[0].ports:
#        if port not in previous and 'Midi Through' not in port:
#            midi_in.append(rtmidi.MidiIn())
#            midi_in[-1].callback = MidiCallback
#            midi_in[-1].open_port(port)
#            print 'Opened MIDI: ' + port
#            
#    
#    previous = midi_in.ports
#    time.sleep(2)
#except KeyboardInterrupt:
#   print "\nstopped by ctrl-c\n"
#except:
#   print "Other Error"
#finally:
#    display('Stopped')
#    sleep(0.5)
#    GPIO.cleanup()
