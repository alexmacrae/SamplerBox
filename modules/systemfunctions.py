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
        # os.system('sudo killall python && sudo python ' + str(os.getcwd()) + '/samplerbox.py')
        os.system('systemctl stop samplerbox && sudo python ' + str(os.getcwd()) + '/samplerbox.py')

    def shutdown(self, log_file=None):
        gv.nav.text_scroller.stop()
        shutdown_message = 'GOOD BYE!'.center(gv.LCD_COLS, ' ')
        for i in xrange(gv.LCD_ROWS):
            gv.displayer.disp_change(str_override=shutdown_message, line=(i+1), timeout=1, is_priority=True)
        sleep(0.2)
        gv.sound.close_stream()

        if log_file:
            log_file.close()

        if gv.IS_DEBIAN:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
