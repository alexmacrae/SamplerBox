import globalvars as gv

class Buttons():

    def __init__(self):

        self.bouncetime = 250 # time before another button press can take place (in milliseconds)

        if gv.USE_BUTTONS and gv.IS_DEBIAN:

            import RPi.GPIO as GPIO

            if gv.SYSTEM_MODE == 1:

                def button_callback(channel):
                    if GPIO.input(channel) == 0:
                        # print '-------\rChannel:%d Input value:%d' % (channel, GPIO.input(channel))

                        if channel == gv.BUTTON_LEFT_GPIO:
                            print '\rLEFT GPIO button pressed'  # debug
                            gv.nav.state.left()
                        elif channel == gv.BUTTON_RIGHT_GPIO:
                            print '\rRIGHT GPIO button pressed' # debug
                            gv.nav.state.right()
                        elif channel == gv.BUTTON_ENTER_GPIO:
                            print '\rENTER GPIO button pressed' # debug
                            gv.nav.state.enter()
                        elif channel == gv.BUTTON_CANCEL_GPIO:
                            print '\rCANCEL GPIO button pressed' # debug
                            gv.nav.state.cancel()

                GPIO.setmode(GPIO.BCM)
                GPIO_channel_list = [gv.BUTTON_LEFT_GPIO, gv.BUTTON_RIGHT_GPIO, gv.BUTTON_ENTER_GPIO, gv.BUTTON_CANCEL_GPIO]
                GPIO.setup(GPIO_channel_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)

                # BUTTON_MOM = 'momentary'
                # BUTTON_TOG = 'toggle'
                # button_mode = BUTTON_TOG

                GPIO.add_event_detect(gv.BUTTON_LEFT_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=self.bouncetime)
                GPIO.add_event_detect(gv.BUTTON_RIGHT_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=self.bouncetime)
                GPIO.add_event_detect(gv.BUTTON_ENTER_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=self.bouncetime)
                GPIO.add_event_detect(gv.BUTTON_CANCEL_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=self.bouncetime)

            ##################
            # Hans' buttons
            ##################

            if gv.SYSTEM_MODE == 2:

                def button_callback(channel):

                    if GPIO.input(channel) == 0:
                        # print '-------\rChannel:%d Input value:%d' % (channel, GPIO.input(channel))

                        if channel == gv.BUTTON_UP_GPIO:
                            # print("Button up")
                            gv.nav.up()

                        elif channel == gv.BUTTON_DOWN_GPIO:
                            # print("Button down")
                            gv.nav.down()

                        elif channel == gv.BUTTON_FUNC_GPIO:
                            # print("Function Button")
                            gv.nav.func()


                GPIO.setmode(GPIO.BCM)
                GPIO_channel_list = [gv.BUTTON_UP_GPIO, gv.BUTTON_DOWN_GPIO, gv.BUTTON_FUNC_GPIO]
                GPIO.setup(GPIO_channel_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)

                GPIO.add_event_detect(gv.BUTTON_UP_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=self.bouncetime)
                GPIO.add_event_detect(gv.BUTTON_DOWN_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=self.bouncetime)
                GPIO.add_event_detect(gv.BUTTON_FUNC_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=self.bouncetime)

