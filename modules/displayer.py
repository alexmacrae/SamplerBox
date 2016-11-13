''' Displayer formatter
The purpose of this module is to format and route display messages from
elsewhere in the script into the format of the current SYSTEM_MODE
and physical display module(LCD_44780_20x16, 16x2, 7Segment display)
'''

import globalvars as gv
import hd44780_16x2
import hd44780_20x4

DISP_PRESET_MODE = 'preset'
DISP_UTILS_MODE = 'utils'
DISP_MENU_MODE = 'menu'

tempDisplay = False

MENU_MODES = [DISP_PRESET_MODE, DISP_UTILS_MODE, DISP_MENU_MODE]
menu_mode = DISP_PRESET_MODE

displayCalled = False

prev_global_volume = gv.global_volume
prev_percent_loaded = gv.percent_loaded

''' When displayer.change is called
changed_var - str or list.
str_override - Write over a line with a custom string. eg when SampleBox is stopped display STOPPED.
error_message - Same as str_override.
line - the LCD line to be displayed on. Not applicable for 7 segment display.
'''
def change(changed_var=[], str_override=None, error_message=None, line=1):

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
                        curr_preset_name = gv.SETLIST_LIST[p]
                        hd44780_20x4.display(str(p + gv.PRESET_BASE) + unichr(2) + curr_preset_name, 1, is_priority=True)

                        if p < gv.NUM_FOLDERS - 1:
                            p += 1
                        else:
                            p = 0
                        next_preset_name = gv.SETLIST_LIST[p]
                        hd44780_20x4.display(str(p + gv.PRESET_BASE + 1) + unichr(2) + next_preset_name, 2,
                                             is_priority=True)
                    # temp overrides / non-priority messages
                    if 'volume' in changed_var:
                        i = int(float(gv.global_volume / 100.0) * (hd44780_20x4.LCD_COLS - 1)) + 1
                        hd44780_20x4.display('Volume', 3, is_priority=False)
                        hd44780_20x4.display((unichr(1) * i), 4, is_priority=False)
                    elif 'loading' in changed_var:
                        hd44780_20x4.display('Loading...', 3, is_priority=False)
                        hd44780_20x4.display(unichr(1) * int(gv.percent_loaded * (hd44780_20x4.LCD_COLS / 100.0) + 1), 4,
                                             is_priority=False)
                elif menu_mode == DISP_UTILS_MODE:
                    hd44780_20x4.TimeOut = hd44780_20x4.TimeOutReset
                    hd44780_20x4.resetModes()
                    hd44780_20x4.inSysMode = True

                if str_override:
                    hd44780_20x4.display(str_override, line, is_priority=False)
                if error_message:
                    hd44780_20x4.display(str_override, line, is_priority=False)


        #######################
        # SYSTEM MODE 2 by Hans
        #######################

        elif gv.SYSTEM_MODE == 2:

            if gv.USE_HD44780_16x2_LCD:
                if 'loading' in changed_var:
                    hd44780_16x2.display(unichr(1) * int(gv.percent_loaded * (16 / 100.0) + 1))
                if 'voice' in changed_var:
                    hd44780_16x2.display()
                elif str_override:
                    hd44780_16x2.display(str_override)
                else:
                    hd44780_16x2.display('')


            elif gv.USE_HD44780_20x4_LCD:
                # No logic for 20x4 display just yet
                pass

