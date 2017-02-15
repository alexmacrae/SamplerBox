import globalvars as gv
import loadsamples as ls
from os import listdir

lastbuttontime = 0
buttfunc = 0
button_functions = ["", "Volume", "Midichannel", "Transpose", "RenewUSB/MidMute", "PlayChord:"]
button_disp = ["", "V", "M", "T", "S", "C"]  # take care, these values are used below for testing
number_of_folders = len(gv.SETLIST_LIST)


def Button_display():
    function_value = [
        "",
        " %d%%" % (gv.global_volume),
        " %d" % (gv.MIDI_CHANNEL),
        " %+d" % (gv.globaltranspose),
        "",
        " %s" % (gv.ac.autochorder.CHORD_NAMES[gv.ac.autochorder.current_chord])
    ]
    print button_functions[buttfunc] + function_value[buttfunc]
    gv.displayer.disp_change(str_override=button_functions[buttfunc] + function_value[buttfunc])


def up():
    global buttfunc

    if buttfunc == 0:
        gv.preset += 1
        if gv.preset > number_of_folders - 1: gv.preset = 0
        gv.ls.LoadSamples()
        Button_display()
    elif buttfunc == 1:
        gv.global_volume += 5
        if gv.global_volume > 100: gv.global_volume = 100
        gv.ac.master_volume().setvolume(gv.global_volume * 1.27)
        Button_display()
    elif buttfunc == 2:
        gv.MIDI_CHANNEL += 1
        if gv.MIDI_CHANNEL > 16: gv.MIDI_CHANNEL = 0  # zero = all midi channels
        Button_display()
    elif buttfunc == 3:
        gv.globaltranspose += 1
        if gv.globaltranspose > 99: gv.globaltranspose = 99
        Button_display()
    elif buttfunc == 4:
        gv.basename = "None"
        gv.ls.LoadSamples()
    elif buttfunc == 5:
        if gv.ac.autochorder.current_chord < len(gv.ac.autochorder.CHORD_NAMES) - 1:
            gv.ac.autochorder.current_chord += 1
        else:
            gv.ac.autochorder.current_chord = 0
        gv.ac.autochorder.current_chord_mode = [gv.ac.autochorder.current_chord] * 12
        Button_display()


def down():
    global buttfunc
    if buttfunc == 0:
        gv.preset -= 1
        if gv.preset < 0: gv.preset = number_of_folders - 1
        gv.ls.LoadSamples()
        Button_display()
    elif buttfunc == 1:
        gv.global_volume -= 5
        if gv.global_volume < 0: gv.global_volume = 0
        gv.ac.master_volume.setvolume(gv.global_volume * 1.27)
        Button_display()
    elif buttfunc == 2:
        gv.MIDI_CHANNEL -= 1
        if gv.MIDI_CHANNEL < 0: gv.MIDI_CHANNEL = 16
        Button_display()
    elif buttfunc == 3:
        gv.globaltranspose -= 1
        if gv.globaltranspose < -99: gv.globaltranspose = -99
        Button_display()
    elif buttfunc == 4:
        if not gv.midi_mute:
            gv.midi_mute = True
            # display("** MIDI muted **")
        else:
            gv.midi_mute = False
            Button_display()
    elif buttfunc == 5:
        if gv.ac.autochorder.current_chord > 0:
            gv.ac.autochorder.current_chord -= 1
        else:
            gv.ac.autochorder.current_chord = len(gv.ac.autochorder.CHORD_NAMES) - 1
        gv.ac.autochorder.current_chord_mode = [gv.ac.autochorder.current_chord] * 12
        Button_display()


def func():
    global buttfunc
    buttfunc += 1

    if buttfunc >= len(button_functions): buttfunc = 0
    if not gv.USE_ALSA_MIXER:
        if button_disp[buttfunc] == "V": buttfunc += 1
    # use if above gets complex: if buttfunc >= len(button_functions): buttfunc=0
    gv.midi_mute = False
    Button_display()
