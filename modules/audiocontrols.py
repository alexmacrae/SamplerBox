import displayer
import globalvars as gv
if gv.USE_FREEVERB: import freeverb

class Reverb:
    def roomsize(self, vel):
        freeverb.setroomsize(vel)

    def damping(self, vel):
        freeverb.setdamp(vel)

    def wet(self, vel):
        freeverb.setwet(vel)

    def dry(self, vel):
        freeverb.setdry(vel)

    def width(self, vel):
        freeverb.setwidth(vel)

class MasterVolume:
    def setvolume(self, vel):
        # i = int(float(vel / 127.0) * (hd44780_20x4.LCD_COLS - 1)) + 1
        # hd44780_20x4.display('Volume', 3)
        # hd44780_20x4.display((unichr(1) * i), 4)
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



if gv.USE_FREEVERB:

    from ctypes import *
    import ctypes

    class Freeverb:

        freeverb = cdll.LoadLibrary('./freeverb/revmodel.so')
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
            self.setroomsize(60)
            self.setdamp(127)
            self.setwet(0)
            self.setdry(127)
            self.setwidth(127)

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


