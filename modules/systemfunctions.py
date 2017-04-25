import globalvars as gv
import time
import os

def mount_samples_rw():
    if gv.SAMPLES_DIR == '/samples': os.system('mount -o remount,rw /samples')
    print '/samples has been remounted as READ-WRITE'

def mount_samples_ro():
    if gv.SAMPLES_DIR == '/samples': os.system('mount -o remount,ro /samples')
    print '/samples has been remounted as READ-ONLY'

def mount_boot_rw():
    if gv.CONFIG_FILE_PATH == "/boot/samplerbox/config.ini": os.system('mount -o remount,rw /boot')
    print '/boot has been remounted as READ-WRITE'

def mount_boot_ro():
    if gv.CONFIG_FILE_PATH == "/boot/samplerbox/config.ini": os.system('mount -o remount,ro /boot')
    print '/boot has been remounted as READ-ONLY'

def mount_root_rw():
    os.system('mount -o remount,rw /')
    print '/ has been remounted as READ-WRITE'

def mount_root_ro():
    os.system('mount -o remount,ro /')
    print '/ has been remounted as READ-ONLY'

class SystemFunctions:
    def __init__(self):
        pass

    def restart(self):

        # Restart the script

        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE

        if gv.USE_HD44780_16x2_LCD:
            gv.displayer.disp_change(str_override='Restarting', line=1, is_priority=True)
            gv.displayer.disp_change(str_override='SamplerBox', line=2, is_priority=True)
        elif gv.USE_HD44780_20x4_LCD:
            gv.displayer.disp_change(str_override=' ', line=1, is_priority=True)
            gv.displayer.disp_change(str_override='Restarting', line=2, is_priority=True)
            gv.displayer.disp_change(str_override='SamplerBox', line=3, is_priority=True)
            gv.displayer.disp_change(str_override=' ', line=4, is_priority=True)

        time.sleep(0.1)

        if gv.IS_DEBIAN:
            import RPi.GPIO as GPIO
            GPIO.cleanup()

        # Python calls 2 command line commands in one line: kill all python scripts, and re-run samplerbox.py
        # os.system('sudo killall python && sudo python ' + str(os.getcwd()) + '/samplerbox.py')
        os.system('systemctl stop samplerbox')
        os.system('killall python && python ' + str(os.getcwd()) + '/samplerbox.py')

    def reboot(self):

        # Reboot Raspberry Pi

        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE

        if gv.USE_HD44780_16x2_LCD:
            gv.displayer.disp_change(str_override='Rebooting', line=1, is_priority=True)
            gv.displayer.disp_change(str_override='System', line=2, is_priority=True)
        elif gv.USE_HD44780_20x4_LCD:
            gv.displayer.disp_change(str_override=' ', line=1, is_priority=True)
            gv.displayer.disp_change(str_override='Rebooting', line=2, is_priority=True)
            gv.displayer.disp_change(str_override='System', line=3, is_priority=True)
            gv.displayer.disp_change(str_override=' ', line=4, is_priority=True)

        time.sleep(0.1)

        if gv.IS_DEBIAN:
            import RPi.GPIO as GPIO
            GPIO.cleanup()

        os.system('reboot')

    def shutdown(self, log_file=None):

        gv.displayer.menu_mode = gv.displayer.DISP_PRESET_MODE

        if gv.SYSTEM_MODE == 1: gv.nav.text_scroller.stop()  # stop the text scroller in SYS MODE 1
        shutdown_message = 'GOOD BYE!'.center(gv.LCD_COLS, ' ')
        for i in xrange(gv.LCD_ROWS):
            gv.displayer.disp_change(str_override=shutdown_message, line=(i + 1), timeout=1, is_priority=True)

        time.sleep(0.1)
        gv.sound.close_stream()

        if log_file:
            log_file.close()

        if gv.IS_DEBIAN:
            import RPi.GPIO as GPIO
            GPIO.cleanup()

        exit()
