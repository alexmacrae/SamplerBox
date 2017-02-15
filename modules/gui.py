from Tkinter import *
import configdefaultsdict
import configparser_samplerbox as cp
from functools import partial
import sounddevice
from time import sleep
import audiocontrols


class SamplerBoxGUI():
    def __init__(self):

        self.is_main = False
        if __name__ != "__main__":
            import globalvars as gv
            self.is_main = True


        self.root = Tk()

        self.canvas = Canvas(self.root, borderwidth=0)
        self.frame = Frame(self.canvas)

        self.vsb = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.frame.bind("<Configure>", self.on_frame_configure)

        self.frame_config = None

        # Set up emulated LCD display
        self.output = Label(self.frame, text="")
        self.output.config(font=("Lucida Sans Unicode", 20), background='#0080bc', fg='#ffffff')
        self.output.pack()


        from PIL import ImageTk






        # Make some buttons
        if self.is_main:
            self.frame_button_holder = Frame(self.frame)
            self.button_prev_preset = Button(self.frame_button_holder, text='<<', command=lambda: gv.nav.state.left())
            self.button_enter_preset = Button(self.frame_button_holder, text='Enter', command=lambda: gv.nav.state.enter())
            self.button_next_preset = Button(self.frame_button_holder, text='>>', command=lambda: gv.nav.state.right())
            self.button_cancel_preset = Button(self.frame, text='Cancel', command=lambda: gv.nav.state.cancel())

            b_i_left = ImageTk.PhotoImage(file="button_left.png")
            b_i_right = ImageTk.PhotoImage(file="button_right.png")
            b_i_enter = ImageTk.PhotoImage(file="button_enter.png")
            b_i_cancel = ImageTk.PhotoImage(file="button_cancel.png")

            self.button_prev_preset.config(image=b_i_left, bd=0)
            self.button_prev_preset.image = b_i_left
            self.button_enter_preset.config(image=b_i_enter, bd=0)
            self.button_enter_preset.image = b_i_enter
            self.button_next_preset.config(image=b_i_right, bd=0)
            self.button_next_preset.image = b_i_right
            self.button_cancel_preset.config(image=b_i_cancel, bd=0)
            self.button_cancel_preset.image = b_i_cancel

            self.frame_button_holder.pack(side=TOP)
            self.button_prev_preset.pack(side=LEFT)
            self.button_enter_preset.pack(side=LEFT)
            self.button_next_preset.pack(side=RIGHT)
            self.button_cancel_preset.pack(side=TOP)

        frame_test_notes = Frame(self.frame)
        frame_test_notes.pack(side=TOP)
        self.button_play_notes = Button(frame_test_notes, text='Test some notes', command=test_some_notes).pack(side=LEFT)
        self.button_stop_notes = Button(frame_test_notes, text='Stop notes', command=ac.all_notes_off).pack(side=RIGHT)

        self.button_open_config = Button(self.frame, text='Configuration', command=self.open_frame_config)
        self.button_open_config.pack()

        self.open_frame_config()


        ############
        # Menu bar #
        ############

        # create a toplevel menu
        menubar = Menu(self.root)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        self.root.config(menu=menubar)

        #############################
        # WINDOW SIZE AND PLACEMENT #
        #############################

        w = 500
        h = 600
        # get screen width and height
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws * 2) - 1900
        y = (hs / 2) - 500
        # set the dimensions of the screen and where it is placed
        self.root.wm_title("SamplerBox")
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))

        # def populate(self):
        #     '''Put in some fake data'''
        #     for row in range(100):
        #         Label(self.frame, text="%s" % row, width=3, borderwidth="1",
        #               relief="solid").grid(row=row, column=0)
        #         t = "this is the second column for row %s" % row
        #         Label(self.frame, text=t).grid(row=row, column=1)



    def open_frame_config(self):
        self.frame_config = GlobalConfigFrame(self.frame)
        self.button_open_config.config(text='Close Configuration', command=self.close_frame_config)

    def close_frame_config(self):
        if self.frame_config:
            self.frame_config.settings_frame.pack_forget()
        self.button_open_config.config(text='Configuration', command=self.open_frame_config)



    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta / 120), "units")

    def on_frame_configure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def start_gui_loop(self):
        # This is called before the main loop in samplerbox.py
        # IMPORTANT: This must be commented out if running from samplerbox.py
        self.root.mainloop()



class GlobalConfigFrame(object):
    def __init__(self, frame):

        self.frame = frame

        self.sound_devices = get_sound_devices()

        cd = configdefaultsdict.configdefaults
        cd.get('AUDIO_DEVICE_NAME')['options'] = self.sound_devices

        options_order = ['MAX_POLYPHONY', 'MIDI_CHANNEL', 'SYSTEM_MODE',
                         'GLOBAL_VOLUME', 'AUDIO_DEVICE_NAME', 'SAMPLES_DIR',
                         'BOXRELEASE', 'USE_HD44780_16X2_LCD', 'USE_HD44780_20x4_LCD',
                         'CHANNELS', 'BUFFERSIZE', 'SAMPLERATE', 'USE_BUTTONS',
                         'USE_I2C_7SEGMENTDISPLAY', 'USE_FREEVERB', 'USE_TONECONTROL',
                         'USE_SERIALPORT_MIDI', 'PRESET_BASE', 'RAM_LIMIT_PERCENTAGE',
                         'PRINT_MIDI_MESSAGES', 'PRINT_LCD_MESSAGES',
                         'BUTTON_LEFT_MIDI', 'BUTTON_RIGHT_MIDI',
                         'BUTTON_ENTER_MIDI', 'BUTTON_CANCEL_MIDI',
                         'BUTTON_UP_MIDI', 'BUTTON_DOWN_MIDI', 'BUTTON_FUNC_MIDI',
                         'BUTTON_LEFT_GPIO', 'BUTTON_RIGHT_GPIO', 'BUTTON_ENTER_GPIO', 'BUTTON_CANCEL_GPIO',
                         'BUTTON_UP_GPIO', 'BUTTON_DOWN_GPIO', 'BUTTON_FUNC_GPIO',
                         'GPIO_LCD_RS', 'GPIO_LCD_E', 'GPIO_LCD_D4', 'GPIO_LCD_D5', 'GPIO_LCD_D6', 'GPIO_LCD_D7',
                         'GPIO_7SEG']

        self.settings_frame = Frame(master=self.frame)
        # self.settings_frame.pack_propagate(0) # don't shrink to content's size
        self.settings_frame.pack()

        # settings_table = SimpleTable(self.settings_frame, options_order.__len__(), columns=3)
        settings_table = Frame(master=self.settings_frame)
        settings_table.pack(side="top", fill="x")

        rows = options_order.__len__()
        columns = 4

        # Build the config table
        self._widgets = []
        for row in range(rows):
            current_row = []
            option_name = options_order[row]
            if cd.has_key(option_name):

                type = cd.get(option_name).get('type')

                for column in xrange(columns):

                    if column == 0:
                        label_text = option_name.replace('_', ' ').title()
                        label = Label(settings_table, text=label_text, borderwidth=0)
                        label.config(padx=5, pady=5, wraplength=150)
                        label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        current_row.append(label)
                    if column == 1:

                        if type == 'range' or type == 'int':
                            input = Entry(settings_table, borderwidth=0)
                            input.insert(0, str(cp.get_option_by_name(option_name)))
                            input.config(justify=CENTER)
                        elif type == 'string':
                            input = Entry(settings_table, borderwidth=0)
                            input.insert(0, str(cp.get_option_by_name(option_name)))
                            input.config(justify=CENTER)
                        elif type == 'boolean':
                            OPTIONS = ['True', 'False']
                            option_value = str(cp.get_option_by_name(option_name))
                            current_option_index = OPTIONS.index(option_value)
                            variable = StringVar(settings_table)
                            variable.set(OPTIONS[current_option_index])  # default value
                            input = apply(OptionMenu, (settings_table, variable) + tuple(OPTIONS))
                        elif type == 'options':
                            OPTIONS = cd.get(option_name).get('options')
                            option_value = str(cp.get_option_by_name(option_name))
                            current_option_index = OPTIONS.index(option_value)
                            variable = StringVar(settings_table)
                            variable.set(OPTIONS[current_option_index])  # default value
                            input = apply(OptionMenu, (settings_table, variable) + tuple(OPTIONS))
                        elif type == 'midi':
                            input = Label(settings_table, text=str(cp.get_option_by_name(option_name)), borderwidth=0)
                            input.config(justify=LEFT, state=DISABLED)
                        else:
                            input = Entry(settings_table, borderwidth=0)
                            input.insert(0, str(cp.get_option_by_name(option_name)))
                            input.config(justify=CENTER)

                        input.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        current_row.append(input)

                    if column == 2:
                        # pass args to callback
                        button_callback_with_args = partial(self.save_option,
                                                            'SAMPLERBOX CONFIG',
                                                            option_name,
                                                            row
                                                            )
                        button_save = Button(settings_table, text='Save', command=button_callback_with_args)
                        button_save.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        current_row.append(button_save)

                    if column == 3 and type == 'midi':
                        button = Button(settings_table, text='MIDI Learn')
                        button.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        current_row.append(button)

                self._widgets.append(current_row)

        for column in xrange(columns):
            settings_table.grid_columnconfigure(column, weight=1)

    def save_option(self, section, option, row):

        widget = self._widgets[row][1]  # [row][column]
        entry_value = widget.get()

        cp.update_config(section, option, entry_value)


def get_sound_devices():
    sound_devices_dict = sounddevice.query_devices()
    acceptable_sound_devices = []
    index = 0
    for sd in sound_devices_dict:
        if sd['max_output_channels'] > 1:  # only get sound devices with an output
            acceptable_sound_devices.append(sd['name'])
            # print '%s :: %s' % (sd['name'], index)
        index += 1

    return acceptable_sound_devices



ac = audiocontrols.AudioControls()

def test_some_notes():

    notes = [60, 64, 67, 72]
    for note in notes:
        ac.noteon(note, midichannel=1, velocity=127)
        sleep(0.2)






if __name__ == "__main__":

    gui = SamplerBoxGUI()

    # gui.start_frame_config()

    # gui_config = GlobalConfigFrame(gui.frame)

    gui.start_gui_loop()
