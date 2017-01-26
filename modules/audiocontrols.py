import globalvars as gv
from ctypes import *
import ctypes
from os.path import dirname, abspath
from filters import FilterType, Filter, FilterChain
from collections import OrderedDict
import sys


class AudioControls(object):
    def __init__(self):

        self.master_volume = MasterVolume()
        self.autochorder = AutoChorder()
        self.sustain = Sustain()
        self.pitchbend = PitchBend()
        self.voice = Voice()
        if gv.USE_FREEVERB and gv.IS_DEBIAN:
            self.reverb = Reverb(60, 127, 0, 127, 127)
        if gv.USE_TONECONTROL:
            self.tone_control = ToneControl()

    def all_notes_off(self):
        gv.playingsounds = []
        gv.playingnotes = {}
        gv.sustainplayingnotes = []
        gv.triggernotes = {}

        for channel in xrange(16):
            gv.triggernotes[channel + 1] = [128] * 128  # fill with unplayable note
            gv.playingnotes[channel +1 ] = {}



class MasterVolume:
    def setvolume(self, vel):
        gv.global_volume_percent = int((float(vel) / 127.0) * 100)
        gv.global_volume = (10.0 ** (-12.0 / 20.0)) * (float(vel) / 127.0)
        gv.displayer.disp_change('volume')

########################
# Auto Chorder by Hans #
#  Additions by Alex   #
########################

class AutoChorder(object):


    CHORD_NAMES = ["", "Maj", "Min", "Augm", "Dim", "Sus2", "Sus4", "Dom7",
                   "Maj7", "Min7", "MiMa7", "hDim7", "Dim7", "Aug7", "AuMa7", "D7S4"]
    CHORD_NOTES = [[0], [0, 4, 7], [0, 3, 7], [0, 4, 8], [0, 3, 6], [0, 2, 7],
                   [0, 5, 7], [0, 4, 7, 10], [0, 4, 7, 11], [0, 3, 7, 10],
                   [0, 3, 7, 11], [0, 3, 6, 10], [0, 3, 6, 9], [0, 4, 8, 10],
                   [0, 4, 8, 11], [0, 5, 7, 10]]

    NO_CHORD = [0] * 12
    ALL_MAJOR_CHORDS = [1] * 12
    ALL_MINOR_CHORDS = [2] * 12
    MAJOR_SCALE_CHORDS = [1, 4, 2, 4, 2, 1, 4, 1, 4, 2, 4, 4]
    MINOR_SCALE_CHORDS = [2, 4, 2, 1, 4, 2, 4, 2, 1, 4, 1, 4]

    AVAILABLE_CHORDS_SETS = [
        ('Chords OFF', NO_CHORD),
        ('MAJ scale chords', MAJOR_SCALE_CHORDS),
        ('MIN scale chords', MINOR_SCALE_CHORDS),
        ('All MAJ chords', ALL_MAJOR_CHORDS),
        ('All MIN chords', ALL_MINOR_CHORDS)
    ]

    def __init__(self):
        self.chord_set_index = 0
        self.current_chord_mode = self.AVAILABLE_CHORDS_SETS[self.chord_set_index][1]
        self.current_chord = 0  # single note, "normal play"
        self.current_key_index = 0

    def change_mode(self, mode):
        self.current_chord_mode = self.AVAILABLE_CHORDS_SETS[mode][1]

    def change_key(self, key):
        self.current_key_index = key


class Voice:
    def change(self, val):
        gv.currvoice = val
        gv.displayer.disp_change(changed_var='voice')

    def voice1(self, vel):
        if vel > 0:
            gv.currvoice = 1
            gv.displayer.disp_change(changed_var='voice')

    def voice2(self, vel):
        if vel > 0:
            gv.currvoice = 2
            gv.displayer.disp_change(changed_var='voice')

    def voice3(self, vel):
        if vel > 0:
            gv.currvoice = 3
            gv.displayer.disp_change(changed_var='voice')

    def voice4(self, vel):
        if vel > 0:
            gv.currvoice = 4
            gv.displayer.disp_change(changed_var='voice')

    def up(self, vel):
        if vel > 0:
            if gv.currvoice <= 4:
                gv.currvoice += 1
            else:
                gv.currvoice = 1

    def down(self, vel):
        if vel > 0:
            if gv.currvoice > 0:
                gv.currvoice += 1
            else:
                gv.currvoice = 4


class Reverb:
    if gv.USE_FREEVERB and gv.IS_DEBIAN:
        sb_dir = dirname(dirname(abspath(__file__)))

        freeverb = cdll.LoadLibrary(sb_dir + '/freeverb/revmodel.so')

        fvsetroomsize = freeverb.setroomsize
        fvsetroomsize.argtypes = [c_float]
        fvgetroomsize = freeverb.getroomsize
        fvgetroomsize.restype = c_float
        fvsetdamp = freeverb.setdamp
        fvsetdamp.argtypes = [c_float]
        fvgetdamp = freeverb.getdamp
        fvgetdamp.restype = c_float
        fvsetwet = freeverb.setwet
        fvsetwet.argtypes = [c_float]
        fvgetwet = freeverb.getwet
        fvgetwet.restype = c_float
        fvsetdry = freeverb.setdry
        fvsetdry.argtypes = [c_float]
        fvgetdry = freeverb.getdry
        fvgetdry.restype = c_float
        fvsetwidth = freeverb.setwidth
        fvsetwidth.argtypes = [c_float]
        fvgetwidth = freeverb.getwidth
        fvgetwidth.restype = c_float
        fvsetmode = freeverb.setmode
        fvsetmode.argtypes = [c_float]
        fvgetmode = freeverb.getmode
        fvgetmode.restype = c_float
        c_float_p = ctypes.POINTER(ctypes.c_float)
        c_short_p = ctypes.POINTER(ctypes.c_short)
        freeverbprocess = freeverb.process
        freeverbprocess.argtypes = [c_float_p, c_float_p, c_int]
        # not used:
        freeverbmix = freeverb.mix
        freeverbmix.argtypes = [c_short_p, c_float_p, c_float, c_int]
        freeverbmixback = freeverb.mixback
        freeverbmixback.argtypes = [c_float_p, c_float_p, c_float, c_short_p, c_float, c_short_p, c_float, c_int]

        def __init__(self, roomsize, damp, wet, dry, width):
            self.setroomsize(roomsize)
            self.setdamp(damp)
            self.setwet(wet)
            self.setdry(dry)
            self.setwidth(width)

        def unichr_multiplier(self, val):
            return int((val / 127.0 * 100) / 100 * (gv.LCD_COLS - 1)) + 1

        def setroomsize(self, val):
            self.fvsetroomsize(val / 127.0)
            gv.percent_effect = int(val / 127.0 * 100)
            gv.displayer.disp_change(changed_var=['effect', 'roomsize'])

        def setdamp(self, val):
            self.fvsetdamp(val / 127.0)
            gv.percent_effect = int(val / 127.0 * 100)
            gv.displayer.disp_change(changed_var=['effect', 'damping'])

        def setwet(self, val):
            # Disable Freeverb @ 0. BUG: slight audio hiccup when it kicks back in. Needs a better solution.
            # if val <= 0:
            #     gv.USE_FREEVERB = False
            # else:
            #     gv.USE_FREEVERB = True
            self.fvsetwet(val / 127.0)
            gv.percent_effect = int(val / 127.0 * 100)
            gv.displayer.disp_change(changed_var=['effect', 'wet'])

        def setdry(self, val):
            self.fvsetdry(val / 127.0)
            gv.percent_effect = int(val / 127.0 * 100)
            gv.displayer.disp_change(changed_var=['effect', 'dry'])

        def setwidth(self, val):
            self.fvsetwidth(val / 127.0)
            gv.percent_effect = int(val / 127.0 * 100)
            gv.displayer.disp_change(changed_var=['effect', 'width'])


class PitchBend:

    def set_pitch(self, vel, note):
        gv.PITCHBEND = (((128 * vel + note) / gv.pitchdiv) - gv.pitchneutral) * (gv.pitchnotes * 2)

class Sustain:
    def set_sustain(self, message, src, messagetype):
        CCnum = message[1]
        CCval = message[2]
        # NB: the microKEY conditionals are unique to Alex's modded keyboard. Remove in future.
        if gv.sample_mode == gv.PLAYLIVE:
            if (CCval < 64) \
                    or (("microKEY" in src)
                        and (messagetype == 14)
                        and (CCnum == 64 or CCnum == 0)
                        and (CCval >= 28)) \
                            and (gv.sustain == True):  # sustain pedal off
                for n in gv.sustainplayingnotes:
                    n.fadeout(50)
                gv.sustainplayingnotes = []
                gv.sustain = False
            elif (CCval >= 64) \
                    or (("microKEY" in src)
                        and (messagetype == 14)
                        and (CCnum == 64 or CCnum == 0)
                        and (CCval <= 25)) \
                            and (gv.sustain == False):  # sustain pedal on
                gv.sustain = True


###################
# TONE CONTROL
# by Erik
###################

class ToneControl:
    LOW_EQ_FREQ = 80.0
    HIGH_EQ_FREQ = 8000.0
    HIGH_EQ = (2 * HIGH_EQ_FREQ) / gv.SAMPLERATE
    LOW_EQ = (2 * LOW_EQ_FREQ) / gv.SAMPLERATE

    filterTypes = OrderedDict({
        FilterType.LPButter: 'Low Pass (Flat)',
        FilterType.LPBrickwall: 'Low Pass (Brickwall)',
        FilterType.HPButter: 'High Pass (Flat)',
        FilterType.HPBrickwall: 'High Pass (Brickwall)',
        FilterType.LShelving: 'Low Shelf',
        FilterType.HShelving: 'High Shelf',
        FilterType.Peak: 'Peak'})

    eps = 0.0000001
    TYPE = 1
    F = 2
    G = 3
    Q = 4
    deffs = [80, 1000, 3000, 5000, 15000]

    def __init__(self):
        self.chain = None
        self.initFilter()

    def initFilter(self):
        self.chain = FilterChain()
        self.chain._filters.append(Filter(FilterType.LShelving, self.LOW_EQ, 0, 1, enabled=True))
        # self.chain._filters.append(Filter(FilterType.HShelving, deffs[4], 0, 1, enabled = True))
        # self.chain._filters.append(Filter(FilterType.Peak, deffs[0], 0, 1, enabled = True))
        self.chain._filters.append(Filter(FilterType.Peak, self.HIGH_EQ, 0, 1, enabled=True))
        # self.chain._filters.append(Filter(FilterType.LPButter, deffs[3], 0, 1, enabled = True))
        # self.chain._filters.append(Filter(FilterType.HPButter, deffs[3], 0, 1, enabled = True))
        self.chain.reset()

    def updateFilter(self, i, fc, g, Q):
        oldf = self.chain._filters[i]
        type = oldf._type
        # print oldf._type, oldf._fc, oldf._g, oldf._Q

        # fc_val = fc * 2 / fs
        # print fc_val, g, Q

        f = Filter(type, fc, g, Q)
        self.chain.updateFilt(i, f)
        # chain.changeFilt(i, type, fc, g, Q)
        self.chain.reset()
