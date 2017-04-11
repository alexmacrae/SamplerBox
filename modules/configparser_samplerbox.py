""" Parse config.ini settings into SamplerBox

"""
import configparser
import configdefaultsdict as cdd

class Setup:
    def __init__(self, config_file_path):

        self.configdefaults = cdd.configdefaults

        self.CONFIG_FILE_PATH = config_file_path
        self.print_config = True

        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.optionxform = str  # allows case sensitivity

    def get_option_by_name(self, option_name):
        option_name = option_name.upper()

        value_in_config = None
        if self.config.read(self.CONFIG_FILE_PATH):

            for section in self.config.sections():
                for name, value in self.config.items(section):

                    if name.upper() == option_name:
                        value_in_config = value
                        if str(value_in_config).lower() == 'true':
                            value_in_config = True
                        if str(value_in_config).lower() == 'false':
                            value_in_config = False

        if value_in_config != None:
            if self.print_config: print option_name, ' = ', value_in_config
            return value_in_config

        else:
            print 'Error in config.ini @ %s' % option_name
            pass

    def update_config(self, section, option, value):
        # Comments need to be written again.
        # ConfigObj looks like it can update ini files while preserving comments:
        # http://stackoverflow.com/questions/21476554/update-ini-file-without-removing-comments
        # http://www.voidspace.org.uk/python/configobj.html
        # Have had a play below (config2) - will revisit in the future.

        value = str(value) # convert numbers to strings

        sections = ['README', 'SAMPLERBOX CONFIG', 'MISC', 'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 1',
                    'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 2', 'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 1',
                    'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 2', 'GPIO LCD HD44780 PIN SETUP',
                    'GPIO FOR A 7 SEGMENT DISPLAY']

        # If sections don't exist in the config.ini, create them
        for s in sections:
            if not self.config.has_section(s): self.config.add_section(s)

        self.config.set('README',
'; WARNING: Any comments written here will be overwritten by SamplerBox when using the menu system.\r\
; Additions and changes to comments must be made to configparser_samplerbox.py')

        self.config.set('MISC',
'; Outputs LCD messages to the console on a single line. Line breaks are represented by a double pipe: || \r\
; Outputs MIDI messages to the console in this format: messagetype, note <DeviceName>. eg 176, 60, <LaunchKey 61>')

        self.config.set('MIDI BUTTON NAVIGATION FOR SYSTEM MODE 1',
'; Assign MIDI controls or notes to menu navigation in system mode 1.\r\
; MIDI message + device: with print_midi_messages set to True, you can see what messages your device is sending.\r\
; eg button_left = 176, 60, <LaunchKey 61> (<devicename> is optional) \r\
; Can use keyboard notes as navigation. This is not ideal, but useable if you have no alternative.\r\
; eg button_left = F#2, <microKEY-61> (<devicename> is optional)')

        self.config.set('MIDI BUTTON NAVIGATION FOR SYSTEM MODE 2',
'; Assign MIDI controls or notes to menu navigation in system mode 2.\r\
; MIDI message + device: with print_midi_messages set to True, you can see what messages your device is sending.\r\
; eg button_left = 176, 60, <LaunchKey 61> (<devicename> is optional) \r\
; Can use keyboard notes as navigation. This is not ideal, but useable if you have no alternative.\r\
; eg button_left = F#2, <microKEY-61> (<devicename> is optional)')

        self.config.set('GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 1',
'; GPIO: The number of the GPIO pin the button is connected to. eg button_left = GPIO7\r\
; For buttons connected to GPIO pins, USE_BUTTONS must be True')
        self.config.set('GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 2',
'; GPIO: The number of the GPIO pin the button is connected to. eg button_left = GPIO7\r\
; For buttons connected to GPIO pins, USE_BUTTONS must be True')

        self.config.set('GPIO LCD HD44780 PIN SETUP',
'; If you\'re using a 16x2 or 20x4 character LCD module, define its GPIO pins here')

        self.config.set('GPIO FOR A 7 SEGMENT DISPLAY',
'; If you\'re using a 7 segment display, define its GPIO pin here')

        self.config.set(section, option.upper(), value)

        with open(self.CONFIG_FILE_PATH, 'w') as fp:
            self.config.write(fp)

            # from configobj import ConfigObj
            # config2 = ConfigObj("config.ini")
            #
            # def get_config_item_by_name2(option_name):
            #     option_name = option_name.upper()
            #
            #     value_in_config = None
            #
            #     for section, obj in config2.iteritems():
            #
            #         print section
            #         for o in obj.iteritems():
            #             print o
            #
            #         # if name.upper() == option_name:
            #         #     print name, value
            #         #     value_in_config = value
            #         #     if str(value_in_config).lower() == 'true':
            #         #         value_in_config = True
            #         #     if str(value_in_config).lower() == 'false':
            #         #         value_in_config = False
            #
            #     if value_in_config != None:
            #         print option_name, ' = ', value_in_config
            #         return value_in_config
            #
            #     else:
            #         return DEFAULTS.get(option_name)
            #
            #
            # get_config_item_by_name2('MAX_POLYPHONY')


    def build_config_from_defaults(self):
        for c in self.configdefaults.iteritems():
            self.update_config(section=c[1].get('section'), option=c[0], value=c[1].get('default'))