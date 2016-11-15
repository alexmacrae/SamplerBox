''' Displayer formatter
The purpose of this module is to format and route display messages from
elsewhere in the script into the format of the current SYSTEM_MODE
and physical display module(LCD_44780_20x16, 16x2, 7Segment display)

When gv.displayer.disp_change is called:
changed_var - str or list.
str_override - Write over a line with a custom string. eg when SampleBox is stopped display STOPPED.
line - the LCD line to be displayed on. Not applicable for 7 segment display.
'''

import globalvars as gv
import time
import psutil
from os.path import exists

DISP_PRESET_MODE = 'preset'
DISP_UTILS_MODE = 'utils'
DISP_MENU_MODE = 'menu'

tempDisplay = False

MENU_MODES = [DISP_PRESET_MODE, DISP_UTILS_MODE, DISP_MENU_MODE]
menu_mode = DISP_PRESET_MODE

prev_global_volume = gv.global_volume
prev_percent_loaded = gv.percent_loaded


class Displayer:
    LCD_SYS = None
    if gv.SYSTEM_MODE == 1:
        import HD44780_sys_1
        LCD_SYS = HD44780_sys_1
    elif gv.SYSTEM_MODE == 2:
        import HD44780_sys_2
        LCD_SYS = HD44780_sys_2

    def disp_change(self, changed_var=[], str_override='', line=1, timeout=0):
        # if changed_var was a string, convert to a list.
        if isinstance(changed_var, str): changed_var = [changed_var]

        if gv.USE_I2C_7SEGMENTDISPLAY:

            ###################
            # 7 SEGMENT DISPLAY
            ###################
            if gv.USE_I2C_7SEGMENTDISPLAY and gv.IS_DEBIAN:
                import i2c7segment
                if 'preset' in changed_var:
                    d = list('----')
                    p = list(str(gv.preset))
                    for i in xrange(len(p)):
                        d[i] = p[i]
                    d = ''.join(d)
                    if gv.PRINT_LCD_MESSAGES:
                        print d
                    i2c7segment.display(d)

        else:

            #######################
            # SYSTEM MODE 1 by Alex
            #######################

            if gv.SYSTEM_MODE == 1:

                if gv.USE_HD44780_16x2_LCD:

                    # No logic for 16x2 display just yet
                    pass
                elif gv.USE_HD44780_20x4_LCD:

                    if menu_mode == DISP_PRESET_MODE:

                        if 'preset' in changed_var:

                            p = gv.preset
                            self.LCD_SYS.display(str(p - gv.PRESET_BASE + 1) + unichr(2) + gv.SETLIST_LIST[p], 1,
                                                 is_priority=True, timeout_custom=timeout)
                            if p < gv.NUM_FOLDERS-1:
                                p += 1
                            else:
                                p = 0

                            self.LCD_SYS.display(str(p - gv.PRESET_BASE + 1) + unichr(2) + gv.SETLIST_LIST[p], 2,
                                                 is_priority=True, timeout_custom=timeout)
                            self.LCD_SYS.display('', 3, is_priority=True, timeout_custom=timeout)
                            self.LCD_SYS.display('', 4, is_priority=True, timeout_custom=timeout)
                        # temp overrides / non-priority messages
                        if 'volume' in changed_var:
                            i = int(gv.global_volume_percent / 100.0 * (gv.LCD_COLS - 1)) + 1
                            self.LCD_SYS.display('Volume', 3, is_priority=False, timeout_custom=2)
                            self.LCD_SYS.display((unichr(1) * i), 4, is_priority=False, timeout_custom=2)
                        elif 'loading' in changed_var:
                            self.LCD_SYS.display('Loading...', 3, is_priority=False, timeout_custom=timeout)
                            self.LCD_SYS.display(unichr(1) * int(gv.percent_loaded * (gv.LCD_COLS / 100.0) + 1),
                                                 4, is_priority=False, timeout_custom=timeout)
                        elif 'effect' in changed_var:
                            self.LCD_SYS.display(changed_var[1], 3, is_priority=False, timeout_custom=2)
                            self.LCD_SYS.display(unichr(1) * int(gv.percent_effect * (gv.LCD_COLS / 100.0) + 1),
                                                 4, is_priority=False, timeout_custom=2)
                        elif 'voice' in changed_var:
                            self.LCD_SYS.display('', timeout_custom=0)


                    if menu_mode == DISP_UTILS_MODE:
                        if 'util' in changed_var:
                            self.LCD_SYS.display_called = True

                            SD_usage_percent = int(psutil.disk_usage('/').__getattribute__('percent') / (gv.LCD_COLS - 4)) + 1
                            cpu = int(psutil.cpu_percent(None) / (gv.LCD_COLS - 4)) + 1
                            ram = int(float(psutil.virtual_memory().percent) / (gv.LCD_COLS - 4)) + 1

                            disk_usage_str = 'DSK'+(unichr(1) * SD_usage_percent)
                            cpu_str = 'CPU' + (unichr(1) * cpu)
                            ram_str = 'RAM' + (unichr(1) * ram)
                            self.LCD_SYS.display('SYSTEM MONITOR'.center(gv.LCD_COLS, ' '), line=1, is_priority=False,
                                                 timeout_custom=timeout)
                            self.LCD_SYS.display(disk_usage_str, line=2, is_priority=False, timeout_custom=timeout)
                            self.LCD_SYS.display(cpu_str, line=3, is_priority=False, timeout_custom=timeout)
                            self.LCD_SYS.display(ram_str, line=4, is_priority=False, timeout_custom=timeout)

                    if menu_mode == DISP_MENU_MODE:
                        self.LCD_SYS.display(changed_var[0], line=line, is_priority=True, timeout_custom=timeout)

                    if str_override:
                        self.LCD_SYS.display_called = True
                        self.LCD_SYS.display(str_override.center(gv.LCD_COLS, ' '), line=line, is_priority=False,
                                             timeout_custom=timeout)

            #######################
            # SYSTEM MODE 2 by Hans
            #######################

            # Currently the 20x4 module displays the same messages as the 16x2 - ie only on the first 2 lines

            elif gv.SYSTEM_MODE == 2:
                if gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD:

                    if 'loading' in changed_var:
                        self.LCD_SYS.display(unichr(1) * int(gv.percent_loaded * (gv.LCD_COLS / 100.0) + 1))
                    elif 'voice' in changed_var:
                        self.LCD_SYS.display()
                    elif str_override:
                        self.LCD_SYS.display(str_override)
                    else:
                        self.LCD_SYS.display('')
