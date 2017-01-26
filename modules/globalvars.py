import platform
import os
import numpy
import re
import configparser_samplerbox as cp
import time

IS_DEBIAN = platform.linux_distribution()[0].lower() == 'debian'  # Determine if running on RPi (True / False)
CONFIG_PRINT = True

####################
# IMPORT CONFIG.INI
####################

if CONFIG_PRINT: print '\n#### START CONFIG IMPORT ####\n'

SYSTEM_MODE = int(cp.get_option_by_name('SYSTEM_MODE'))
MAX_POLYPHONY = int(cp.get_option_by_name('MAX_POLYPHONY'))
MIDI_CHANNEL = int(cp.get_option_by_name('MIDI_CHANNEL'))
CHANNELS = int(cp.get_option_by_name('CHANNELS'))
BUFFERSIZE = int(cp.get_option_by_name('BUFFERSIZE'))
SAMPLERATE = int(cp.get_option_by_name('SAMPLERATE'))
RAM_LIMIT_PERCENTAGE = int(cp.get_option_by_name('RAM_LIMIT_PERCENTAGE'))
global_volume = int(cp.get_option_by_name('GLOBAL_VOLUME'))
global_volume_percent = int((float(global_volume) / 100.0) * 100)
global_volume = 0 if global_volume < 0 else 100 if global_volume > 100 else global_volume
global_volume = (10.0 ** (-12.0 / 20.0)) * (float(global_volume) / 100.0)
SAMPLES_DIR = str(cp.get_option_by_name('SAMPLES_DIR'))
if not os.path.isdir(SAMPLES_DIR):
    print 'WARNING: The directory', SAMPLES_DIR, 'was not found. Using default: ./media'
    SAMPLES_DIR = './media'
USE_BUTTONS = cp.get_option_by_name('USE_BUTTONS')
USE_HD44780_16x2_LCD = cp.get_option_by_name('USE_HD44780_16x2_LCD')
USE_HD44780_20x4_LCD = cp.get_option_by_name('USE_HD44780_20x4_LCD')
USE_FREEVERB = cp.get_option_by_name('USE_FREEVERB')
USE_TONECONTROL = cp.get_option_by_name('USE_TONECONTROL')
USE_SERIALPORT_MIDI = cp.get_option_by_name('USE_SERIALPORT_MIDI')
USE_I2C_7SEGMENTDISPLAY = cp.get_option_by_name('USE_I2C_7SEGMENTDISPLAY')
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

# (config.ini) change this number to start checking with other card index, default=0
MIXER_CARD_ID = int(cp.get_option_by_name('MIXER_CARD_ID'))
# (config.ini) change this name according soundcard, default="PCM"
MIXER_CONTROL = str(cp.get_option_by_name('MIXER_CONTROL'))
# (config.ini) Set to True to use to use the alsa mixer (via pyalsaaudio)
USE_ALSA_MIXER = cp.get_option_by_name('USE_ALSA_MIXER')

NOTES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


def button_assign(midi_str):
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
    else:
        midi_value = midi_str.replace(' ', '')
        midi_value = midi_value[0:midi_value.find('<')].split(',')
        button_assign_list.extend([int(midi_value[0]), int(midi_value[1])])
    # For if a device was specified
    if '<' in midi_str:
        midi_device = re.split('[<>]+', midi_str)[1]
        button_assign_list.append(midi_device)

    button_assign_list = filter(None, button_assign_list)  # now remove empty items
    # returns: 176, 60, <devicename> or C#2, <devicename> or GPIO, 4
    return button_assign_list


# For system mode 1 (by Alex)
BUTTON_LEFT_MIDI = button_assign(str(cp.get_option_by_name('BUTTON_LEFT_MIDI')))
BUTTON_RIGHT_MIDI = button_assign(str(cp.get_option_by_name('BUTTON_RIGHT_MIDI')))
BUTTON_ENTER_MIDI = button_assign(str(cp.get_option_by_name('BUTTON_ENTER_MIDI')))
BUTTON_CANCEL_MIDI = button_assign(str(cp.get_option_by_name('BUTTON_CANCEL_MIDI')))
BUTTON_LEFT_GPIO = int(cp.get_option_by_name('BUTTON_LEFT_GPIO'))
BUTTON_RIGHT_GPIO = int(cp.get_option_by_name('BUTTON_RIGHT_GPIO'))
BUTTON_ENTER_GPIO = int(cp.get_option_by_name('BUTTON_ENTER_GPIO'))
BUTTON_CANCEL_GPIO = int(cp.get_option_by_name('BUTTON_CANCEL_GPIO'))
# For system mode 2 (by Hans)
BUTTON_UP_MIDI = button_assign(str(cp.get_option_by_name('BUTTON_UP_MIDI')))
BUTTON_DOWN_MIDI = button_assign(str(cp.get_option_by_name('BUTTON_DOWN_MIDI')))
BUTTON_FUNC_MIDI = button_assign(str(cp.get_option_by_name('BUTTON_FUNC_MIDI')))
BUTTON_UP_GPIO = int(cp.get_option_by_name('BUTTON_UP_GPIO'))
BUTTON_DOWN_GPIO = int(cp.get_option_by_name('BUTTON_DOWN_GPIO'))
BUTTON_FUNC_GPIO = int(cp.get_option_by_name('BUTTON_FUNC_GPIO'))

if CONFIG_PRINT: print '\n#### END CONFIG IMPORT ####\n'

VERSION1 = " -=SAMPLER-BOX=- "
VERSION2 = "V2.0.1 15-06-2016"

###################
# MIDI MAPS
###################

MIDIMAPS_FILE_PATH = 'midimaps.pkl'

###################
# SETLIST
###################

SONG_FOLDERS_LIST = os.listdir(SAMPLES_DIR)
SETLIST_FILE_PATH = 'setlist/setlist.txt'
SETLIST_LIST = None #open(SETLIST_FILE_PATH).read().splitlines()
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
sustain = False
playingsounds = []
globaltranspose = 0
basename = "<Empty>"

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
setlist = None
ls = None

# add to selection of samples, not to Velocity Volume
VelocitySelectionOffset = 0

###################
# OTHER GLOBALS
###################

# Constants



PLAYLIVE = "Keyb"  # reacts on "keyboard" interaction
PLAYBACK = "Once"  # ignores loop markers and note-off ("just play the sample")
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



PITCHRANGE_DEFAULT = 12  # default range of the pitchwheel in semitones (max=12. Higher than 12 produces inaccurate pitching)
PITCHBITS = 7  # pitchwheel resolution, 0=disable, max=14 (=16384 steps) values below 7 will produce bad results
PITCHBEND = 0
pitchnotes = PITCHRANGE_DEFAULT * 2
PITCHSTEPS = 2 ** PITCHBITS
pitchneutral = PITCHSTEPS / 2
pitchdiv = 2 ** (14 - PITCHBITS)

usleep = lambda x: time.sleep(x / 1000000.0)
msleep = lambda x: time.sleep(x / 1000.0)

###################
# FADE / RELEASE / SPEED
###################
FADEOUTLENGTH_DEFAULT = 30000
FADEOUTLENGTH = FADEOUTLENGTH_DEFAULT
FADEOUT = numpy.linspace(1., 0., FADEOUTLENGTH)  # by default, float64
FADEOUT = numpy.power(FADEOUT, 6)
FADEOUT = numpy.append(FADEOUT, numpy.zeros(FADEOUTLENGTH, numpy.float32)).astype(numpy.float32)
SPEED = numpy.power(2, numpy.arange(-48.0 * PITCHSTEPS, 48.0 * PITCHSTEPS) / (12 * PITCHSTEPS)).astype(numpy.float32)

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
