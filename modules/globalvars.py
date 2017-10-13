import platform
import numpy
import re
import configparser_samplerbox
import time
import os
import sys
import systemfunctions as sysfunc
from os import path

IS_DEBIAN = platform.linux_distribution()[0].lower() == 'debian'  # Determine if running on RPi (True / False)

####################
# IMPORT CONFIG.INI
####################

print '\n#### START CONFIG IMPORT ####\n'

config_exists = True

if path.basename(sys.modules['__main__'].__file__) == "samplerbox.py":
        CONFIG_FILE_PATH = "/boot/samplerbox/config.ini"
        print '>>>> CONFIG: Looking for config.ini in /boot/samplerbox/'
        if not os.path.exists(CONFIG_FILE_PATH):
            CONFIG_FILE_PATH = "./config.ini"
            print '>>>> CONFIG: looking for config.ini in /SamplerBox/'
            # try:
            #     file = open(CONFIG_FILE_PATH, 'r') # test if exists
            # except:
            #     file = open(CONFIG_FILE_PATH,'w')
            #     config_exists = False
            #     print 'Creating empty config.ini'
            # file.close()
        print '>>>> CONFIG used: %s' % CONFIG_FILE_PATH
else:
    CONFIG_FILE_PATH = "../config.ini"
    print '>>>> CONFIG: using config.ini in ../'

cp = configparser_samplerbox.Setup(config_file_path=CONFIG_FILE_PATH)
# If the main config doesn't exist, or if it's empty, build it with default values
if os.path.isfile(CONFIG_FILE_PATH) == False or os.stat(CONFIG_FILE_PATH).st_size == 0:
    cp.build_config_from_defaults()

SYSTEM_MODE = int(cp.get_option_by_name('SYSTEM_MODE'))
MAX_POLYPHONY = int(cp.get_option_by_name('MAX_POLYPHONY'))
MIDI_CHANNEL = int(cp.get_option_by_name('MIDI_CHANNEL'))
BUFFERSIZE = int(cp.get_option_by_name('BUFFERSIZE'))
SAMPLERATE = int(cp.get_option_by_name('SAMPLERATE'))
BOXRELEASE = int(cp.get_option_by_name('BOXRELEASE'))
RAM_LIMIT_PERCENTAGE = int(cp.get_option_by_name('RAM_LIMIT_PERCENTAGE'))
# global_volume = int(cp.get_option_by_name('GLOBAL_VOLUME'))
global_volume = 100  # ignore config.ini value and set to max
global_volume_percent = int((float(global_volume) / 100.0) * 100)
global_volume = 0 if global_volume < 0 else 100 if global_volume > 100 else global_volume
global_volume = (10.0 ** (-12.0 / 20.0)) * (float(global_volume) / 100.0)
SAMPLES_DIR = str(cp.get_option_by_name('SAMPLES_DIR'))
if path.basename(sys.modules['__main__'].__file__) == "samplerbox.py":
    if not os.path.isdir(SAMPLES_DIR):
        print '>>>> SAMPLES WARNING: dir', SAMPLES_DIR, 'not found. Looking for USB drive: /media'
        SAMPLES_DIR = '/media'
        if not os.path.isdir(SAMPLES_DIR) or not os.path.ismount(SAMPLES_DIR): # check if USB is mounted
            print '>>>> SAMPLES WARNING: USB (', SAMPLES_DIR, ') not found or not mounted. Looking for SD card dir: /samples'
            SAMPLES_DIR = '/samples'
            if not os.path.isdir(SAMPLES_DIR) or not os.path.ismount(SAMPLES_DIR):
                print '>>>> SAMPLES WARNING: dir', SAMPLES_DIR, 'not found. Looking for default: ./media' # use /media/ in /SamplerBox/ if /samples/ doesn't exist
                SAMPLES_DIR = './media'
    print '>>>> SAMPLES DIR: %s' % SAMPLES_DIR
else:
    print '>>>> SAMPLES: Using default: ../media' # dev env
    SAMPLES_DIR = '../media'
USE_BUTTONS = cp.get_option_by_name('USE_BUTTONS')
USE_HD44780_16x2_LCD = cp.get_option_by_name('USE_HD44780_16x2_LCD')
USE_HD44780_20x4_LCD = cp.get_option_by_name('USE_HD44780_20x4_LCD')
USE_FREEVERB = cp.get_option_by_name('USE_FREEVERB')
USE_TONECONTROL = cp.get_option_by_name('USE_TONECONTROL')
USE_I2C_7SEGMENTDISPLAY = cp.get_option_by_name('USE_I2C_7SEGMENTDISPLAY')
USE_GUI = cp.get_option_by_name('USE_GUI')
INVERT_SUSTAIN = cp.get_option_by_name('INVERT_SUSTAIN')
VELOCITY_CURVE = cp.get_option_by_name('VELOCITY_CURVE')
PRINT_LCD_MESSAGES = cp.get_option_by_name('PRINT_LCD_MESSAGES')
PRINT_MIDI_MESSAGES = cp.get_option_by_name('PRINT_MIDI_MESSAGES')
AUDIO_DEVICE_ID = int(cp.get_option_by_name('AUDIO_DEVICE_ID'))
AUDIO_DEVICE_NAME = str(cp.get_option_by_name('AUDIO_DEVICE_NAME'))
PRESET_BASE = int(cp.get_option_by_name('PRESET_BASE'))
GPIO_LCD_RS = int(cp.get_option_by_name('GPIO_LCD_RS'))
GPIO_LCD_E = int(cp.get_option_by_name('GPIO_LCD_E'))
GPIO_LCD_D4 = int(cp.get_option_by_name('GPIO_LCD_D4'))
GPIO_LCD_D5 = int(cp.get_option_by_name('GPIO_LCD_D5'))
GPIO_LCD_D6 = int(cp.get_option_by_name('GPIO_LCD_D6'))
GPIO_LCD_D7 = int(cp.get_option_by_name('GPIO_LCD_D7'))
GPIO_7SEG = int(cp.get_option_by_name('GPIO_7SEG'))

#########################################
# by Hans

# Auto detected in sound.py
MIXER_CARD_ID, MIXER_CONTROL, USE_ALSA_MIXER = None, None, None

NOTES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


#########################################

def button_assign(config_option_name):

    midi_str = str(cp.get_option_by_name(config_option_name))

    button_assign_list = []
    li = midi_str.split(',')

    # For notes (eg C#2)
    if li[0][:-1].lower() in NOTES:
        midi_note = NOTES.index(li[0][:-1].lower()) + (int(li[0][-1]) + 1) * 12
        midi_type = 144
        button_assign_list.extend([int(midi_type), int(midi_note)])
    # For GPIO pins (eg GPIO7)
    elif 'gpio' in midi_str.lower():
        gpio_pin = midi_str.lower().replace('gpio', '')
        button_assign_list.extend(['GPIO', gpio_pin])
    # For MIDI messages (eg 176, 60)
    elif 'none' in midi_str.lower():
        print ' [!] Warning: No MIDI control has been assigned to %s' % config_option_name
    else:
        midi_value = midi_str.replace(' ', '')
        midi_value = midi_value[0:midi_value.find('<')].split(',')
        try:
            button_assign_list.extend([int(midi_value[0]), int(midi_value[1])])
        except:
            print ' [!] Warning: Invalid MIDI navigation assignment: %s ' % midi_value
    # For if a device was specified
    if '<' in midi_str:
        midi_device = re.split('[<>]+', midi_str)[1]
        button_assign_list.append(midi_device)

    button_assign_list = filter(None, button_assign_list)  # now remove empty items
    # returns: 176, 60, <devicename> or C#2, <devicename> or GPIO, 4
    return button_assign_list

PANIC_KEY = button_assign('PANIC_KEY')

# For system mode 1 (by Alex)
BUTTON_LEFT_MIDI = button_assign('BUTTON_LEFT_MIDI')
BUTTON_RIGHT_MIDI = button_assign('BUTTON_RIGHT_MIDI')
BUTTON_ENTER_MIDI = button_assign('BUTTON_ENTER_MIDI')
BUTTON_CANCEL_MIDI = button_assign('BUTTON_CANCEL_MIDI')
BUTTON_LEFT_GPIO = int(cp.get_option_by_name('BUTTON_LEFT_GPIO'))
BUTTON_RIGHT_GPIO = int(cp.get_option_by_name('BUTTON_RIGHT_GPIO'))
BUTTON_ENTER_GPIO = int(cp.get_option_by_name('BUTTON_ENTER_GPIO'))
BUTTON_CANCEL_GPIO = int(cp.get_option_by_name('BUTTON_CANCEL_GPIO'))
# For system mode 2 (by Hans)
BUTTON_UP_MIDI = button_assign('BUTTON_UP_MIDI')
BUTTON_DOWN_MIDI = button_assign('BUTTON_DOWN_MIDI')
BUTTON_FUNC_MIDI = button_assign('BUTTON_FUNC_MIDI')
BUTTON_UP_GPIO = int(cp.get_option_by_name('BUTTON_UP_GPIO'))
BUTTON_DOWN_GPIO = int(cp.get_option_by_name('BUTTON_DOWN_GPIO'))
BUTTON_FUNC_GPIO = int(cp.get_option_by_name('BUTTON_FUNC_GPIO'))

print '\n#### END CONFIG IMPORT ####\n'

VERSION1 = " -=SAMPLER-BOX=- "
VERSION2 = "V2.0.1 15-06-2016"

###################
# MIDI MAPS
###################

if IS_DEBIAN:
    MIDIMAPS_FILE_PATH = '/boot/samplerbox/midimaps.pkl'
else:
    MIDIMAPS_FILE_PATH = 'midimaps.pkl'

print MIDIMAPS_FILE_PATH, ' <--- MIDI maps path'

###################
# SETLIST
###################

SONG_FOLDERS_LIST = [d for d in os.listdir(SAMPLES_DIR) if os.path.isdir(os.path.join(SAMPLES_DIR, d))]

if path.basename(sys.modules['__main__'].__file__) == "samplerbox.py":
    SETLIST_FILE_PATH = SAMPLES_DIR + '/setlist.txt'
else:
    SETLIST_FILE_PATH = '../setlist/setlist.txt'  # When testing modules

if not os.path.exists(SETLIST_FILE_PATH):
    print '>>>> SETLIST: %s does not exist. Creating an empty setlist file.' % SETLIST_FILE_PATH
    sysfunc.mount_samples_dir_rw()  # remount `/samples` as read-write (if using SD card)
    f = open(SETLIST_FILE_PATH, 'w')
    sysfunc.mount_samples_dir_ro()  # remount as read-only
    f.close()

SETLIST_LIST = None  # open(SETLIST_FILE_PATH).read().splitlines()
NUM_FOLDERS = len(os.walk(SAMPLES_DIR).next()[1])

# Disable Freeverb when not on Pi
if not IS_DEBIAN:
    USE_FREEVERB = False

# ADMINISTRATION SAMPLER
samples = {}
samples_indices = []
playingnotes = {}
lastplayedseq = {}
sustainplayingnotes = []
triggernotes = {}
for channel in xrange(16):
    triggernotes[channel + 1] = [128] * 128
    playingnotes[channel + 1] = {}
fillnotes = {}
sustain = False
playingsounds = []
globaltranspose = 0
basename = "<Empty>"
midicallback = None
midiserial = None

# LCD screen character dimensions
if USE_HD44780_16x2_LCD:
    LCD_COLS = 16
    LCD_ROWS = 2
elif USE_HD44780_20x4_LCD:
    LCD_COLS = 20
    LCD_ROWS = 4
else:
    LCD_COLS = 50
    LCD_ROWS = 4

####################
# Navigator, Displayer, and SystemFunction objects referenced here
# Initialized in main script
####################
nav = None
displayer = None
sysfunc = None
ac = None
autochorder = None
setlist = None
ls = None
gui = None
sound = None

# add to selection of samples, not to Velocity Volume
VelocitySelectionOffset = 0

###################
# OTHER GLOBALS
###################

# Constants

PLAYLIVE = "Keyb"  # reacts on "keyboard" interaction
PLAYONCE = "Once"  # ignores loop markers and note-off ("just play the sample")
PLAYSTOP = "On64"  # ignores loop markers with note-off by note+64 ("just play the sample with option to stop")
PLAYLOOP = "Loop"  # recognize loop markers, note-off by note+64 ("just play the loop with option to stop")
PLAYLO2X = "Loo2"  # recognize loop markers, note-off by same note ("just play the loop with option to stop")
SAMPLE_MODE_DEFAULT = PLAYLIVE

VELSAMPLE = "Sample"  # velocity equals sampled value, requires multiple samples to get differentation
VELACCURATE = "Accurate"  # velocity as played, allows for multiple (normalized!) samples for timbre
VELOCITY_MODE_DEFAULT = VELACCURATE

sample_mode = SAMPLE_MODE_DEFAULT
velocity_mode = VELOCITY_MODE_DEFAULT
# global_volume used in favour
# volume_alsa = 87  # the startup (alsa=output) volume (0-100), change with function buttons
volumeCC = 1.0  # assumed value of the volumeknob controller before first use, max=1.0 (the knob can only decrease).
preset = 0 + PRESET_BASE  # the default patch to load
voices = []
currvoice = 1
midi_mute = False
gain = 1  # the input volume correction, change per set in definition.txt

###################
# PITCH
###################

PRERELEASE = BOXRELEASE
PITCHRANGE_DEFAULT = 7  # default range of the pitchwheel in semitones (max=12. Higher than 12 produces inaccurate pitching)
PITCHBITS = 10  # pitchwheel resolution, 0=disable, max=14 (=16384 steps) values below 7 will produce bad results
PITCHBEND = 0
pitchnotes = PITCHRANGE_DEFAULT
PITCHSTEPS = 2 ** PITCHBITS
pitchneutral = PITCHSTEPS / 2
pitchdiv = 2 ** (14 - PITCHBITS)

usleep = lambda x: time.sleep(x / 1000000.0)
msleep = lambda x: time.sleep(x / 1000.0)

###################
# FADE / RELEASE / SPEED
###################

FADEOUTLENGTH = 640 * 1000  # a large table gives reasonable results (640 up to 2 sec)
FADEOUT = numpy.linspace(1., 0., FADEOUTLENGTH)  # by default, float64
FADEOUT = numpy.power(FADEOUT, 6)
FADEOUT = numpy.append(FADEOUT, numpy.zeros(FADEOUTLENGTH, numpy.float32)).astype(numpy.float32)
SPEEDRANGE = 48
SPEED = numpy.power(2, numpy.arange(-1.0 * SPEEDRANGE * PITCHSTEPS, 1.0 * SPEEDRANGE * PITCHSTEPS) / (
    12 * PITCHSTEPS)).astype(numpy.float32)

###################
# BACKING TRACK VARS
###################

# wf_back = None
# wf_click = None
# BackingRunning = False
# backvolume = 0
# backvolumeDB = 0
# clickvolume = 0
# clickvolumeDB = 0

###################
# MIDI LEARNING
###################

midimaps = None
learningMode = False

###################
# GLOBAL DISPLAY VARS
###################

GPIO_button_func = None
GPIO_function_val = None
percent_loaded = 0
percent_effect = 0
