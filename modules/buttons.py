import globalvars as gv

if gv.USE_BUTTONS and gv.IS_DEBIAN:

    import time
    import threading
    import RPi.GPIO as GPIO
    if gv.SYSTEM_MODE == 1:

        def Buttons_1():
            time.sleep(8)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(gv.BUTTON_LEFT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(gv.BUTTON_RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(gv.BUTTON_ENTER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(gv.BUTTON_CANCEL_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            last_button_time = 0

            button_pressed = False
            prev_button = 0

            BUTTON_MOM = 'momentary'
            BUTTON_TOG = 'toggle'
            button_mode = BUTTON_TOG

            while True:
                now = time.time()
                if (now - last_button_time) > 1:


                    if not GPIO.input(gv.BUTTON_LEFT_GPIO):
                        prev_button = GPIO.input(gv.BUTTON_LEFT_GPIO)
                        print time.ctime(), prev_button
                        gv.displayer.disp_change(str_override=str(time.ctime()), line=2, timeout=0)
                        last_button_time = now

                    # if not GPIO.input(gv.BUTTON_LEFT_GPIO) and not prev_button:
                    #     gv.nav1.state.left()
                    #     print 'left'
                    #     prev_button = GPIO.input(gv.BUTTON_LEFT_GPIO)
                    #     #button_pressed = True
                    # elif not GPIO.input(gv.BUTTON_RIGHT_GPIO):
                    #     print 'right'
                    #     gv.nav1.state.right()
                    # elif not GPIO.input(gv.BUTTON_ENTER_GPIO):
                    #     print 'enter'
                    #     gv.nav1.state.enter()
                    # elif not GPIO.input(gv.BUTTON_CANCEL_GPIO):
                    #     print 'cancel'
                    #     gv.nav1.state.cancel()
                    # else:
                    #     button_pressed = False

                time.sleep(1)


        ButtonsThread_1 = threading.Thread(target=Buttons_1)
        ButtonsThread_1.daemon = True
        ButtonsThread_1.start()

    ##################
    # Hans' buttons
    ##################

    if gv.SYSTEM_MODE == 2:

        import loadsamples as ls

        last_button_time = 0
        butt_up = gv.BUTTON_UP_GPIO  # values of butt_up/down/sel depend on physical wiring
        butt_down = gv.BUTTON_DOWN_GPIO   # values of butt_up/down/sel depend on physical wiring
        butt_func = gv.BUTTON_FUNC_GPIO   # values of butt_up/down/sel depend on physical wiring
        buttfunc = 0
        button_functions = ["", "Volume", "Midichannel", "Transpose", "RenewUSB/MidMute", "Play Chord:"]
        button_disp = ["", "V", "M", "T", "S", "C"]  # take care, these values are used below for testing


        def Button_display():
            global volume, MIDI_CHANNEL, globaltranspose, buttfunc, button_functions, CHORD_NAMES, current_chord
            function_value = ["", " %d%%" % (volume), " %d" % (MIDI_CHANNEL), " %+d" % (globaltranspose), "",
                              " %s" % (CHORD_NAMES[current_chord])]

            gv.GPIO_button_func = button_functions[buttfunc]
            gv.GPIO_function_val = function_value[buttfunc]

            #display(button_functions[buttfunc] + function_value[buttfunc])


        def Buttons_2():
            global preset, basename, last_button_time, volume, MIDI_CHANNEL, globaltranspose, midi_mute, CHORD_NAMES, current_chord
            global buttfunc, button_functions, butt_up, butt_down, butt_sel, button_disp

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(butt_up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(butt_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(butt_func, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            last_button_time = time.time()

            while True:
                now = time.time()
                if (now - last_button_time) > 0.2:
                    if not GPIO.input(butt_down):
                        last_button_time = now
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
                            current_chord -= 1
                            if current_chord < 0: current_chord = len(CHORD_NAMES) - 1
                            Button_display()

                    elif not GPIO.input(butt_up):
                        last_button_time = now
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
                            current_chord += 1
                            if current_chord >= len(CHORD_NAMES): current_chord = 0
                            Button_display()

                    elif not GPIO.input(butt_func):
                        last_button_time = now
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
