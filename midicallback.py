import globalvars as gvars
import loadsamples
import lcd
import freeverb
import navigator

Navigator = navigator.Navigator


############################
# ACTUAL DO STUFF FUNCTIONS
############################

class Reverb:
    def roomsize(self, vel):
        freeverb.setroomsize(vel)

    def damping(self, vel):
        freeverb.setdamp(vel)

    def wet(self, vel):
        freeverb.setwet(vel)

    def dry(self, vel):
        freeverb.setdry(vel)

    def width(self, vel):
        freeverb.setwidth(vel)


def noteon(messagetype, note, vel):
    # print messagetype, note, vel
    pass


def noteoff(messagetype, note, vel):
    # print messagetype, note, vel
    pass


class MasterVolume:
    def setvolume(self, vel):
        i = int(float(vel / 127.0) * (lcd.LCD_COLS - 1)) + 1
        lcd.display('Volume', 3)
        lcd.display((unichr(1) * i), 4)
        gvars.globalvolume = (10.0 ** (-12.0 / 20.0)) * (float(vel) / 127.0)


class Voices:
    def voice1(self, vel):
        if vel != 0:
            gvars.current_voice = 1
            print 'Voice 1 activated'

    def voice2(self, vel):
        if vel != 0:
            gvars.current_voice = 2
            print 'Voice 2 activated'

    def voice3(self, vel):
        if vel != 0:
            gvars.current_voice = 3
            print 'Voice 3 activated'

    def voice4(self, vel):
        if vel != 0:
            gvars.current_voice = 4
            print 'Voice 4 activated'


class PresetNav:
    def left(self, vel):
        if vel != 0:
            navigator.PresetNav().left()

    def right(self, vel):
        if vel != 0:
            navigator.PresetNav().right()


#########################################
# MIDI CALLBACK
#########################################

def MidiCallback(src, message, time_stamp):
    midimaps = gvars.midimaps

    src = src[:src.rfind(" "):]  # remove the port number from the end

    cc_remapped = False
    preset_notes = [70, 71]
    voice_notes = [66, 67, 68, 69]



    messagetype = message[0] >> 4
    if messagetype == 13:
        return

    messagechannel = (message[0] & 15) + 1

    note = message[1] if len(message) > 1 else None
    midinote = note
    velocity = message[2] if len(message) > 2 else None
    # if (messagetype != 14):
    #    print "ch: " + str(messagechannel) + " type: " + str(messagetype) + " raw: " + str(message) + " SRC: " + str(src)
    if gvars.PRINT_MIDI_MESSAGES:
        print str(message[0]) + ', ' + str(note) + ', <'+src+'>'


    # special keys from Kurzweil
    # if len(message) == 1 and message[0] == 250:  # playbutton Kurzweil
    #     StartTrack()
    #
    # if len(message) == 1 and message[0] == 252: # stopbutton Kurzweil
    #     StopTrack()
    if gvars.learningMode and messagetype != 8:

        Navigator.state.sendControlToMap(message, src)

    else:
        try:

            messageKey = (message[0], message[1])

            if midimaps.get(src).has_key(messageKey):

                # remap note to a function
                if midimaps.get(src).get(messageKey).has_key('fn'):

                    fnSplit = midimaps.get(src).get(messageKey).get('fn').split('.')

                    getattr(eval(fnSplit[0])(), fnSplit[1])(
                        velocity)  # runs method from class. ie getattr(MasterVolume(), 'setvolume')

                    cc_remapped = True

                # remap note to a key
                elif isinstance(midimaps.get(src).get(messageKey).get('note'), int):
                    note = midimaps.get(src).get(messageKey).get('note')

        except:
            pass

        # Default CC mapping
        if not cc_remapped and messagetype != 9 and messagetype != 8 and messagetype == 11:
            if (note == 7):
                MasterVolume().setvolume(velocity)


        ######################
        # Button navigation
        # Determined by config
        ######################

        enter = gvars.BUTTON_ENTER
        left = gvars.BUTTON_LEFT
        right = gvars.BUTTON_RIGHT
        cancel = gvars.BUTTON_CANCEL

        if message[0] == enter[0] and note == enter[1] and velocity > 0 and enter[2] in src: # Enter arrow button
            gvars.nav.state.enter()

        elif message[0] == left[0] and note == left[1] and velocity > 0 and left[2] in src:  # Left arrow button
            gvars.nav.state.left()

        elif message[0] == right[0] and note == right[1] and velocity > 0 and right[2] in src:  # Right arrow button
            gvars.nav.state.right()

        elif message[0] == cancel[0] and note == cancel[1] and velocity > 0 and cancel[2] in src:  # Cancel button
            gvars.nav.state.cancel()



        if messagechannel == gvars.MIDI_CHANNEL:

            if messagetype == 9 and velocity == 0:
                messagetype = 8
            elif messagetype == 9:  # Note on
                midinote += gvars.globaltranspose
                # scale the selected sample based on velocity, the volume will be kept, this will normally make the sound brighter
                SelectVelocity = (
                                     velocity * (
                                         127 - gvars.VelocitySelectionOffset) / 127) + gvars.VelocitySelectionOffset

                for n in gvars.sustainplayingnotes:
                    if n.note == midinote:
                        n.fadeout(500)
                try:
                    gvars.playingnotes.setdefault(midinote, []).append(
                        gvars.samples[midinote, SelectVelocity, gvars.current_voice].play(midinote, velocity))
                except:
                    print 'failed'
                    pass

            elif messagetype == 8:  # Note off
                midinote += gvars.globaltranspose
                if midinote in gvars.playingnotes:
                    for n in gvars.playingnotes[midinote]:
                        if gvars.sustain:
                            gvars.sustainplayingnotes.append(n)
                        else:
                            n.fadeout(50)
                    gvars.playingnotes[midinote] = []

            elif messagetype == 12:  # Program change
                # print 'Program change ' + str(note)
                if gvars.preset != note:
                    gvars.preset = note
                    loadsamples.LoadSamples()


                    # VOICE CHANGE
                    # With MIDI mapping available, this is not necessary anymore

                    # if (messagetype == 11) and (velocity == 127) and (note in voice_notes):
                    #     if (note == voice_notes[0]):
                    #         gvars.current_voice = 1
                    #     if (note == voice_notes[1]):
                    #         gvars.current_voice = 2
                    #     if (note == voice_notes[2]):
                    #         gvars.current_voice = 3
                    #     if (note == voice_notes[3]):
                    #         gvars.current_voice = 4
                    #     print 'VOICE [' + str(gvars.current_voice) + ']'

                    # FREEVERB
                    # With MIDI mapping available, this is not necessary anymore
                    # if (messagetype == 11):
                    #     if (note == 21):
                    #         freeverb.setroomsize(velocity)
                    #     if (note == 22):
                    #         freeverb.setdamp(velocity)
                    #     if (note == 23):
                    #         freeverb.setwet(velocity)
                    #     if (note == 19):
                    #         freeverb.setdry(velocity)
                    #     if (note == 20):
                    #         freeverb.setwidth(velocity)


                    # SUSTAIN PEDAL
            if ((messagetype == 11) and (note == 64) and (velocity < 64)) or (
                                ("microKEY" in src) and (messagetype == 14) and (note == 64 or note == 0) and (
                                velocity >= 28)) and (gvars.sustain == True):  # sustain pedal off
                for n in gvars.sustainplayingnotes:
                    n.fadeout(50)
                    gvars.sustainplayingnotes = []
                gvars.sustain = False

            elif ((messagetype == 11) and (note == 64) and (velocity >= 64)) or (
                                ("microKEY" in src) and (messagetype == 14) and (note == 64 or note == 0) and (
                                velocity <= 25)) and (gvars.sustain == False):  # sustain pedal on
                gvars.sustain = True

                # GLOBAL VOLUME

            elif (messagetype == 11) and (note == 7):
                MasterVolume().setvolume(velocity)
