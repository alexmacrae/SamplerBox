""" Parse config.ini settings into SamplerBox


"""
import configparser
import os
import sys
from os import path

print_config = False


if path.basename(sys.modules['__main__'].__file__) == "samplerbox.py":
    import globalvars as gv
    print_config = gv.CONFIG_PRINT
    CONFIG_FILE_PATH = "/media/config.ini"
    if not os.path.exists(CONFIG_FILE_PATH):
        CONFIG_FILE_PATH = "/boot/config.ini"
        if not os.path.exists(CONFIG_FILE_PATH):
            CONFIG_FILE_PATH = "./config.ini"
else:
    CONFIG_FILE_PATH = "../config.ini"
    print_config = True

# CONFIG_FILE_PATH = "./config.ini"
# print_config = True


config = configparser.ConfigParser(allow_no_value=True)
config.optionxform = str  # allows case sensitivity


def get_option_by_name(option_name):
    option_name = option_name.upper()

    value_in_config = None
    if config.read(CONFIG_FILE_PATH):

        for section in config.sections():
            for name, value in config.items(section):

                if name.upper() == option_name:
                    value_in_config = value
                    if str(value_in_config).lower() == 'true':
                        value_in_config = True
                    if str(value_in_config).lower() == 'false':
                        value_in_config = False

    if value_in_config != None:
        if print_config: print option_name, ' = ', value_in_config
        return value_in_config

    else:
        print 'Error in config.ini'
        pass

def update_config(section, option, value):
    # Comments need to be written again.
    # ConfigObj looks like it can update ini files while preserving comments:
    # http://stackoverflow.com/questions/21476554/update-ini-file-without-removing-comments
    # http://www.voidspace.org.uk/python/configobj.html
    # Have had a play below (config2) - will revisit in the future.
    config.set('README',
               '; WARNING: Any comments written here will be overwritten by SamplerBox when using the menu system. Additions and changes to comments must be made to configparser_samplerbox.py')

    config.set('MISC',
               '; Prints midi messages in the format: messagetype, note <DeviceName>. eg 176, 60, <LaunchKey 61>')

    config.set('MIDI BUTTON NAVIGATION FOR SYSTEM MODE 1', '; Assign MIDI controls or notes to menu navigation.\r\
; MIDI message + device: with print_midi_messages set to True, you can see what messages your device is sending. <devicename> is optional. eg button_left = 176, 60, <LaunchKey 61>\r\
; GPIO: The number of the GPIO pin the button is connected to. eg button_left = GPIO7\r\
; Notes: Not ideal, but useable if you have no alternative. <devicename> is optional. eg button_left = C1, F#2 etc.')

    config.set('GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 1',
               '; For buttons connected to GPIO pins, USE_BUTTONS must be True')

    config.set(section, option.upper(), value)

    with open(CONFIG_FILE_PATH, 'w') as fp:
        config.write(fp)

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
