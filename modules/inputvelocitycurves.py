import math

"""
Adjusts the MIDI input velocity. Useful for devices that have poor velocity
sensitivities that cannot be modified on the device. eg Novation's LaunchKey Mini MKII
"""

class InputVelocityCurves:

    alpha_linear = (1, 'Default (linear)')  # default, linear
    alpha_1 = (3.0, 'Extremely soft curve')
    alpha_2 = (2.0, 'Very soft curve')
    alpha_3 = (1.5, 'Soft curve')
    alpha_4 = (0.7, 'Hard curve')
    alpha_5 = (0.4, 'Harder curve')
    alpha_6 = (0.2, 'Extremely hard curve')
    alpha_list = [alpha_linear, alpha_1, alpha_2, alpha_3, alpha_4, alpha_5, alpha_6]

    def adjust_vel(self, input_vel, alpha):
        output_vel = (math.pow((float(input_vel) / 128.0), float(alpha)) * 128.0)
        output_vel = max(min(127.0, (output_vel)), 1.0)  # keeps value within range 1-127
        return int(math.ceil(output_vel))


# TODO
"""
Perhaps menu settings navigation class should live in the module, rather than in navigator_sys_1.
Makes it easier for others to contibute their own module/plugin features.
"""

# class SettingsMenu:
#
#     def __init__(self):
#
#         self.text_scroller.stop()
#         self.ivc = InputVelocityCurves()
#         self.ALPHA_LIST = self.ivc.alpha_list
#         self.alpha_index = gv.VELOCITY_CURVE
#         self.display()
#
#     def display(self):
#         first_line = 'Velocity Curve'
#         second_line = self.ALPHA_LIST[self.alpha_index][1]
#
#         gv.displayer.disp_change(first_line.center(gv.LCD_COLS, ' '), line=1, timeout=0)
#         gv.displayer.disp_change(second_line.center(gv.LCD_COLS, ' '), line=2, timeout=0)
#
#     def left(self):
#         if gv.ac.autochorder.chord_set_index > 0:
#             gv.ac.autochorder.chord_set_index -= 1
#             gv.ac.autochorder.change_mode(gv.ac.autochorder.chord_set_index)
#             self.display()
#
#     def right(self):
#         if gv.ac.autochorder.chord_set_index < len(self.AVAILABLE_CHORD_SETS) - 1:
#             gv.ac.autochorder.chord_set_index += 1
#             gv.ac.autochorder.change_mode(gv.ac.autochorder.chord_set_index)
#             self.display()
#
#     def enter(self):
#         gv.INVERT_SUSTAIN = self.invert_sustain
#         gv.cp.update_config('SAMPLERBOX CONFIG', 'INVERT_SUSTAIN', str(self.invert_sustain))
#         self.cancel()
#
#     def cancel(self):
#         self.load_state(MenuNav)




if __name__ == '__main__':

    ivc = InputVelocityCurves()

    for i in range(1, 128):
        print i, ivc.adjust_vel(i, ivc.alpha_1[0])  # test it
