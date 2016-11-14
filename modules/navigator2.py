import globalvars as gv
import loadsamples as ls
import displayer
import audiocontrols as ac

lastbuttontime = 0
buttfunc = 0
button_functions = ["", "Volume", "Midichannel", "Transpose", "RenewUSB/MidMute", "Play Chord:"]
button_disp = ["", "V", "M", "T", "S", "C"]  # take care, these values are used below for testing


def Button_display():
    function_value = ["", " %d%%" % (gv.global_volume),
                      " %d" % (gv.MIDI_CHANNEL), " %+d" % (gv.globaltranspose),
                      "", " %s" % (gv.chordname[gv.currchord])]
    displayer.disp_change(str_override=button_functions[buttfunc] + function_value[buttfunc])


def butt_up():
    global buttfunc

    if buttfunc == 0:
        gv.preset += 1
        if gv.preset > 127: gv.preset = 0
        ls.LoadSamples()
    elif buttfunc == 1:
        gv.global_volume += 5
        if gv.global_volume > 100: gv.global_volume = 100
        ac.MasterVolume().setvolume(gv.global_volume * 1.27)
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
        ls.LoadSamples()
    elif buttfunc == 5:
        gv.currchord += 1
        if gv.currchord >= len(gv.chordname): gv.currchord = 0
        Button_display()


def butt_down():
    global buttfunc
    if buttfunc == 0:
        gv.preset -= 1
        if gv.preset < 0: gv.preset = 127
        ls.LoadSamples()
    elif buttfunc == 1:
        gv.global_volume -= 5
        if gv.global_volume < 0: gv.global_volume = 0
        ac.MasterVolume().setvolume(gv.global_volume * 1.27)
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
        gv.currchord -= 1
        if gv.currchord < 0: gv.currchord = len(gv.chordname) - 1
        Button_display()


def butt_func():
    global buttfunc
    buttfunc += 1

    if buttfunc >= len(button_functions): buttfunc = 0
    if not gv.USE_ALSA_MIXER:
        if button_disp[buttfunc] == "V": buttfunc += 1
    # use if above gets complex: if buttfunc >= len(button_functions): buttfunc=0
    gv.midi_mute = False
    Button_display()
