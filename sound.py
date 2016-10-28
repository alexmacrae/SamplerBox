
#########################################
# MIXER CLASSES
#########################################
import samplerbox_audio
import numpy
import wave
import pyaudio
from chunk import Chunk
import struct
import globalvars as gvars
import freeverb
from filters import FilterType, Filter, FilterChain
from collections import OrderedDict

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
            gvars.playingsounds.remove(self)
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
        gvars.playingsounds.append(snd)
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

BackingRunning = False

def AudioCallback(outdata, frame_count, time_info, status):

    global SampleLoading
    global BackingRunning
    global BackWav, BackIndex, ClickWav, ClickIndex
    global backvolume, clickvolume
    rmlist = []
    gvars.playingsounds = gvars.playingsounds[-gvars.MAX_POLYPHONY:]

    b = samplerbox_audio.mixaudiobuffers(gvars.playingsounds, rmlist, frame_count, gvars.FADEOUT, gvars.FADEOUTLENGTH, gvars.SPEED)

    if gvars.USE_FREEVERB:
        b_temp = b
        freeverb.freeverbprocess(b_temp.ctypes.data_as(freeverb.c_float_p), b.ctypes.data_as(freeverb.c_float_p), frame_count)

    for e in rmlist:
        try:
            gvars.playingsounds.remove(e)
        except:
            pass

    b *= gvars.globalvolume
    #outdata[:] = b.reshape(outdata.shape)


    # if gvars.USE_TONECONTOL:
    #      b = numpy.array(chain.filter(bb))
    #      b=bb


    if gvars.CHANNELS == 4:  # 4 channel playback

        # if backingtrack running: add in the audio
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
            newdata = (backvolume * BackData + b * gvars.globalvolume)
            Click = ClickData * clickvolume
        else:
            Click = numpy.zeros(frame_count * 2, dtype=numpy.float32)
            newdata = b * gvars.globalvolume

        # putting streams in 4 channel audio by magic in numpy reshape
        a1 = newdata.reshape(frame_count, 2)
        a2 = Click.reshape(frame_count, 2)
        ch4 = numpy.hstack((a1, a2)).reshape(1, frame_count * 4)

        # mute while loading Sample or BackingTrack, otherwise there could be dirty hick-ups
        # if SampleLoading or (BackLoadingPerc > 0 and BackLoadingPerc < 100):
        #     ch4 *= 0
        return (ch4.astype(numpy.int16).tostring(), pyaudio.paContinue)

    else:  # 2 Channel playback

        # if backingtrack running: add in the audio
        if BackingRunning:
            BackData = BackWav[BackIndex:BackIndex + 2 * frame_count]
            BackIndex += 2 * frame_count
            if len(b) != len(BackData):
                BackingRunning = False
                BackData = None
                BackIndex = 0

        if BackingRunning:
            newdata = (backvolume * BackData + b * gvars.globalvolume)
        else:
            newdata = b * gvars.globalvolume

        return (newdata.astype(numpy.int16).tostring(), pyaudio.paContinue)



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
