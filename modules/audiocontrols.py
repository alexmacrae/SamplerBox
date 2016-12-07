import globalvars as gv
from ctypes import *
import ctypes
from os.path import dirname, abspath

class AudioControls:

    def __init__(self):
        if gv.USE_FREEVERB and gv.IS_DEBIAN:
            self.Reverb().setroomsize(60)
            self.Reverb().setdamp(127)
            self.Reverb().setwet(0)
            self.Reverb().setdry(127)
            self.Reverb().setwidth(127)

    def all_notes_off(self):
        gv.playingsounds = []
        gv.playingnotes = {}
        gv.sustainplayingnotes = []
        gv.triggernotes = [128] * 128  # fill with unplayable note


    class MasterVolume:
        def setvolume(self, vel):
            gv.global_volume_percent = int((float(vel) / 127.0) * 100)
            gv.global_volume = (10.0 ** (-12.0 / 20.0)) * (float(vel) / 127.0)
            gv.displayer.disp_change('volume')

    class Chord:
        def change(self, val):
            gv.current_chord = val
            gv.displayer.disp_change(changed_var='chord')

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

            freeverb = cdll.LoadLibrary(sb_dir+'/freeverb/revmodel.so')

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

            def __init__(self):
                pass

            def unichr_multiplier(self, val):
                return int((val / 127.0 * 100) / 100 * (self.hd44780_20x4.LCD_COLS - 1)) + 1

            def setroomsize(self, val):
                self.fvsetroomsize(val/127.0)
                gv.percent_effect = int(val / 127.0 * 100)
                gv.displayer.disp_change(changed_var=['effect', 'roomsize'])

            def setdamp(self, val):
                self.fvsetdamp(val/127.0)
                gv.percent_effect = int(val / 127.0 * 100)
                gv.displayer.disp_change(changed_var=['effect', 'damping'])

            def setwet(self, val):
                # Disable Freeverb @ 0. BUG: slight audio hiccup when it kicks back in. Needs a better solution.
                # if val <= 0:
                #     gv.USE_FREEVERB = False
                # else:
                #     gv.USE_FREEVERB = True
                self.fvsetwet(val/127.0)
                gv.percent_effect = int(val / 127.0 * 100)
                gv.displayer.disp_change(changed_var=['effect', 'wet'])

            def setdry(self, val):
                self.fvsetdry(val/127.0)
                gv.percent_effect = int(val / 127.0 * 100)
                gv.displayer.disp_change(changed_var=['effect', 'dry'])

            def setwidth(self, val):
                self.fvsetwidth(val/127.0)
                gv.percent_effect = int(val / 127.0 * 100)
                gv.displayer.disp_change(changed_var=['effect', 'width'])


