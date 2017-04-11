#################
# MIXER CLASSES #
#################
import samplerbox_audio
import struct
import wave
from chunk import Chunk
import numpy
import sounddevice
import globalvars as gv
import exceptions
import sys
import re
if gv.IS_DEBIAN:
    import alsaaudio


############################################################
# SLIGHT MODIFICATION OF PYTHON'S WAVE MODULE              #
# TO READ CUE MARKERS & LOOP MARKERS if applicable in mode #
############################################################


class waveread(wave.Wave_read):
    def initfp(self, file):
        self._convert = None
        self._soundpos = 0
        self._cue = []
        self._loops = []
        self._ieee = False
        self._file = Chunk(file, bigendian=0)
        if self._file.getname() != 'RIFF':
            raise exceptions.WaveReadError, 'file does not start with RIFF id'
        if self._file.read(4) != 'WAVE':
            raise exceptions.WaveReadError, 'not a WAVE file'
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
                    raise exceptions.WaveReadError, 'data chunk before fmt chunk'
                self._data_chunk = chunk
                self._nframes = chunk.chunksize // self._framesize
                self._data_seek_needed = 0
            elif chunkname == 'cue ':
                numcue = struct.unpack('<i', chunk.read(4))[0]
                for i in range(numcue):
                    id, position, datachunkid, chunkstart, blockstart, sampleoffset = struct.unpack('<iiiiii',
                                                                                                    chunk.read(24))
                    self._cue.append(sampleoffset)
            elif chunkname == 'smpl':
                manuf, prod, sampleperiod, midiunitynote, midipitchfraction, smptefmt, smpteoffs, numsampleloops, samplerdata = struct.unpack(
                    '<iiiiiiiii', chunk.read(36))
                for i in range(numsampleloops):
                    cuepointid, type, start, end, fraction, playcount = struct.unpack('<iiiiii', chunk.read(24))
                    self._loops.append([start, end])
            chunk.skip()
        if not self._fmt_chunk_read or not self._data_chunk:
            raise exceptions.WaveReadError, 'fmt chunk and/or data chunk missing'

    def getmarkers(self):
        return self._cue

    def getloops(self):
        if gv.sample_mode == gv.PLAYLIVE or gv.sample_mode == gv.PLAYLOOP or gv.sample_mode == gv.PLAYLO2X:
            return self._loops


class PlayingSound:
    def __init__(self, sound, note, vel, timestamp=None):
        self.sound = sound
        self.pos = 0
        self.fadeoutpos = 0
        self.isfadeout = False
        self.note = note
        self.vel = vel
        self.timestamp = timestamp

    def fadeout(self, i):
        if self.isfadeout:
            try:
                gv.playingsounds.remove(self)
            except:
                pass
        else:
            self.isfadeout = True

    def stop(self):
        try:
            gv.playingsounds.remove(self)
        except:
            pass


class Sound:
    def __init__(self, filename, midinote, velocity, seq, channel, release):
        wf = waveread(filename)
        self.fname = filename
        self.midinote = midinote
        self.velocity = velocity
        self.seq = seq
        self.channel = channel
        self.release = release

        if wf.getloops():
            self.loop = wf.getloops()[0][0]
            self.nframes = wf.getloops()[0][1] + 2
        else:
            self.loop = -1
            self.nframes = wf.getnframes()
        self.data = self.frames2array(wf.readframes(self.nframes), wf.getsampwidth(), wf.getnchannels())
        wf.close()

    def play(self, note, vel, timestamp=None):
        snd = PlayingSound(self, note, vel, timestamp)
        # print 'fname: ' + self.fname + ' note/vel: ' + str(note) + '/' + str(vel) + ' midinote: ' + str(self.midinote) + ' vel: ' + str(self.velocity)
        gv.playingsounds.append(snd)
        return snd

    def frames2array(self, data, sampwidth, numchan):
        if sampwidth == 2:
            npdata = numpy.fromstring(data, dtype=numpy.int16)
        elif sampwidth == 3:
            npdata = samplerbox_audio.binary24_to_int16(data, len(data) / 3)
        if numchan == 1:
            npdata = numpy.repeat(npdata, 2)
        return npdata


##################
# AUDIO CALLBACK #
##################

def audio_callback(outdata, frame_count, time_info, status):
    rmlist = []
    gv.playingsounds = gv.playingsounds[-gv.MAX_POLYPHONY:]

    # b = samplerbox_audio.mixaudiobuffers(gv.playingsounds, rmlist, frame_count,
    #                                      gv.FADEOUT, gv.FADEOUTLENGTH, gv.SPEED,
    #                                      gv.PITCHBEND, gv.PITCHSTEPS)

    b = samplerbox_audio.mixaudiobuffers(gv.playingsounds, rmlist, frame_count, gv.FADEOUT, gv.FADEOUTLENGTH,
                                         gv.PRERELEASE, gv.SPEED, gv.SPEEDRANGE, gv.PITCHBEND, gv.PITCHSTEPS)

    """
    With the below uncommented, a MIDI volume controller will control ALSA audio only.
    This is problematic; we want to control ALSA only. Full volume sounddevice might cause distortion.
    """
    # if gv.USE_ALSA_MIXER == False: # Use alsamixer's setvolume instead
    b *= (gv.global_volume * gv.volumeCC)

    if gv.USE_FREEVERB and gv.IS_DEBIAN:
        b_verb = b
        gv.ac.reverb.freeverbprocess(b_verb.ctypes.data_as(gv.ac.reverb.c_float_p),
                                     b.ctypes.data_as(gv.ac.reverb.c_float_p), frame_count)

        # if gv.USE_ALSA_MIXER == False:  # Use alsamixer's setvolume instead
        b_verb *= (gv.global_volume * gv.volumeCC)

    for e in rmlist:
        try:
            gv.playingsounds.remove(e)
        except:
            pass

    outdata[:] = b.reshape(outdata.shape)

    # if gv.USE_TONECONTROL:
    #     b_tc = numpy.array(gv.ac.tone_control.chain.filter(b))
    #     # b = b_tc

#####################
# OPEN AUDIO DEVICE #
#####################

class StartSound:
    def __init__(self):

        print '\n#### START OF AUDIO DEVICES ####\n'
        print 'Available devices:'
        self.all_audio_devices = self.get_all_audio_devices()
        print sounddevice.query_devices()  # all available audio devices (with audio output)

        self.sd = None
        self.amixer = None
        self.mixer_card_index = 0
        self.mixer_id = 0
        self.mixer_control = 'PCM'

        self.set_audio_device(gv.AUDIO_DEVICE_NAME)

        print '\n#### END OF AUDIO DEVICES ####\n'

    ############################
    # Start sounddevice stream #
    ############################

    def start_sounddevice_stream(self, latency='low'):

        try:
            self.sd = sounddevice.OutputStream(device=gv.AUDIO_DEVICE_ID, latency=latency, samplerate=gv.SAMPLERATE, channels=gv.CHANNELS, dtype='int16', callback=audio_callback)
            self.sd.start()
            print '>>>> Opened audio device #%i (latency: %ims)' % (gv.AUDIO_DEVICE_ID, self.sd.latency * 1000)
        except:
            gv.displayer.disp_change('Invalid audio device', line=2, timeout=0)
            print 'Invalid audio device #%i' % gv.AUDIO_DEVICE_ID

    ##############
    # ALSA mixer #
    ##############

    def get_alsa_volume(self):
        vol = self.amixer.getvolume()
        gv.global_volume = int(vol[0])

    def set_alsa_volume(self, volume):
        # self.amixer.setvolume(int(volume))
        self.amixer.setvolume(100) # Just set it to 100% and let sounddevice control volume

    def start_alsa_mixer(self):
        self.amixer = alsaaudio.Mixer(id=self.mixer_id, cardindex=self.mixer_card_index, control=self.mixer_control)
        self.set_alsa_volume(gv.global_volume_percent)

    def is_alsa_device(self, device_name):
        # print 'MIXERS: %s' % alsaaudio.mixers() #show available mixer controls

        if gv.IS_DEBIAN == False:
            return

        if device_name == 'bcm2835':
            mixer_card_index = 0
        else:
            mixer_card_index = re.search('\(hw:(.*),', device_name) # get x from (hw:x,y) in device name
            mixer_card_index = int(mixer_card_index.group(1))

        available_mixer_types = alsaaudio.mixers() # returns a list of available mixer types. Usually only "PCM"

        for mixer_control in available_mixer_types:
            print '>>>> Trying mixer control "%s"' % mixer_control
            for mixer_id in range(0, 6):
                try:
                    amixer = alsaaudio.Mixer(id=mixer_id, cardindex=mixer_card_index, control=mixer_control)
                    print amixer.cardname()
                    del amixer # No use for amixer in this method. Create instance in start_alsa_mixer()
                    gv.USE_ALSA_MIXER = True
                    self.mixer_id = mixer_id
                    self.mixer_card_index = mixer_card_index  # save the found value
                    self.mixer_control = mixer_control
                    print '>>>> Found ALSA device: card id "%i", control "%s"' % (self.mixer_card_index, mixer_control)

                    return True

                except Exception as e:
                    # gv.displayer.disp_change('Invalid mixerdev', line=2, timeout=0)
                    # print 'Invalid mixer card id "%i" or control "%s"' % (gv.MIXER_CARD_ID, gv.MIXER_CONTROL)
                    print 'Invalid mixer card id "%i" or control "%s"' % (mixer_card_index, mixer_control)
                    # print 'Available devices (mixer card id is "x" in "(hw:x,y)" of device #%i):' % gv.AUDIO_DEVICE_ID
                    # print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)

        print '>>>> This is not an ALSA compatible device'
        gv.USE_ALSA_MIXER = False
        return False

    #################
    # End alsaaudio #
    #################

    def close_stream(self):
        if self.sd:
            print ">>>>> Closing sounddevice stream"
            self.sd.abort()
            self.sd.stop()
            self.sd.close()

    def get_all_audio_devices(self):
        all_output_devices = {}
        i = 0
        for d in sounddevice.query_devices():
            if d['max_output_channels'] > 0:
                all_output_devices[i] = d
                i += 1
        return all_output_devices

    """
    Select a device by name. On startup try AUDIO_DEVICE_NAME specified in the config.ini.
    If no match is found, search for any audio device that isn't a RPi device. Failing that, use the default
    on-board bcm2835 ALSA sound device.
    NOTE: In SYSTEM_MODE=1 we can change the device via the menu.
    """

    def set_audio_device(self, device_name):

        device_found = False
        try:
            if gv.AUDIO_DEVICE_ID >= 0:
                print '>>>> Using user-defined AUDIO_DEVICE_ID (%d)' % gv.AUDIO_DEVICE_ID
                pass
            else:
                i = 0
                for d in sounddevice.query_devices():
                    if device_name in d['name'] and d['max_output_channels'] > 0:
                        gv.AUDIO_DEVICE_ID = i
                        device_name = d['name']
                        gv.AUDIO_DEVICE_NAME = device_name
                        print '\r>>>> Device selected by name: [%i]: %s\r' % (i, device_name)
                        device_found = True
                        break
                    i += 1

                if device_found is not True and gv.IS_DEBIAN:
                    print ">>>> Device defined in config.ini could not be found. Looking for other connected audio devices."
                    i = 0
                    for d in sounddevice.query_devices():
                        print d['name']
                        if 'bcm2835 ALSA' not in d['name'] and 'sysdefault' not in d['name'] \
                                and 'default' not in d['name'] and 'dmix' not in d['name'] \
                                and d['max_output_channels'] > 0:
                            gv.AUDIO_DEVICE_ID = i
                            device_name = d['name']
                            gv.AUDIO_DEVICE_NAME = device_name
                            print '\r>>>>> Device selected by name: [%i]: %s\r' % (i, device_name)
                            device_found = True
                            break
                        i += 1

                # Default to the Raspberry Pi on-board audio if device in config is not found
                if device_found is not True and gv.IS_DEBIAN:
                    print ">>>> No connected audio devices found. Defaulting to RPi on-board soundcard."
                    i = 0
                    device_name = 'bcm2835'
                    for d in sounddevice.query_devices():
                        if device_name in d['name'] and d['max_output_channels'] > 0:
                            gv.AUDIO_DEVICE_ID = i
                            device_name = d['name']
                            gv.AUDIO_DEVICE_NAME = device_name
                            print '\r>>>>> Default RPi audio device selected: [%i]: %s\r' % (i, device_name)
                            device_found = True
                            break
                        i += 1

        except:
            print "There was an error setting the audio device"
            pass

        self.close_stream()  # close the audio stream in case it's open so we can start a new one

        # if 'bcm2835' in device_name:
        #     self.start_sounddevice_stream('high') # must be high latency for on-board
        #     self.start_alsa_mixer()
        if self.is_alsa_device(device_name):
            latency = 'low'
            if 'bcm2835' in device_name: latency = 'high'
            self.start_sounddevice_stream(latency)
            self.start_alsa_mixer()
        else:
            self.start_sounddevice_stream()
