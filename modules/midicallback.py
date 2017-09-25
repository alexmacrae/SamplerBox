import globalvars as gv
from re import search

def remove_number_dash_space(str):
    # removes the pattern "[0-9]- " from start. eg "5- LaunchKey" = "LaunchKey". When the system numbers devices like
    # this, mapped controls are not found. This function solves the issue.
    reobj = search('(?<=[0-9]- ).*', str)
    if reobj:
        str = reobj.group()
    return str

class Midi:
    def __init__(self):
        ########################
        # Button navigation    #
        # Determined by config #
        ########################

        self.enter = gv.BUTTON_ENTER_MIDI
        self.left = gv.BUTTON_LEFT_MIDI
        self.right = gv.BUTTON_RIGHT_MIDI
        self.cancel = gv.BUTTON_CANCEL_MIDI

        self.up = gv.BUTTON_UP_MIDI
        self.down = gv.BUTTON_DOWN_MIDI
        self.func = gv.BUTTON_FUNC_MIDI

        self.panic_key = gv.PANIC_KEY

    def noteon(self, messagetype, note, vel):
        # print messagetype, note, vel
        pass

    def noteoff(self, messagetype, note, vel):
        # print messagetype, note, vel
        pass

    #################
    # MIDI CALLBACK #
    #################

    def callback(self, src, message, time_stamp):

        gv.ls.midi_detected = True

        midimaps = gv.midimaps
        src = src[:src.rfind(" "):]  # remove the port number from the end
        src = remove_number_dash_space(src) # remove the pattern "[0-9]- " from start. eg "5- LaunchKey" = "LaunchKey"

        messagetype = message[0] >> 4
        midichannel = (message[0] & 15) + 1

        note = message[1] if len(message) > 1 else None
        midinote = note
        velocity = message[2] if len(message) > 2 else None
        noteoff = True

        if gv.sample_mode == gv.PLAYLIVE:
            noteoff = True
        elif gv.sample_mode == gv.PLAYONCE:
            noteoff = False

        if gv.PRINT_MIDI_MESSAGES:
            print '%d, %d, <%s>' % (message[0], note, src)

        ##########################################
        # MIDI Learning                          #
        # Send messages when learningMode is set #
        ##########################################

        messageKey = mk = (message[0], message[1])

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

            ########################
            # Check if MIDI Mapped #
            ########################

            try:

                # Check for MIDI map match from the config.ini

                if mk[0] == self.enter[0] and mk[1] == self.enter[1] and velocity > 0:  # Enter button
                    if len(self.enter) == 2 or len(self.enter) == 3 and src in self.enter[2]:
                        gv.nav.state.enter()
                        return
                elif mk[0] == self.left[0] and mk[1] == self.left[1] and velocity > 0:  # Left button
                    if len(self.left) == 2 or len(self.left) == 3 and src in self.left[2]:
                        gv.nav.state.left()
                        return
                elif mk[0] == self.right[0] and mk[1] == self.right[1] and velocity > 0:  # Right button
                    if len(self.right) == 2 or len(self.right) == 3 and src in self.right[2]:
                        gv.nav.state.right()
                        return
                elif mk[0] == self.cancel[0] and mk[1] == self.cancel[1] and velocity > 0:  # Cancel button
                    if len(self.cancel) == 2 or len(self.cancel) == 3 and src in self.cancel[2]:
                        gv.nav.state.cancel()
                        return
                elif mk[0] == self.panic_key[0] and mk[1] == self.panic_key[1]:  # Panic key
                    if len(self.panic_key) == 2 or len(self.panic_key) == 3 and src in self.panic_key[2]:
                        gv.ac.panic()
                        return
            except:
                #print "This MIDI message hasn't been assigned in config.ini -- skipping" # debug
                pass

            try:
                # Now check for MIDI mappings that the user may have defined from within the menu system

                if midimaps.get(src).has_key(messageKey):

                    # Remap note/control to a function

                    if midimaps.get(src).get(messageKey).has_key('fn'):

                        try:
                            # Runs method from class. ie ac.master_volume.setvolume(velocity).
                            # TODO: there must be a more elegant way to do this ;)
                            fn = midimaps.get(src).get(messageKey).get('fn')
                            fn_name = fn.split('.')[-1]
                            if fn_name == 'set_pitch':
                                eval(fn)(velocity, note)
                            elif fn_name == 'set_sustain':
                                eval(fn)(message, src, messagetype)
                            elif fn_name == 'panic':
                                eval(fn)()
                            else:
                                eval(fn)(velocity)
                        except:
                            # For functions that don't take velocity. eg menu navigation
                            if velocity > 0:
                                eval(midimaps.get(src).get(messageKey).get('fn'))()

                                # remap note to a key
                    elif isinstance(midimaps.get(src).get(messageKey).get('note'), int):
                        note = midimaps.get(src).get(messageKey).get('note')

                    return # Stop here. Control has been mapped - don't perform any other MIDI functions below

            except:
                #print "MIDI message isn't mapped, or it is and it failed" # debug
                pass

        elif gv.SYSTEM_MODE == 2:

            try:
                # Up / next preset
                if mk[0] == self.up[0] and mk[1] == self.up[1] and velocity > 0:
                    if len(self.up) == 2 or len(self.up) == 3 and self.up[2] in src:
                        gv.nav.up()
                        return
                # Down / previous preset
                elif mk[0] == self.down[0] and mk[1] == self.down[1] and velocity > 0:
                    if len(self.down) == 2 or len(self.down) == 3 and self.down[2] in src:
                        gv.nav.down()
                        return
                # Function button
                elif mk[0] == self.func[0] and mk[1] == self.func[1] and velocity > 0:
                    if len(self.func) == 2 or len(self.func) == 3 and self.func[2] in src:
                        gv.nav.func()
                        return
            except:
                # print 'MIDI error: menu navigation MIDI settings not set correctly in config.ini'
                pass

        ##############################
        # Do default MIDI operations #
        ##############################

        # if (midichannel == gv.MIDI_CHANNEL or gv.MIDI_CHANNEL <= 0) and (gv.midi_mute == False): # MIDI_CHANNEL = 0 is omni mode (accepts all MIDI channels)
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

                gv.ac.noteon(midinote=midinote, midichannel=midichannel, velocity=velocity)

            elif messagetype == 8:  # Note off

                if noteoff == True:
                    gv.ac.noteoff(midinote=midinote, midichannel=midichannel)


            elif messagetype == 12:  # Program change
                # print 'Program change ' + str(note)
                if gv.preset != note:
                    gv.preset = note
                    gv.ls.load_preset()

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
                    if CCval < len(gv.autochorder.CHORD_NOTES):
                        gv.ac.autochorder.change()

                # "All sounds off" or "all notes off"
                elif CCnum == 120 or CCnum == 123:
                    gv.ac.panic()

                elif CCnum == 72:  # Sound controller 3 = release time
                    gv.PRERELEASE = CCval

                elif CCnum == 82:  # Pitch bend sensitivity (my controller cannot send RPN)
                    gv.pitchnotes = (24 * CCval + 100) / 127

