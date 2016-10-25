import numpy
import platform
import os
import configparser

IS_DEBIAN = platform.linux_distribution()[0].lower() == 'debian' # Determine if running on RPi (True or False)

if IS_DEBIAN:
    AUDIO_DEVICE_ID     = 2
else:
    AUDIO_DEVICE_ID     = 4                 # change this number to use another soundcard
AUDIO_DEVICE_NAME       = "USB Audio DAC"   # If we know the name (or part of the name), match by name instead
SAMPLES_DIR             = "./media"         # The root directory containing the sample-sets. Example: "/media/" to look for samples on a USB stick / SD card
USE_SERIALPORT_MIDI     = False             # Set to True to enable MIDI IN via SerialPort (e.g. RaspberryPi's GPIO UART pins)
USE_I2C_7SEGMENTDISPLAY = False             # Set to True to use a 7-segment display via I2C
VERSION1                = " -=SAMPLER-BOX=- "
VERSION2                = "V2.0.1 15-06-2016"

MIDI_CONFIG_DIR = "midi config/"
CONFIG_FILE_PATH = "system config/config.ini"
SETLIST_FILE_PATH = "setlist/setlist.txt"
SONG_FOLDERS_LIST = os.listdir(SAMPLES_DIR)

LCD_DEBUG = True                                                # Print LCD messages to python output




def parseConfig():
    global MAX_POLYPHONY, MIDI_CHANNEL, CHANNELS, BUFFERSIZE, SAMPLERATE
    global GLOBAL_VOLUME, USE_BUTTONS, USE_HD44780_16x2_LCD, USE_FREEVERB, USE_TONECONTROL

    if config.read(CONFIG_FILE_PATH):
        print '-= Reading settings from config.ini =-'
        MAX_POLYPHONY = int(config['DEFAULT']['MAX_POLYPHONY'])
        MIDI_CHANNEL = int(config['DEFAULT']['MIDI_CHANNEL'])
        CHANNELS = int(config['DEFAULT']['CHANNELS'])
        BUFFERSIZE = int(config['DEFAULT']['BUFFERSIZE'])
        SAMPLERATE = int(config['DEFAULT']['SAMPLERATE'])
        GLOBAL_VOLUME = int(config['DEFAULT']['GLOBAL_VOLUME'])
        USE_BUTTONS = bool(config['DEFAULT']['USE_BUTTONS'])
        USE_HD44780_16x2_LCD = bool(config['DEFAULT']['USE_HD44780_16x2_LCD'])
        USE_FREEVERB = bool(config['DEFAULT']['USE_FREEVERB'])
        USE_TONECONTROL = bool(config['DEFAULT']['USE_TONECONTROL'])
    else:
        print '!! config.ini does not exist - using defaults !!'
        MAX_POLYPHONY = 80
        MIDI_CHANNEL = 1
        CHANNELS = 4
        BUFFERSIZE = 128
        SAMPLERATE = 44100
        GLOBAL_VOLUME = 100
        USE_BUTTONS = False
        USE_HD44780_16x2_LCD = True
        USE_FREEVERB = True
        USE_TONECONTROL = False


config = configparser.ConfigParser()
parseConfig()

def writeConfig():
    config['DEFAULT']['MAX_POLYPHONY'] = str(MAX_POLYPHONY)
    config['DEFAULT']['MIDI_CHANNEL'] = str(MIDI_CHANNEL)
    config['DEFAULT']['CHANNELS'] = str(CHANNELS)
    config['DEFAULT']['BUFFERSIZE'] = str(BUFFERSIZE)
    config['DEFAULT']['SAMPLERATE'] = str(SAMPLERATE)
    config['DEFAULT']['GLOBAL_VOLUME'] = str(GLOBAL_VOLUME)
    config['DEFAULT']['USE_BUTTONS'] = str(USE_BUTTONS)
    config['DEFAULT']['USE_HD44780_16x2_LCD'] = str(USE_HD44780_16x2_LCD)
    config['DEFAULT']['USE_FREEVERB'] = str(USE_FREEVERB)
    config['DEFAULT']['USE_TONECONTOL'] = str(USE_TONECONTROL)
    print 'WRITING CONFIG'
    with open(CONFIG_FILE_PATH, 'w') as configfile:
        config.write(configfile)




# Disable Freeverb when not on Pi
if not IS_DEBIAN:
    USE_FREEVERB = False


# settings for ToneControl
LOW_EQ_FREQ = 80.0
HIGH_EQ_FREQ = 8000.0
HIGH_EQ = (2 * HIGH_EQ_FREQ) / SAMPLERATE
LOW_EQ = (2 * LOW_EQ_FREQ) / SAMPLERATE


# BACKING TRACK VARS
wf_back = None
wf_click = None
BackingRunning = False

# FADE / RELEASE
FADEOUTLENGTH = 30000
FADEOUT = numpy.linspace(1., 0., FADEOUTLENGTH)            # by default, float64
FADEOUT = numpy.power(FADEOUT, 6)
FADEOUT = numpy.append(FADEOUT, numpy.zeros(FADEOUTLENGTH, numpy.float32)).astype(numpy.float32)
SPEED = numpy.power(2, numpy.arange(0.0, 84.0) / 12).astype(numpy.float32)

# ADMINISTRATION SAMPLER
samples = {}
playingnotes = {}
totalVoices = 1
sustainplayingnotes = []
sustain = False
playingsounds = []
globaltranspose = 0
basename = "<Empty>"

nav = None

VelocitySelectionOffset = 0		#add to selection of samples, not to Velocity Volume

# VOLUMES
globalvolume = 0
globalvolumeDB = 0
backvolume = 0
backvolumeDB = 0
clickvolume = 0
clickvolumeDB = 0

# PRESETS
preset = 0
current_voice = 1

# MIDI LEARNING
midimaps = None
learningMode = False

