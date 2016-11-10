import time
import globalvars as gv
import threading

if gv.USE_BUTTONS and gv.IS_DEBIAN:
    import RPi.GPIO as GPIO

    lastbuttontime = 0

    # NB: Not using Hans' button setup due to our different navigation systems
    def Buttons():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gv.BUTTON_LEFT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(gv.BUTTON_RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(gv.BUTTON_ENTER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(gv.BUTTON_CANCEL_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        global lastbuttontime
        while True:
            now = time.time()
            if(now - lastbuttontime) :
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

    ButtonsThread = threading.Thread(target=Buttons)
    ButtonsThread.daemon = True
    ButtonsThread.start()

