
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
        self.mode = mode
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
    #print "sounds: " +str(len(playingsounds)) + " notes: " + str(len(playingnotes)) + " sust: " + str(len(sustainplayingnotes))
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

    # b *= gvars.globalvolume
    # outdata[:] = b.reshape(outdata.shape)


    # if USE_TONECONTOL
    # 	b = numpy.array(chain.filter(bb))
    # 	b=bb


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


