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
import psutil
import os


class Displayer:

    def __init__(self):

        self.DISP_PRESET_MODE = 'preset'
        self.DISP_UTILS_MODE = 'utils'
        self.DISP_MENU_MODE = 'menu'

        self.tempDisplay = False

        self.MENU_MODES = [self.DISP_PRESET_MODE, self.DISP_UTILS_MODE, self.DISP_MENU_MODE]
        self.menu_mode = self.DISP_PRESET_MODE

        self.prev_global_volume = gv.global_volume
        self.prev_percent_loaded = gv.percent_loaded

        self.LCD_SYS = None

        self.voices_display_blocks = True

        if gv.SYSTEM_MODE == 1:
            from modules import HD44780_sys_1
            from modules import navigator_sys_1
            self.LCD_SYS = HD44780_sys_1.LCD_SYS_1()
            gv.nav = navigator_sys_1.Navigator(navigator_sys_1.PresetNav)
        elif gv.SYSTEM_MODE == 2:
            from modules import HD44780_sys_2
            from modules import navigator_sys_2
            self.LCD_SYS = HD44780_sys_2.LCD_SYS_2()
            gv.nav = navigator_sys_2



    def display_preset_with_voices(self, preset_string):
        preset_string = preset_string + ' ' * gv.LCD_COLS  # fill with space chars
        preset_string_list = list(preset_string[:gv.LCD_COLS])  # limit to width of LCD's chars/columns
        v_len = len(gv.voices)
        if v_len > 1:
            if self.voices_display_blocks:
                buttons = list(unichr(5) * v_len)  # fill with custom block chars
                buttons[gv.currvoice - 1] = unichr(1)
                buttons.insert(0, ' ')  # add a space before the voices section
                for i in xrange(v_len + 1):
                    str_index = (v_len + 1) - i
                    preset_string_list[-str_index] = buttons[i]
            else:
                v_str = ' v%d:%d' % (gv.currvoice, v_len)
                preset_string_list[-5] = v_str
        return ''.join(preset_string_list)

    def disp_change(self, changed_var=[], str_override='', line=1, is_priority=False, timeout=0):
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
                    gv.preset = list(str(gv.preset))
                    for i in xrange(len(gv.preset)):
                        d[i] = gv.preset[i]
                    d = ''.join(d)
                    if gv.PRINT_LCD_MESSAGES:
                        print d
                    i2c7segment.display(d)

        else:

            #########################
            # SYSTEM MODE 1 by Alex #
            #########################

            if gv.SYSTEM_MODE == 1:

                if gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD:

                    # Determine whether to push some lines (eg loading bars) down 2 rows if using 20x4 display
                    n = 2 if gv.USE_HD44780_20x4_LCD else 0

                    if self.menu_mode == self.DISP_PRESET_MODE:

                        if str_override:
                            self.LCD_SYS.display_called = True
                            self.LCD_SYS.display(str_override.center(gv.LCD_COLS, ' '), line=line,
                                                 is_priority=is_priority,
                                                 timeout_custom=timeout)
                            return

                        if 'preset' in changed_var or 'voice' in changed_var:

                            preset_name = gv.SETLIST_LIST[gv.samples_indices[gv.preset]]
                            preset_num_name = str(gv.preset - gv.PRESET_BASE + 1) + ' ' + preset_name
                            preset_line_1 = preset_num_name

                            self.LCD_SYS.display(preset_line_1, line=1, is_priority=True, timeout_custom=timeout)

                            next_preset = gv.preset
                            if gv.preset < len(gv.SETLIST_LIST) - 1:
                                next_preset += 1
                            else:
                                next_preset = 0

                            preset_name = gv.SETLIST_LIST[gv.samples_indices[next_preset]]
                            preset_num_name = str(next_preset - gv.PRESET_BASE + 1) + ' ' + preset_name
                            preset_line_2 = self.display_preset_with_voices(preset_num_name)

                            self.LCD_SYS.display(preset_line_2, line=2, is_priority=True, timeout_custom=timeout)
                            self.LCD_SYS.display('', 3, is_priority=True, timeout_custom=timeout)
                            self.LCD_SYS.display('', 4, is_priority=True, timeout_custom=timeout)

                            # temp overrides / non-priority messages

                        if 'volume' in changed_var:
                            i = int(gv.global_volume_percent / 100.0 * (gv.LCD_COLS - 1)) + 1
                            vol_line = 'Volume'.upper().center(gv.LCD_COLS, ' ')
                            self.LCD_SYS.display(vol_line, line=1 + n, is_priority=False, timeout_custom=timeout)
                            self.LCD_SYS.display((unichr(1) * i), line=2 + n, is_priority=False, timeout_custom=timeout)
                        elif 'loading' in changed_var:
                            loading_line = 'Loading'.upper().center(gv.LCD_COLS, ' ')
                            self.LCD_SYS.display(loading_line, line=1 + n, is_priority=False, timeout_custom=timeout)
                            self.LCD_SYS.display(unichr(1) * int(gv.percent_loaded * (gv.LCD_COLS / 100.0) + 1),
                                                 line=2 + n, is_priority=False, timeout_custom=timeout)
                        elif 'effect' in changed_var:
                            effect_line = changed_var[1].upper().center(gv.LCD_COLS, ' ')
                            self.LCD_SYS.display(effect_line, line=1 + n, is_priority=False, timeout_custom=2)
                            self.LCD_SYS.display(unichr(1) * int(gv.percent_effect * (gv.LCD_COLS / 100.0) + 1),
                                                 line=1 + n, is_priority=False, timeout_custom=2)

                    if self.menu_mode == self.DISP_UTILS_MODE:
                        if 'util' in changed_var:
                            self.LCD_SYS.display_called = True

                            SD_usage_percent = int(psutil.disk_usage('/')
                                                   .__getattribute__('percent') / (gv.LCD_COLS / 2 - 4)) + 1
                            cpu = int(psutil.cpu_percent(None) / (gv.LCD_COLS / 2 - 4)) + 1
                            ram = int(float(psutil.virtual_memory().percent) / (gv.LCD_COLS / 2 - 4)) + 1
                            temp = float(os.popen('vcgencmd measure_temp')
                                         .readline().replace('temp=', '').replace("'C\n", ''))

                            disk_usage_str = 'DSK' + (unichr(1) * SD_usage_percent)
                            cpu_str = 'CPU' + (unichr(1) * cpu)
                            ram_str = 'RAM' + (unichr(1) * ram)
                            if gv.USE_HD44780_16x2_LCD:
                                temp_str = ' ' + str(temp)
                            elif gv.USE_HD44780_20x4_LCD:
                                temp_str = 'TEMP ' + str(temp)

                            self.LCD_SYS.display('SYSTEM MONITOR'.center(gv.LCD_COLS, ' '), line=1, is_priority=False,
                                                 timeout_custom=timeout)
                            self.LCD_SYS.display(disk_usage_str, line=2, is_priority=False, timeout_custom=timeout)
                            line_4_str = cpu_str + ' ' * (gv.LCD_COLS / 2 - len(cpu_str)) + temp_str
                            self.LCD_SYS.display(line_4_str, line=3, is_priority=False, timeout_custom=timeout)
                            self.LCD_SYS.display(ram_str, line=4, is_priority=False, timeout_custom=timeout)

                    if self.menu_mode == self.DISP_MENU_MODE:
                        # Don't attempt to display any volume, loading, effect or voice messages in menu mode
                        if 'volume' in changed_var or 'loading' in changed_var or 'effect' in changed_var or 'voice' in changed_var:
                            return
                        self.LCD_SYS.display(changed_var[0], line=line, is_priority=True, timeout_custom=timeout)



            #######################
            # SYSTEM MODE 2 by Hans
            #######################

            # Currently the 20x4 module displays the same messages as the 16x2 - ie only on the first 2 lines

            elif gv.SYSTEM_MODE == 2:
                if gv.USE_HD44780_16x2_LCD or gv.USE_HD44780_20x4_LCD:
                    if 'loading' in changed_var:
                        pass
                        # self.LCD_SYS.display(unichr(1) * int(gv.percent_loaded * (gv.LCD_COLS / 100.0) + 1))
                    elif 'voice' in changed_var:
                        self.LCD_SYS.display('')
                    elif str_override:
                        self.LCD_SYS.display(str_override)
                    else:
                        self.LCD_SYS.display('')
