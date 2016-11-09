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

AUDIO_DEVICE_ID = int(cs.get_config_item_by_name('AUDIO_DEVICE_ID'))  # An external USB sound device on RPi is usually 2
AUDIO_DEVICE_NAME = "USB Audio DAC"  # If we know the name (or part of the name), match by name instead


########  LITERALS, don't change ########
# by Hans

PLAYLIVE = "Keyb"                       # reacts on "keyboard" interaction
PLAYBACK = "Once"                       # ignores loop markers and note-off ("just play the sample")
PLAYSTOP = "On64"                       # ignores loop markers with note-off by note+64 ("just play the sample with option to stop")
PLAYLOOP = "Loop"                       # recognize loop markers, note-off by note+64 ("just play the loop with option to stop")
PLAYLO2X = "Loo2"                       # recognize loop markers, note-off by same note ("just play the loop with option to stop")
VELSAMPLE = "Sample"                    # velocity equals sampled value, requires multiple samples to get differentation
VELACCURATE = "Accurate"                # velocity as played, allows for multiple (normalized!) samples for timbre

#########################################
# by Hans

MIXER_CARD_ID = 1                       # change this number to start checking with other card index, default=0
MIXER_CONTROL = "Speaker"               # change this name according soundcard, default="PCM"
USE_ALSA_MIXER = True                   # Set to True to use to use the alsa mixer (via pyalsaaudio)
sample_mode = PLAYLIVE                  # we need a default: original samplerbox
velocity_mode = VELSAMPLE               # we need a default: original samplerbox
volume = 87                             # the startup (alsa=output) volume (0-100), change with function buttons
volumeCC = 1.0                          # assumed value of the volumeknob controller before first use, max=1.0 (the knob can only decrease).
PRESETBASE = 0                          # Does the programchange / sample set start at 0 (MIDI style) or 1 (human style)
preset = 0 + PRESETBASE                 # the default patch to load
PITCHRANGE = 12                         # default range of the pitchwheel in semitones (max=12 is een octave)
PITCHBITS = 7                           # pitchwheel resolution, 0=disable, max=14 (=16384 steps)
                                        # values below 7 will produce bad results


########## Chords definitions  # You always need index=0 (is single note, "normal play")
# by Hans

chordname = ["", "Maj", "Min", "Augm", "Dim", "Sus2", "Sus4", "Dom7", "Maj7", "Min7", "MiMa7", "hDim7", "Dim7", "Aug7",
             "AuMa7", "D7S4"]
chordnote = [[0], [0, 4, 7], [0, 3, 7], [0, 4, 8], [0, 3, 6], [0, 2, 7], [0, 5, 7], [0, 4, 7, 10], [0, 4, 7, 11],
             [0, 3, 7, 10], [0, 3, 7, 11], [0, 3, 6, 10], [0, 3, 6, 9], [0, 4, 8, 10], [0, 4, 8, 11], [0, 5, 7, 10]]
currchord = 0  # single note, "normal play"



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


BUTTON_LEFT = button_assign(str(cs.get_config_item_by_name('BUTTON_LEFT')))
BUTTON_RIGHT = button_assign(str(cs.get_config_item_by_name('BUTTON_RIGHT')))
BUTTON_ENTER = button_assign(str(cs.get_config_item_by_name('BUTTON_ENTER')))
BUTTON_CANCEL = button_assign(str(cs.get_config_item_by_name('BUTTON_CANCEL')))



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


########## Initialize other globals, don't change
# by Hans

voices = [] # _____NEW
currvoice = 1 # _____NEW
midi_mute = False # _____NEW
gain = 1   # _____NEW # the input volume correction, change per set in definition.txt
PITCHBEND = 0 # _____NEW
pitchnotes = PITCHRANGE # _____NEW
PITCHSTEPS = 2 ** PITCHBITS # _____NEW
pitchneutral = PITCHSTEPS / 2 # _____NEW
pitchdiv = 2 ** (14 - PITCHBITS) # _____NEW

# ADMINISTRATION SAMPLER
samples = {}
playingnotes = {}
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

# MIDI LEARNING
midimaps = None
learningMode = False
