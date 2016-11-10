##################################################################################
# link for freeverb C++ lib
##################################################################################
import globalvars as gv

if gv.USE_FREEVERB:
    import ctypes
    from ctypes import *
    import lcd
    freeverb = cdll.LoadLibrary('./freeverb/revmodel.so')

    def unichr_multiplier(val):
        return int((val / 127.0 * 100)/100 * (lcd.LCD_COLS-1)) + 1

    fvsetroomsize = freeverb.setroomsize
    fvsetroomsize.argtypes = [c_float]
    fvgetroomsize = freeverb.getroomsize
    fvgetroomsize.restype = c_float
    def setroomsize(val):
        fvsetroomsize(val/127.0)
        lcd.display('Roomsize', 3)
        lcd.display(unichr(1) * unichr_multiplier(val) , 4)

    fvsetdamp = freeverb.setdamp
    fvsetdamp.argtypes = [c_float]
    fvgetdamp = freeverb.getdamp
    fvgetdamp.restype = c_float
    def setdamp(val):
        fvsetdamp(val/127.0)
        lcd.display('Damping', 3)
        lcd.display(unichr(1) * unichr_multiplier(val), 4)

    fvsetwet = freeverb.setwet
    fvsetwet.argtypes = [c_float]
    fvgetwet = freeverb.getwet
    fvgetwet.restype = c_float
    def setwet(val):
        fvsetwet(val/127.0)
        lcd.display('Wet', 3)
        lcd.display(unichr(1) * unichr_multiplier(val), 4)

    fvsetdry = freeverb.setdry
    fvsetdry.argtypes = [c_float]
    fvgetdry = freeverb.getdry
    fvgetdry.restype = c_float
    def setdry(val):
        fvsetdry(val/127.0)
        lcd.display('Dry', 3)
        lcd.display(unichr(1) * unichr_multiplier(val), 4)

    fvsetwidth = freeverb.setwidth
    fvsetwidth.argtypes = [c_float]
    fvgetwidth = freeverb.getwidth
    fvgetwidth.restype = c_float
    def setwidth(val):
        fvsetwidth(val/127.0)
        lcd.display('Width', 3)
        lcd.display(unichr(1) * unichr_multiplier(val), 4)


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

    setroomsize(60)
    setdamp(127)
    setwet(0)
    setdry(127)
    setwidth(127)