import globalvars as gv
from time import sleep



class SystemFunctions:
    def __init__(self):
        pass


    def restart(self):

        gv.displayer.menu_mode = gv.displayer.DISP_UTILS_MODE
        if gv.USE_HD44780_16x2_LCD:
            gv.displayer.disp_change(str_override='Restarting', line=1, is_priority=True)
            gv.displayer.disp_change(str_override='SamplerBox', line=2, is_priority=True)
        elif gv.USE_HD44780_20x4_LCD:
            gv.displayer.disp_change(str_override='----', line=1, is_priority=True)
            gv.displayer.disp_change(str_override='Restarting', line=2, is_priority=True)
            gv.displayer.disp_change(str_override='SamplerBox', line=3, is_priority=True)
            gv.displayer.disp_change(str_override='----', line=4, is_priority=True)

        sleep(0.15)

        if gv.IS_DEBIAN:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        import os
        # Python calls 2 command line commands in one line: kill all python scripts, and re-run samplerbox.py
        os.system('sudo killall python && sudo python ' + str(os.getcwd()) + '/samplerbox.py')

    def shutdown(self):
        gv.displayer.disp_change(str_override='Good bye!', line=1, timeout=1)
        gv.displayer.disp_change(str_override='Good bye!', line=2, timeout=1)
        gv.displayer.disp_change(str_override='Good bye!', line=3, timeout=1)
        gv.displayer.disp_change(str_override='Good bye!', line=4, timeout=1)
        sleep(0.2)
        if gv.IS_DEBIAN:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
