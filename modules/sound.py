
#########################################
# MIXER CLASSES
#########################################
import samplerbox_audio
import struct
import wave
from chunk import Chunk
import numpy
import pyaudio
import sounddevice
#import freeverb
import audiocontrols as ac
import globalvars as gv
import displayer

#########################################
##  SLIGHT MODIFICATION OF PYTHON'S WAVE MODULE
##  TO READ CUE MARKERS & LOOP MARKERS if applicable in mode
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
            raise Error, 'fmt chunk and/or data chunk missing'

    def getmarkers(self):
        return self._cue

    def getloops(self):
        if gv.sample_mode == gv.PLAYLIVE or gv.sample_mode == gv.PLAYLOOP or gv.sample_mode == gv.PLAYLO2X:
            return self._loops



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
            gv.playingsounds.remove(self)
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
        #print 'fname: ' + self.fname + ' note/vel: ' + str(note) + '/' + str(vel) + ' midinote: ' + str(self.midinote) + ' vel: ' + str(self.velocity)
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


#########################################
# AUDIO CALLBACK
#########################################

def AudioCallback(outdata, frame_count, time_info, status):
    rmlist = []
    gv.playingsounds = gv.playingsounds[-gv.MAX_POLYPHONY:]

    b = samplerbox_audio.mixaudiobuffers(gv.playingsounds, rmlist, frame_count,
                                         gv.FADEOUT, gv.FADEOUTLENGTH, gv.SPEED,
                                         gv.PITCHBEND, gv.PITCHSTEPS)

    # if gv.USE_FREEVERB:
    #     b_temp = b
    #     ac.Freeverb().freeverbprocess(b_temp.ctypes.data_as(ac.Freeverb().c_float_p), b.ctypes.data_as(ac.Freeverb().c_float_p), frame_count)

    for e in rmlist:
        try:
            gv.playingsounds.remove(e)
        except:
            pass

    b *= (gv.global_volume * gv.volumeCC)
    outdata[:] = b.reshape(outdata.shape)


    # if gv.USE_TONECONTOL:
    #      b = numpy.array(chain.filter(bb))
    #      b=bb


    if gv.CHANNELS == 4:  # 4 channel playback

        # if backingtrack running: add in the audio
        if gv.BackingRunning:
            BackData = gv.BackWav[gv.BackIndex:gv.BackIndex + 2 * frame_count]
            gv.ClickData = gv.ClickWav[gv.ClickIndex:gv.ClickIndex + 2 * frame_count]
            gv.BackIndex += 2 * frame_count
            gv.ClickIndex += 2 * frame_count
            if len(b) != len(BackData) or len(b) != len(gv.ClickData):
                gv.BackingRunning = False
                gv.BackData = None
                gv.BackIndex = 0
                gv.ClickData = None
                gv.ClickIndex = 0

        if gv.BackingRunning:
            newdata = (gv.backvolume * gv.BackData + b * gv.global_volume)
            gv.Click = gv.ClickData * gv.clickvolume
        else:
            gv.Click = numpy.zeros(frame_count * 2, dtype=numpy.float32)
            newdata = b * gv.global_volume

        # putting streams in 4 channel audio by magic in numpy reshape
        a1 = newdata.reshape(frame_count, 2)
        a2 = gv.Click.reshape(frame_count, 2)
        ch4 = numpy.hstack((a1, a2)).reshape(1, frame_count * 4)

        # mute while loading Sample or BackingTrack, otherwise there could be dirty hick-ups
        # if SampleLoading or (BackLoadingPerc > 0 and BackLoadingPerc < 100):
        #     ch4 *= 0
        return (ch4.astype(numpy.int16).tostring(), pyaudio.paContinue)

    else:  # 2 Channel playback

        # if backingtrack running: add in the audio
        if gv.BackingRunning:
            BackData = gv.BackWav[gv.BackIndex:gv.BackIndex + 2 * frame_count]
            gv.BackIndex += 2 * frame_count
            if len(b) != len(BackData):
                gv.BackingRunning = False
                BackData = None
                BackIndex = 0

        if gv.BackingRunning:
            newdata = (gv.backvolume * gv.BackData + b * gv.global_volume)
        else:
            newdata = b * gv.global_volume

        return (newdata.astype(numpy.int16).tostring(), pyaudio.paContinue)

#########################################
# OPEN AUDIO DEVICE
#########################################

# Using pyaudio only to list device names. sounddevice doesn't seem to have that option
p = pyaudio.PyAudio()
print "Here is a list of audio devices:"
foundByDeviceName = False
dev_name = ''
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    s = ""
    if not foundByDeviceName:
        if i == gv.AUDIO_DEVICE_ID:
            s += " <--- SELECTED BY ID"
            dev_name = dev['name']
        if (gv.AUDIO_DEVICE_NAME in dev['name']):
            gv.AUDIO_DEVICE_ID = i
            s += " <--- SELECTED BY MATCHED NAME (takes precedence)"
            dev_name = dev['name']
            foundByDeviceName = True
        if dev['maxOutputChannels'] > 0:
            print str(i) + ": " + dev['name'] + s
            # if (s != ""):
            #     break
            # else:
            #     continue

# try:
#     stream = p.open(format=pyaudio.paInt16, channels=gv.CHANNELS, rate=gv.SAMPLERATE,
#                     frames_per_buffer=gv.BUFFERSIZE, output=True,
#                     output_device_index=gv.AUDIO_DEVICE_ID, stream_callback=AudioCallback)
# except:
#     print "Sample audio:  Invalid Audio Device ID"
#     exit(1)

    # initFilter()
    # updateFilter(0, 1000.0, 12.0, 1.0)

try:
    sd = sounddevice.OutputStream(device=gv.AUDIO_DEVICE_ID, blocksize=gv.BUFFERSIZE,
                                  samplerate=gv.SAMPLERATE, channels=gv.CHANNELS,
                                  dtype='int16', callback=AudioCallback)
    sd.start()
    print 'Opened audio device #%i' % gv.AUDIO_DEVICE_ID
except:

    displayer.disp_change(error_message="Invalid audiodev")
    print 'Invalid audio device #%i' % gv.AUDIO_DEVICE_ID
    print 'Available devices:'
    print(sounddevice.query_devices())
    exit(1)

if gv.USE_ALSA_MIXER and gv.IS_DEBIAN:
    import alsaaudio
    for i in range(0, 4):
        try:
            amix = alsaaudio.Mixer(cardindex=gv.MIXER_CARD_ID+i,control=gv.MIXER_CONTROL)
            gv.MIXER_CARD_ID+=i    # save the found value
            i=0                 # indicate OK
            print 'Opened Alsamixer: card id "%i", control "%s"' % (gv.MIXER_CARD_ID, gv.MIXER_CONTROL)
            break
        except:
            pass
    if i > 0:
        displayer.disp_change(error_message="Invalid mixerdev")
        print 'Invalid mixer card id "%i" or control "%s"' % (gv.MIXER_CARD_ID, gv.MIXER_CONTROL)
        print 'Available devices (mixer card id is "x" in "(hw:x,y)" of device #%i):' % gv.AUDIO_DEVICE_ID
        print(sounddevice.query_devices())
        exit(1)
    def getvolume():
        vol = amix.getvolume()
        gv.volume = int(vol[0])
    def setvolume(volume):
        amix.setvolume(volume)
    setvolume(gv.volume)
    getvolume()
else:
    def getvolume():
        pass
    def setvolume(volume):
        pass
#
# # EQ
#
# filterTypes = OrderedDict({
#     FilterType.LPButter: 'Low Pass (Flat)',
#     FilterType.LPBrickwall: 'Low Pass (Brickwall)',
#     FilterType.HPButter: 'High Pass (Flat)',
#     FilterType.HPBrickwall: 'High Pass (Brickwall)',
#     FilterType.LShelving: 'Low Shelf',
#     FilterType.HShelving: 'High Shelf',
#     FilterType.Peak: 'Peak'})
#
# # fs = 44100
# fs = 48000
# eps = 0.0000001
#
#
# class Params:
#     TYPE = 1
#     F = 2
#     G = 3
#     Q = 4
#
#
# deffs = [80, 1000, 3000, 5000, 15000]
#
# chain = None
#
#
# def initFilter():
#     global deffs, chain, fs
#
#     chain = FilterChain()
#     chain._filters.append(Filter(FilterType.LShelving, LOW_EQ, 0, 1, enabled=True))
#     # chain._filters.append(Filter(FilterType.HShelving, deffs[4], 0, 1, enabled = True))
#     # chain._filters.append(Filter(FilterType.Peak, deffs[0], 0, 1, enabled = True))
#     chain._filters.append(Filter(FilterType.Peak, HIGH_EQ, 0, 1, enabled=True))
#     # chain._filters.append(Filter(FilterType.LPButter, deffs[3], 0, 1, enabled = True))
#     # chain._filters.append(Filter(FilterType.HPButter, deffs[3], 0, 1, enabled = True))
#     chain.reset()
#
#
# def updateFilter(i, fc, g, Q):
#     global chain
#     global fs
#     oldf = chain._filters[i]
#     type = oldf._type
#     # print oldf._type, oldf._fc, oldf._g, oldf._Q
#
#     # fc_val = fc * 2 / fs
#     # print fc_val, g, Q
#
#     f = Filter(type, fc, g, Q)
#     chain.updateFilt(i, f)
#     # chain.changeFilt(i, type, fc, g, Q)
#     chain.reset()
#
