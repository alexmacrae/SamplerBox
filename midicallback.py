import globalvars as gvars
import os
import loadsamples
import lcdcustomchars as lcdcc
import lcd
import freeverb

#########################################
# MIDI CALLBACK
#########################################

def MidiCallback(src, message, time_stamp):
    global n

    preset_notes    = [70, 71]
    voice_notes     = [66, 67, 68, 69]

    messagetype = message[0] >> 4
    if messagetype == 13:
        return

    messagechannel = (message[0] & 15) + 1

    note = message[1] if len(message) > 1 else None
    midinote = note
    velocity = message[2] if len(message) > 2 else None
    # if (messagetype != 14):
    #    print "ch: " + str(messagechannel) + " type: " + str(messagetype) + " raw: " + str(message) + " SRC: " + str(src)


    # special keys from Kurzweil
    # if len(message) == 1 and message[0] == 250:  # playbutton Kurzweil
    #     StartTrack()
    #
    # if len(message) == 1 and message[0] == 252: # stopbutton Kurzweil
    #     StopTrack()


    if(messagetype == 11):

        if(note == 49): # Enter button
            if(velocity == 127):
                if gvars.nav:
                    gvars.nav.state.enter()
#            else:
#                nav.state.enterUp()

        if(note == 48): # Left arrow button
            if(velocity == 127):
                gvars.nav.state.left()
    #            else:
    #                nav.state.leftUp()


        if(note == 50): # Right arrow button
            if(velocity == 127):
                gvars.nav.state.right()

    #            else:
    #                nav.state.rightUp()


        if(note == 65): # Cancel button
            if(velocity == 127):
                gvars.nav.state.cancel()
    #            else:
    #                nav.state.cancelUp()

    if messagechannel == gvars.MIDI_CHANNEL:
        if messagetype == 9 and velocity == 0:
            messagetype = 8
        elif messagetype == 9:    # Note on
            midinote += gvars.globaltranspose
            # scale the selected sample based on velocity, the volume will be kept, this will normally make the sound brighter
            SelectVelocity = (velocity * (127-gvars.VelocitySelectionOffset) / 127) + gvars.VelocitySelectionOffset

            for sn in gvars.sustainplayingnotes:
                if n.note == midinote:
                    n.fadeout(500)
            try:
                gvars.playingnotes.setdefault(midinote, []).append(gvars.samples[midinote, SelectVelocity, gvars.current_voice].play(midinote, velocity))
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
            #print 'Program change ' + str(note)
            if gvars.preset != note:
                gvars.preset = note
                loadsamples.LoadSamples()


    # VOICE CHANGE

        if (messagetype == 11) and (velocity == 127) and (note in voice_notes):
            if (note == voice_notes[0]):
                gvars.current_voice = 1
            if (note == voice_notes[1]):
                gvars.current_voice = 2
            if (note == voice_notes[2]):
                gvars.current_voice = 3
            if (note == voice_notes[3]):
                gvars.current_voice = 4
            print 'VOICE [' + str(gvars.current_voice) + ']'

    # FREEVERB
        if (messagetype == 11):

            if (note == 21):
                freeverb.setroomsize(velocity)
            if (note == 22):
                freeverb.setdamp(velocity)
            if (note == 23):
                freeverb.setwet(velocity)
            if (note == 19):
                freeverb.setdry(velocity)
            if (note == 20):
                freeverb.setwidth(velocity)


    # SUSTAIN PEDAL
        elif ((messagetype == 11) and (note == 64) and (velocity < 64)) or (("microKEY" in src) and (messagetype == 14) and (note == 64 or note == 0) and (velocity >= 28)) and (gvars.sustain == True):  # sustain pedal off

            for n in gvars.sustainplayingnotes:
                n.fadeout(50)
                gvars.sustainplayingnotes = []
            gvars.sustain = False
            #print "up"

        elif ((messagetype == 11) and (note == 64) and (velocity >= 64)) or (("microKEY" in src) and (messagetype == 14) and (note == 64 or note == 0) and (velocity <= 25)) and (gvars.sustain == False):  # sustain pedal on
            gvars.sustain = True
            #print "down"

    # GLOBAL VOLUME
        elif (messagetype == 11) and (note == 7) and ("nanoKONTROL" in src):
            i = int(float(velocity / 127.0) * 13) + 1
            lcd.display('VOL' + (unichr(1) * i), 2)
            gvars.globalvolume = (10.0 ** (-12.0 / 20.0)) * (float(velocity) / 127.0)
            #print gvars.globalvolume

    # STARTBACKING TRACK
    #  elif (message[0]==176) and (message[1]==29) and (message[2]==127):
    #    StartTrack()
