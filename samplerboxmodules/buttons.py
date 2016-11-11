import globalvars as gv

if gv.USE_BUTTONS and gv.IS_DEBIAN:

    import time
    import threading
    import RPi.GPIO as GPIO
    if gv.SYSTEM_MODE == 1:

        def Buttons_1():
            lastbuttontime = 0
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(gv.BUTTON_LEFT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(gv.BUTTON_RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(gv.BUTTON_ENTER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(gv.BUTTON_CANCEL_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            while True:
                now = time.time()
                if (now - lastbuttontime):
                    lastbuttontime = now
                    if not GPIO.input(gv.BUTTON_LEFT_GPIO):
                        gv.nav.state.left()
                    elif not GPIO.input(gv.BUTTON_RIGHT_GPIO):
                        gv.nav.state.right()
                    elif not GPIO.input(gv.BUTTON_ENTER_GPIO):
                        gv.nav.state.enter()
                    elif not GPIO.input(gv.BUTTON_CANCEL_GPIO):
                        gv.nav.state.cancel()

                time.sleep(0.020)


        ButtonsThread_1 = threading.Thread(target=Buttons_1)
        ButtonsThread_1.daemon = True
        ButtonsThread_1.start()

    ##################
    # Hans' buttons
    ##################

    if gv.SYSTEM_MODE == 2:

        import loadsamples as ls

        lastbuttontime = 0
        butt_up = gv.BUTTON_UP_GPIO  # values of butt_up/down/sel depend on physical wiring
        butt_down = gv.BUTTON_DOWN_GPIO   # values of butt_up/down/sel depend on physical wiring
        butt_func = gv.BUTTON_FUNC_GPIO   # values of butt_up/down/sel depend on physical wiring
        buttfunc = 0
        button_functions = ["", "Volume", "Midichannel", "Transpose", "RenewUSB/MidMute", "Play Chord:"]
        button_disp = ["", "V", "M", "T", "S", "C"]  # take care, these values are used below for testing


        def Button_display():
            global volume, MIDI_CHANNEL, globaltranspose, buttfunc, button_functions, chordname, currchord
            function_value = ["", " %d%%" % (volume), " %d" % (MIDI_CHANNEL), " %+d" % (globaltranspose), "",
                              " %s" % (chordname[currchord])]

            gv.GPIO_button_func = button_functions[buttfunc]
            gv.GPIO_function_val = function_value[buttfunc]

            #display(button_functions[buttfunc] + function_value[buttfunc])


        def Buttons_2():
            global preset, basename, lastbuttontime, volume, MIDI_CHANNEL, globaltranspose, midi_mute, chordname, currchord
            global buttfunc, button_functions, butt_up, butt_down, butt_sel, button_disp

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(butt_up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(butt_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(butt_func, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            lastbuttontime = time.time()

            while True:
                now = time.time()
                if (now - lastbuttontime) > 0.2:
                    if not GPIO.input(butt_down):
                        lastbuttontime = now
                        # print("Button down")
                        if buttfunc == 0:
                            preset -= 1
                            if preset < gv.PRESETBASE: preset = 127 + gv.PRESETBASE
                            ls.LoadSamples()
                        elif buttfunc == 1:
                            volume -= 5
                            if volume < 0: volume = 0
                            setvolume(volume)
                            getvolume()
                            Button_display()
                        elif buttfunc == 2:
                            MIDI_CHANNEL -= 1
                            if MIDI_CHANNEL < 1: MIDI_CHANNEL = 16
                            Button_display()
                        elif buttfunc == 3:
                            globaltranspose -= 1
                            if globaltranspose < -99: globaltranspose = -99
                            Button_display()
                        elif buttfunc == 4:
                            if not midi_mute:
                                midi_mute = True
                                display("** MIDI muted **")
                            else:
                                midi_mute = False
                                Button_display()
                        elif buttfunc == 5:
                            currchord -= 1
                            if currchord < 0: currchord = len(chordname) - 1
                            Button_display()

                    elif not GPIO.input(butt_up):
                        lastbuttontime = now
                        # print("Button up")
                        midi_mute = False
                        if buttfunc == 0:
                            preset += 1
                            if preset > 127 + gv.PRESETBASE: preset = gv.PRESETBASE
                            ls.LoadSamples()
                        elif buttfunc == 1:
                            volume += 5
                            if volume > 100: volume = 100
                            setvolume(volume)
                            getvolume()
                            Button_display()
                        elif buttfunc == 2:
                            MIDI_CHANNEL += 1
                            if MIDI_CHANNEL > 16: MIDI_CHANNEL = 1
                            Button_display()
                        elif buttfunc == 3:
                            globaltranspose += 1
                            if globaltranspose > 99: globaltranspose = 99
                            Button_display()
                        elif buttfunc == 4:
                            basename = "None"
                            ls.LoadSamples()
                            # Button_display()
                        elif buttfunc == 5:
                            currchord += 1
                            if currchord >= len(chordname): currchord = 0
                            Button_display()

                    elif not GPIO.input(butt_func):
                        lastbuttontime = now
                        # print("Function Button")
                        buttfuncmax = len(button_functions)
                        buttfunc += 1
                        if buttfunc >= len(button_functions): buttfunc = 0
                        if not gv.USE_ALSA_MIXER:
                            if button_disp[buttfunc] == "V": buttfunc += 1
                        # use if above gets complex: if buttfunc >= len(button_functions): buttfunc=0
                        midi_mute = False
                        Button_display()

                    time.sleep(0.02)


        ButtonsThread_2 = threading.Thread(target=Buttons_2)
        ButtonsThread_2.daemon = True
        ButtonsThread_2.start()
