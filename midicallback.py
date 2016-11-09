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

def AllNotesOff():
    gvars.playingsounds = []
    gvars.playingnotes = {}
    gvars.sustainplayingnotes = []

class MasterVolume:
    def setvolume(self, vel):
        i = int(float(vel / 127.0) * (lcd.LCD_COLS - 1)) + 1
        lcd.display('Volume', 3)
        lcd.display((unichr(1) * i), 4)
        gvars.globalvolume = (10.0 ** (-12.0 / 20.0)) * (float(vel) / 127.0)


class Voices:
    def voice1(self, vel):
        if vel != 0:
            gvars.currvoice = 1
            print 'Voice 1 activated'

    def voice2(self, vel):
        if vel != 0:
            gvars.currvoice = 2
            print 'Voice 2 activated'

    def voice3(self, vel):
        if vel != 0:
            gvars.currvoice = 3
            print 'Voice 3 activated'

    def voice4(self, vel):
        if vel != 0:
            gvars.currvoice = 4
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

    preset_notes = [70, 71]
    voice_notes = [66, 67, 68, 69]

    messagetype = message[0] >> 4
    messagechannel = (message[0] & 15) + 1
    note = message[1] if len(message) > 1 else None
    midinote = note
    velocity = message[2] if len(message) > 2 else None
    noteoff = False
    if gvars.sample_mode == gvars.PLAYLIVE:
        noteoff = True

    if gvars.PRINT_MIDI_MESSAGES:
        print '%d, %d, <%s>' % (message[0], note, src)

    # special keys from Kurzweil
    # if len(message) == 1 and message[0] == 250:  # playbutton Kurzweil
    #     StartTrack()
    #
    # if len(message) == 1 and message[0] == 252: # stopbutton Kurzweil
    #     StopTrack()

    ######################
    # MIDI Learning
    # Send messages when learningMode is set
    ######################
    if gvars.learningMode and messagetype != 8:  # don't send note-offs
        Navigator.state.sendControlToMap(message, src)
        return

    ######################
    # Check if MIDI Mapped
    ######################
    try:
        messageKey = (message[0], message[1])

        if midimaps.get(src).has_key(messageKey):

            # remap note to a function
            if midimaps.get(src).get(messageKey).has_key('fn'):

                fnSplit = midimaps.get(src).get(messageKey).get('fn').split('.')

                getattr(eval(fnSplit[0])(), fnSplit[1])(
                    velocity)  # runs method from class. ie getattr(MasterVolume(), 'setvolume')

            # remap note to a key
            elif isinstance(midimaps.get(src).get(messageKey).get('note'), int):
                note = midimaps.get(src).get(messageKey).get('note')

    except:
        pass

    ######################
    # Button navigation
    # Determined by config
    ######################

    enter = gvars.BUTTON_ENTER
    left = gvars.BUTTON_LEFT
    right = gvars.BUTTON_RIGHT
    cancel = gvars.BUTTON_CANCEL

    if message[0] == enter[0] and note == enter[1] and velocity > 0 and enter[2] in src:  # Enter arrow button
        gvars.nav.state.enter()

    elif message[0] == left[0] and note == left[1] and velocity > 0 and left[2] in src:  # Left arrow button
        gvars.nav.state.left()

    elif message[0] == right[0] and note == right[1] and velocity > 0 and right[2] in src:  # Right arrow button
        gvars.nav.state.right()

    elif message[0] == cancel[0] and note == cancel[1] and velocity > 0 and cancel[2] in src:  # Cancel button
        gvars.nav.state.cancel()

    ######################
    # Do default MIDI functions
    ######################
    if (messagechannel == gvars.MIDI_CHANNEL) and (gvars.midi_mute == False):

        if messagetype == 9:  # is a note-off hidden in this note-on ?
            if velocity == 0:  # midi protocol, next elif's are SB's special modes
                messagetype = 8  # noteoff must be true here :-)
            elif (gvars.sample_mode == gvars.PLAYSTOP or gvars.sample_mode == gvars.PLAYLOOP) and midinote > 63:
                messagetype = 8
                midinote = midinote - 64
                noteoff = True
            elif gvars.sample_mode == gvars.PLAYLO2X and midinote in gvars.playingnotes:
                if gvars.playingnotes[midinote] != []:
                    messagetype = 8
                    noteoff = True

        if messagetype == 9:  # Note on
            midinote += gvars.globaltranspose
            # scale the selected sample based on velocity, the volume will be kept,
            # this will normally make the sound brighter (by Erik)
            SelectVelocity = (velocity
                              * (127 - gvars.VelocitySelectionOffset) / 127) \
                             + gvars.VelocitySelectionOffset

            for n in range(len(gvars.chordnote[gvars.currchord])):
                playnote = midinote + gvars.chordnote[gvars.currchord][n]
                for m in gvars.sustainplayingnotes:  # cleanup predecessors (check if necessary
                    if m.note == playnote:
                        m.fadeout(50)
                        # print 'stop sustain ' + str(playnote)
                if playnote in gvars.playingnotes:  # cleanup predecessors
                    for m in gvars.playingnotes[playnote]:
                        # print "stop note " + str(playnote)
                        m.fadeout(50)

            #### Replaced this with Hans' below
            # for n in gvars.sustainplayingnotes:
            #     if n.note == midinote:
            #         n.fadeout(500)
            # try:
            #     gvars.playingnotes.setdefault(midinote, []).append(
            #         gvars.samples[midinote, SelectVelocity, gvars.currvoice].play(midinote, velocity))
            try:
                if gvars.velocity_mode == gvars.VELSAMPLE:
                    velmixer = 127 * gvars.gain
                else:
                    velmixer = velocity * gvars.gain
                for n in range(len(gvars.chordnote[gvars.currchord])):
                    playnote = midinote + gvars.chordnote[gvars.currchord][n]
                    # print "start note " + str(playnote)
                    gvars.playingnotes.setdefault(playnote, []) \
                        .append(gvars.samples[playnote, velocity, gvars.currvoice].play(playnote, velmixer))
            except:
                print 'NoteOn entered exception routine'
                pass

        elif messagetype == 8:  # Note off
            midinote += gvars.globaltranspose
            if noteoff == True:
                # print 'Note off ' + str(note) + '->' + str(midinote) + ', voice=' + str(currvoice)    #debug
                if midinote in gvars.playingnotes:
                    for n in range(len(gvars.chordnote[gvars.currchord])):
                        playnote = midinote + gvars.chordnote[gvars.currchord][n]
                        for m in gvars.playingnotes[playnote]:
                            # print "stop note " + str(playnote)
                            if gvars.sustain:
                                # print 'Sustain note ' + str(playnote)   # debug
                                gvars.sustainplayingnotes.append(m)
                            else:
                                m.fadeout(50)
                    gvars.playingnotes[playnote] = []

        elif messagetype == 12:  # Program change
            # print 'Program change ' + str(note)
            if gvars.preset != note:
                gvars.preset = note
                loadsamples.LoadSamples()

        elif messagetype == 14:  # Pitch Bend
            gvars.PITCHBEND = (((128 * velocity + note) / gvars.pitchdiv) - gvars.pitchneutral) * gvars.pitchnotes

            # VOICE CHANGE
            # With MIDI mapping available, this is not necessary anymore

            # if (messagetype == 11) and (velocity == 127) and (note in voice_notes):
            #     if (note == voice_notes[0]):
            #         gvars.currvoice = 1
            #     if (note == voice_notes[1]):
            #         gvars.currvoice = 2
            #     if (note == voice_notes[2]):
            #         gvars.currvoice = 3
            #     if (note == voice_notes[3]):
            #         gvars.currvoice = 4
            #     print 'VOICE [' + str(gvars.currvoice) + ']'

        elif messagetype == 11:  # control change (CC, sometimes called Continuous Controllers)
            CCnum = note
            CCval = velocity

            # Default master volume control (CC7 is the universal standard)
            if (CCnum == 7):
                MasterVolume().setvolume(CCval)

            # Sustain pedal
            # NB: the microKEY conditionals are unique to Alex's modded keyboard. Remove in future.
            if (CCnum == 64):
                if gvars.sample_mode == gvars.PLAYLIVE:
                    if (CCval < 64) \
                            or (("microKEY" in src)
                                and (messagetype == 14)
                                and (CCnum == 64 or CCnum == 0)
                                and (CCval >= 28)) \
                                    and (gvars.sustain == True):  # sustain pedal off
                        for n in gvars.sustainplayingnotes:
                            n.fadeout(50)
                        gvars.sustainplayingnotes = []
                        gvars.sustain = False
                    elif (CCval >= 64) \
                            or (("microKEY" in src)
                                and (messagetype == 14)
                                and (CCnum == 64 or CCnum == 0)
                                and (CCval <= 25)) \
                                    and (gvars.sustain == False):  # sustain pedal on
                        gvars.sustain = True

            # general purpose 80 used for voices
            elif CCnum == 80:
                if CCval in gvars.voices:
                    gvars.currvoice = CCval
                    # lcd.display("")

            # general purpose 81 used for chords
            elif CCnum == 81:
                if CCval < len(gvars.chordnote):
                    gvars.currchord = CCval
                    # lcd.display("")

            # "All sounds off" or "all notes off"
            elif CCnum == 120 or CCnum == 123:
                AllNotesOff()
