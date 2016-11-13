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
        gv.global_volume = (10.0 ** (-12.0 / 20.0)) * (float(vel) / 127.0)
        displayer.change('volume')

class Chord:
    def change(self, val):
        gv.currchord = val
        displayer.change(changed_var='chord')

class Voice:

    def change(self, val):
        gv.currvoice = val
        displayer.change(changed_var='voice')

    def voice1(self, vel):
        if vel > 0:
            gv.currvoice = 1
            displayer.change(changed_var='voice')

    def voice2(self, vel):
        if vel > 0:
            gv.currvoice = 2
            displayer.change(changed_var='voice')

    def voice3(self, vel):
        if vel > 0:
            gv.currvoice = 3
            displayer.change(changed_var='voice')

    def voice4(self, vel):
        if vel > 0:
            gv.currvoice = 4
            displayer.change(changed_var='voice')

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