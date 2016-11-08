import platform
import os
import numpy
import re
import configparser_samplerbox as cs

IS_DEBIAN = platform.linux_distribution()[0].lower() == 'debian'  # Determine if running on RPi (True / False)


MAX_POLYPHONY = int(cs.get_config_item_by_name('MAX_POLYPHONY'))
MIDI_CHANNEL = int(cs.get_config_item_by_name('MIDI_CHANNEL'))
CHANNELS = int(cs.get_config_item_by_name('CHANNELS'))
BUFFERSIZE = int(cs.get_config_item_by_name('BUFFERSIZE'))
SAMPLERATE = int(cs.get_config_item_by_name('SAMPLERATE'))
GLOBAL_VOLUME = int(cs.get_config_item_by_name('GLOBAL_VOLUME'))

SAMPLES_DIR = str(cs.get_config_item_by_name('SAMPLES_DIR'))
if not os.path.isdir(SAMPLES_DIR):
    print 'WARNING: The directory', SAMPLES_DIR, 'was not found. Using default: ./media'
    SAMPLES_DIR = './media'

USE_BUTTONS = cs.get_config_item_by_name('USE_BUTTONS')
USE_HD44780_16x2_LCD = cs.get_config_item_by_name('USE_HD44780_16x2_LCD')
USE_FREEVERB = cs.get_config_item_by_name('USE_FREEVERB')
USE_TONECONTROL = cs.get_config_item_by_name('USE_TONECONTROL')
USE_SERIALPORT_MIDI = cs.get_config_item_by_name(
    'USE_SERIALPORT_MIDI')  # Set to True to enable MIDI IN via SerialPort (e.g. RaspberryPi's GPIO UART pins)
USE_I2C_7SEGMENTDISPLAY = cs.get_config_item_by_name(
    'USE_I2C_7SEGMENTDISPLAY')  # Set to True to use a 7-segment display via I2C
LCD_DEBUG = cs.get_config_item_by_name('LCD_DEBUG')
PRINT_MIDI_MESSAGES = cs.get_config_item_by_name('PRINT_MIDI_MESSAGES')

NOTES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


def button_assign(midi_str):
    new_list = []
    li = midi_str.split(',')

    # For notes (eg C#2)
    if li[0][:-1].lower() in NOTES:
        midi_note = NOTES.index(li[0][:-1].lower()) + (int(li[0][-1]) + 1) * 12
        midi_type = 144
        new_list.extend([int(midi_type), int(midi_note)])
    # For GPIO pins (eg GPIO7)
    elif 'gpio' in midi_str.lower():
        gpio_pin = midi_str.lower().replace('gpio', '')
        new_list.extend(['GPIO', gpio_pin])
    # For MIDI messages (eg 176, 60)
    else:
        midi_value = midi_str.replace(' ', '')
        midi_value = midi_value[0:midi_value.find('<')].split(',')
        new_list.extend([int(midi_value[0]), int(midi_value[1])])
    # For if a device was specified
    if '<' in midi_str:
        midi_device = re.split('[<>]+', midi_str)[1]
        new_list.append(midi_device)

    new_list = filter(None, new_list)  # now remove empty items
    return new_list
    # print 'NEW LIST: ',new_list
    #
    # print '----------'


BUTTON_LEFT = button_assign(str(cs.get_config_item_by_name('BUTTON_LEFT')))
BUTTON_RIGHT = button_assign(str(cs.get_config_item_by_name('BUTTON_RIGHT')))
BUTTON_ENTER = button_assign(str(cs.get_config_item_by_name('BUTTON_ENTER')))
BUTTON_CANCEL = button_assign(str(cs.get_config_item_by_name('BUTTON_CANCEL')))

AUDIO_DEVICE_ID = int(cs.get_config_item_by_name('AUDIO_DEVICE_ID'))  # An external USB sound device on RPi is usually 2
AUDIO_DEVICE_NAME = "USB Audio DAC"  # If we know the name (or part of the name), match by name instead

VERSION1 = " -=SAMPLER-BOX=- "
VERSION2 = "V2.0.1 15-06-2016"

SONG_FOLDERS_LIST = os.listdir(SAMPLES_DIR)
SETLIST_FILE_PATH = 'setlist/setlist.txt'

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
FADEOUT = numpy.linspace(1., 0., FADEOUTLENGTH)  # by default, float64
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

# navigator object always referenced here. eg gvars.nav.state.enter()
nav = None

VelocitySelectionOffset = 0  # add to selection of samples, not to Velocity Volume

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
