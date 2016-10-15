import time
import globalvars as gvars
import loadsamples as ls
import threading
import navigator
import lcd

#########################################

if gvars.USE_BUTTONS and gvars.IS_DEBIAN:
    import RPi.GPIO as GPIO

    lastbuttontime = 0

    def Buttons():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        global lastbuttontime
        while True:
            now = time.time()
            if not GPIO.input(18) and (now - lastbuttontime) > 0.2:
                lastbuttontime = now
                gvars.preset -= 1
                if gvars.preset < 0:
                    gvars.preset = 127
                ls.LoadSamples()

            elif not GPIO.input(17) and (now - lastbuttontime) > 0.2:
                lastbuttontime = now
                gvars.preset += 1
                if gvars.preset > 127:
                    gvars.preset = 0
                ls.LoadSamples()

            time.sleep(0.020)







    # def Buttons():
    #     GPIO.setmode(GPIO.BCM)
    #     GPIO.setup(6, GPIO.IN)
    #     GPIO.setup(13, GPIO.IN)
    #     GPIO.setup(19, GPIO.IN)
    #     GPIO.setup(26, GPIO.IN)
    #
    #     global lastbuttontime #, preset
    #     while True:
    #         now = time.time()
    #         if GPIO.input(6) and (now - lastbuttontime) > 0.2:
    #             lastbuttontime = now
    #             gvars.preset += 1
    #             the_str = 'Preset: ' + str(gvars.preset)
    #             lcd.display('-=SAMPLERBOX=- !', 1)
    #             lcd.display(the_str, 2)
    #         if GPIO.input(13):
    #             lcd.display('Button: 2', 1)
    #         if GPIO.input(19):
    #             lcd.display('Button: 3', 1)
    #         if GPIO.input(26):
    #             lcd.display('Button: 4', 1)
    #         time.sleep(0.01)
    #
    #
    # ButtonsThread = threading.Thread(target=Buttons)
    # ButtonsThread.daemon = True
    # ButtonsThread.start()


