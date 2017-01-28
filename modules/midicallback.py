import globalvars as gv
import loadsamples
import time
import random
import exceptions


def noteon(messagetype, note, vel):
    # print messagetype, note, vel
    pass


def noteoff(messagetype, note, vel):
    # print messagetype, note, vel
    pass


#########################################
# MIDI CALLBACK
#########################################

def MidiCallback(src, message, time_stamp):
    midimaps = gv.midimaps
    src = src[:src.rfind(" "):]  # remove the port number from the end

    messagetype = message[0] >> 4
    midichannel = (message[0] & 15) + 1

    note = message[1] if len(message) > 1 else None
    midinote = note
    velocity = message[2] if len(message) > 2 else None
    noteoff = False
    last_note_timestamp = 0
    if gv.sample_mode == gv.PLAYLIVE:
        noteoff = True

    if gv.PRINT_MIDI_MESSAGES:
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

    if gv.SYSTEM_MODE == 1:

        if gv.learningMode and messagetype != 8:  # don't send note-offs
            message_to_match = [message[0], note, str(src)]
            all_sys_buttons = [gv.BUTTON_LEFT_MIDI, gv.BUTTON_RIGHT_MIDI, gv.BUTTON_ENTER_MIDI,
                               gv.BUTTON_CANCEL_MIDI, gv.BUTTON_UP_MIDI, gv.BUTTON_DOWN_MIDI, gv.BUTTON_FUNC_MIDI]
            if message_to_match in all_sys_buttons:
                print 'This MIDI control has been assigned to %s in the config.ini. Will not be mapped.' \
                      % str(str(message) + src)
            else:
                gv.nav.state.sendControlToMap(message, src)
                return  # don't continue from here

        ######################
        # Check if MIDI Mapped
        ######################
        try:
            messageKey = (message[0], message[1])
            if midimaps.get(src).has_key(messageKey):
                # remap note to a function
                if midimaps.get(src).get(messageKey).has_key('fn'):

                    try:
                        # Runs method from class. ie ac.master_volume.setvolume(velocity).
                        # No doubt there's a better way to do this
                        fn = midimaps.get(src).get(messageKey).get('fn')
                        if (fn.split('.')[-1] == 'set_pitch'):
                            eval(fn)(velocity, note)
                        elif (fn.split('.')[-1] == 'set_sustain'):
                            eval(fn)(message, src, messagetype)
                        else:
                            eval(fn)(velocity)
                    except:
                        # For functions that don't take velocity. eg menu navigation
                        if velocity > 0:
                            eval(midimaps.get(src).get(messageKey).get('fn'))()

                            # remap note to a key
                elif isinstance(midimaps.get(src).get(messageKey).get('note'), int):
                    note = midimaps.get(src).get(messageKey).get('note')

        except:
            # print "MIDI message isn't mapped, or it is and it failed" # debug
            pass

    ######################
    # Button navigation
    # Determined by config
    ######################

    enter = gv.BUTTON_ENTER_MIDI
    left = gv.BUTTON_LEFT_MIDI
    right = gv.BUTTON_RIGHT_MIDI
    cancel = gv.BUTTON_CANCEL_MIDI

    up = gv.BUTTON_UP_MIDI
    down = gv.BUTTON_DOWN_MIDI
    func = gv.BUTTON_FUNC_MIDI

    if gv.SYSTEM_MODE == 1:
        if message[0] == enter[0] and note == enter[1] and velocity > 0 and enter[2] in src:  # Enter arrow button
            gv.nav.state.enter()

        elif message[0] == left[0] and note == left[1] and velocity > 0 and left[2] in src:  # Left arrow button
            gv.nav.state.left()

        elif message[0] == right[0] and note == right[1] and velocity > 0 and right[2] in src:  # Right arrow button
            gv.nav.state.right()

        elif message[0] == cancel[0] and note == cancel[1] and velocity > 0 and cancel[2] in src:  # Cancel button
            gv.nav.state.cancel()

    elif gv.SYSTEM_MODE == 2:
        if message[0] == up[0] and note == up[1] and velocity > 0 and up[2] in src:  # Enter arrow button
            gv.nav.up()

        elif message[0] == down[0] and note == down[1] and velocity > 0 and down[2] in src:  # Left arrow button
            gv.nav.down()

        elif message[0] == func[0] and note == func[1] and velocity > 0 and func[2] in src:  # Right arrow button
            gv.nav.func()

    ######################
    # Do default MIDI functions
    ######################

    #if (midichannel == gv.MIDI_CHANNEL or gv.MIDI_CHANNEL <= 0) and (gv.midi_mute == False):
    if gv.midi_mute == False:

        if messagetype == 9:  # is a note-off hidden in this note-on ?
            if velocity == 0:  # midi protocol, next elif's are SB's special modes
                messagetype = 8  # noteoff must be true here :-)
            elif (gv.sample_mode == gv.PLAYSTOP or gv.sample_mode == gv.PLAYLOOP) and midinote > 63:
                messagetype = 8
                midinote = midinote - 64
                noteoff = True
            elif gv.sample_mode == gv.PLAYLO2X and midinote in gv.playingnotes:
                if gv.playingnotes[midinote] != []:
                    messagetype = 8
                    noteoff = True

        if messagetype == 9:  # Note on

            midinote += gv.globaltranspose
            actual_preset = gv.samples_indices[gv.preset]

            try:
                # scale the selected sample based on velocity, the volume will be kept,
                # this will normally make the sound brighter (by Erik)

                # TODO: make VelocitySelectionOffset a system setting effectively adjusting the sensitivity of a device

                select_velocity = (velocity * (127 - gv.VelocitySelectionOffset) / 127) \
                                  + gv.VelocitySelectionOffset

                if gv.velocity_mode == gv.VELSAMPLE:
                    velmixer = 127 * gv.gain
                else:
                    velmixer = velocity * gv.gain

                if gv.SYSTEM_MODE > 0:

                    note_index = midinote % 12 - gv.ac.autochorder.current_key_index
                    chord_index = gv.ac.autochorder.current_chord_mode[note_index]

                    for n in range(len(gv.ac.autochorder.CHORD_NOTES[chord_index])):
                        playnote = midinote + gv.ac.autochorder.CHORD_NOTES[chord_index][n]
                        for m in gv.sustainplayingnotes:  # safeguard polyphony; don't sustain double notes
                            if m.note == playnote:
                                m.fadeout(50)
                                # print 'clean sustain ' + str(playnote)
                        if gv.triggernotes[midichannel][playnote] < 128:  # cleanup in case of retrigger
                            if playnote in gv.playingnotes[midichannel]:  # occurs in once/loops modes and chords)
                                for m in gv.playingnotes[midichannel][playnote]:
                                    # print "clean note " + str(playnote)
                                    m.fadeout(50)
                                gv.playingnotes[midichannel][playnote] = []  # housekeeping
                        # Start David Hilowitz
                        # Get the list of available samples for this note and velocity
                        notesamples = gv.samples[actual_preset][playnote, velocity, gv.currvoice, midichannel]
                        # Choose a sample from the list
                        sample = random.choice(notesamples)
                        # If we have no value for lastplayedseq, set it to 0
                        gv.lastplayedseq.setdefault(playnote, 0)
                        # If we have more than 2 samples to work with, reject duplicates
                        if len(notesamples) >= 3:
                            while sample.seq == gv.lastplayedseq[playnote]:
                                sample = random.choice(notesamples)
                        # End David Hilowitz
                        gv.triggernotes[midichannel][playnote] = midinote  # we are last playing this one
                        # print "start note " + str(playnote)
                        gv.playingnotes[midichannel].setdefault(playnote, []).append(
                            sample.play(playnote, velmixer))
                        gv.lastplayedseq[playnote] = sample.seq  # David Hilowitz

            except:
                raise exceptions.NoteOnError, 'Couldn\'t play note'
                pass

            
            
        elif messagetype == 8:  # Note off
            midinote += gv.globaltranspose
            if noteoff == True:

                if gv.SYSTEM_MODE > 0:
                    for playnote in xrange(128):
                        if gv.triggernotes[midichannel][playnote] == midinote:  # did we make this one play ?
                            if playnote in gv.playingnotes[midichannel]:
                                for m in gv.playingnotes[midichannel][playnote]:
                                    if gv.sustain:
                                        # print 'Sustain note ' + str(playnote)   # debug
                                        gv.sustainplayingnotes.append(m)
                                    else:
                                        # print "stop note " + str(playnote)
                                        m.fadeout(50)
                                # gv.playingnotes[playnote] = []
                                gv.playingnotes[midichannel].pop(playnote)
                            gv.triggernotes[midichannel][playnote] = 128  # housekeeping



        elif messagetype == 12:  # Program change
            # print 'Program change ' + str(note)
            if gv.preset != note:
                gv.preset = note
                loadsamples.LoadSamples()

        elif messagetype == 14:  # Pitch Bend

            gv.ac.pitchbend.set_pitch(velocity, note)

        elif messagetype == 11:  # control change (CC, sometimes called Continuous Controllers)
            CCnum = note
            CCval = velocity

            # Default master volume control (CC7 is the universal standard)
            if (CCnum == 7):
                gv.ac.master_volume.setvolume(CCval)

            # Sustain pedal
            elif (CCnum == 64):
                gv.ac.sustain.set_sustain(message, src, messagetype)

            # general purpose 80 used for voices
            elif CCnum == 80:
                if CCval in gv.voices:
                    gv.ac.voice.change(CCval)
                    # lcd.display("")

            # general purpose 81 used for chords
            elif CCnum == 81:
                if CCval < len(gv.CHORD_NOTES):
                    gv.ac.autochorder.change()

            # "All sounds off" or "all notes off"
            elif CCnum == 120 or CCnum == 123:
                gv.ac.all_notes_off()

            elif CCnum == 72:  # Sound controller 3 = release time
                gv.PRERELEASE = CCval

            elif CCnum == 82:        # Pitch bend sensitivity (my controller cannot send RPN)
                gv.pitchnotes = (24*CCval+100)/127