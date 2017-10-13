import threading
import time
import globalvars as gv

class TextScroller:
    def __init__(self):

        self.init_sleep = 1.5
        self.line = 0
        self.is_error = False
        self.num_cols = gv.LCD_COLS
        self.delay = 0.2
        self.change_triggered = False
        self.s_first_run = ''
        self.s_all_others = ''
        self.s = ''
        self.is_looping = False
        self.loop_alive = True
        self.string_loop_thread = threading.Thread(target=self.loop_thread)
        self.string_loop_thread.daemon = True
        self.string_loop_thread.start()

    def set_string(self, string, line=2, is_error=False):

        self.loop_alive = True
        self.is_looping = True
        self.change_triggered = True
        self.line = line
        self.is_error = is_error
        padding = ' ' * self.num_cols
        self.s_first_run = string + padding  # First string fills the screen
        self.s_all_others = padding + self.s_first_run  # Second onwards comes in from the right
        self.s = self.s_first_run

    def stop(self):
        self.s = ''
        self.change_triggered = True
        self.loop_alive = False
        self.is_looping = False

    def loop_thread(self):

        while True:
            if self.is_looping:
                for i in range(len(self.s) - self.num_cols + 1):
                    if self.change_triggered or self.is_looping == False:
                        self.change_triggered = False
                        break
                    framebuffer = self.s[i:i + self.num_cols]
                    gv.displayer.disp_change(framebuffer, line=self.line, timeout=0, is_error=self.is_error)
                    if i == 0:
                        for k in range(int(self.init_sleep / self.delay)):
                            if self.change_triggered or self.is_looping == False:
                                self.change_triggered = False
                                break
                            time.sleep(self.delay)
                    else:
                        time.sleep(self.delay)
            else:
                time.sleep(0.005)

            time.sleep(0.005)
