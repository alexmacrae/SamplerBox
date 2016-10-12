import numpy
import platform

AUDIO_DEVICE_ID         = 4                  # change this number to use another soundcard
AUDIO_DEVICE_NAME       = "USB Audio DAC"   # If we know the name (or part of the name), match by name instead
#SAMPLES_DIR            = "../../media"     # The root directory containing the sample-sets. Example: "/media/" to look for samples on a USB stick / SD card
SAMPLES_DIR             = "./media"         # The root directory containing the sample-sets. Example: "/media/" to look for samples on a USB stick / SD card
USE_SERIALPORT_MIDI     = False             # Set to True to enable MIDI IN via SerialPort (e.g. RaspberryPi's GPIO UART pins)
USE_I2C_7SEGMENTDISPLAY = False             # Set to True to use a 7-segment display via I2C
USE_BUTTONS             = False             # Set to True to use momentary buttons (connected to RaspberryPi's GPIO pins) to change preset
MAX_POLYPHONY           = 80                # This can be set higher, but 80 is a safe value
MIDI_CHANNEL            = 1
USE_HD44780_16x2_LCD    = False             # Set to True to use a HD44780 based 16x2 LCD
USE_FREEVERB            = False             # Set to True to enable FreeVerb
USE_TONECONTOL          = False	            # Set to True to enable Tonecontrol (also remove comments in code
CHANNELS                = 2	                # set to 2 for normal stereo output, 4 for 4 channel playback
BUFFERSIZE              = 128               # Buffersize: lower means less latency, higher more polyphony and stability
SAMPLERATE              = 44100
VERSION1                = " -=SAMPLER-BOX=- "
VERSION2                = "V2.0.1 15-06-2016"

LCD_DEBUG = False                                                # Print LCD messages to python
IS_DEBIAN = platform.linux_distribution()[0].lower() == 'debian' # Determine if running on RPi (True or False)



# settings for ToneControl
LOW_EQ_FREQ = 80.0
HIGH_EQ_FREQ = 8000.0
HIGH_EQ = (2 * HIGH_EQ_FREQ) / SAMPLERATE
LOW_EQ = (2 * LOW_EQ_FREQ) / SAMPLERATE


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

nav = None

VelocitySelectionOffset = 0		#add to selection of samples, not to Velocity Volume

globalvolume = 0
globalvolumeDB = 0
backvolume = 0
backvolumeDB = 0
clickvolume = 0
clickvolumeDB = 0

preset = 0
current_voice = 1