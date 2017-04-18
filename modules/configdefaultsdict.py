configdefaults = {
    'MAX_POLYPHONY': {'type': 'range', 'min': 1, 'max': 128, 'default': 80, 'section': 'SAMPLERBOX CONFIG'},
    'MIDI_CHANNEL': {'type': 'range', 'min': 1, 'max': 16, 'default': 1, 'section': 'SAMPLERBOX CONFIG'},
    'CHANNELS': {'type': 'options', 'options': ['2', '4'], 'default': 2, 'section': 'SAMPLERBOX CONFIG'},
    'BUFFERSIZE': {'type': 'options',
                   'options': ['16', '32', '64', '128', '256', '512', '1024', '2048'], 'default': 64, 'section': 'SAMPLERBOX CONFIG'},
    'SAMPLERATE': {'type': 'options', 'options': ['44100', '48000', '96000'], 'default': 44100, 'section': 'SAMPLERBOX CONFIG'},
    'GLOBAL_VOLUME': {'type': 'range', 'min': '0', 'max': 100, 'default': 100, 'section': 'SAMPLERBOX CONFIG'},
    'USE_BUTTONS': {'type': 'boolean', 'default': True, 'section': 'SAMPLERBOX CONFIG'},
    'USE_HD44780_16X2_LCD': {'type': 'boolean', 'default': True, 'section': 'SAMPLERBOX CONFIG'},
    'USE_HD44780_20x4_LCD': {'type': 'boolean', 'default': False, 'section': 'SAMPLERBOX CONFIG'},
    'USE_I2C_7SEGMENTDISPLAY': {'type': 'boolean', 'default': False, 'section': 'SAMPLERBOX CONFIG'},
    'USE_FREEVERB': {'type': 'boolean', 'default': False, 'section': 'SAMPLERBOX CONFIG'},
    'USE_TONECONTROL': {'type': 'boolean', 'default': False, 'section': 'SAMPLERBOX CONFIG'},
    'USE_SERIALPORT_MIDI': {'type': 'boolean', 'default': False, 'section': 'SAMPLERBOX CONFIG'},
    'SAMPLES_DIR': {'type': 'string', 'default': 'None', 'section': 'SAMPLERBOX CONFIG'},
    'PRESET_BASE': {'type': 'int', 'default': 0, 'section': 'SAMPLERBOX CONFIG'},
    'AUDIO_DEVICE_ID': {'type': 'int', 'default': -1, 'section': 'SAMPLERBOX CONFIG'},
    'AUDIO_DEVICE_NAME': {'type': 'options', 'options': [], 'default': 'autodetect', 'section': 'SAMPLERBOX CONFIG'},
    'SYSTEM_MODE': {'type': 'options', 'options': ['1', '2'], 'default': 1, 'section': 'SAMPLERBOX CONFIG'},
    'RAM_LIMIT_PERCENTAGE': {'type': 'range', 'min': 0, 'max': 95, 'default': 40, 'section': 'SAMPLERBOX CONFIG'},
    'BOXRELEASE': {'type': 'range', 'min': 1, 'max': 128, 'default': 30, 'section': 'SAMPLERBOX CONFIG'},
    'USE_GUI': {'type': 'boolean', 'default': False, 'section': 'SAMPLERBOX CONFIG'},

    'PRINT_MIDI_MESSAGES': {'type': 'boolean', 'default': True, 'section': 'MISC'},
    'PRINT_LCD_MESSAGES': {'type': 'boolean', 'default': True, 'section': 'MISC'},

    'BUTTON_LEFT_MIDI': {'type': 'midi', 'default': 'None', 'section': 'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 1'},
    'BUTTON_RIGHT_MIDI': {'type': 'midi', 'default': 'None', 'section': 'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 1'},
    'BUTTON_ENTER_MIDI': {'type': 'midi', 'default': 'None', 'section': 'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 1'},
    'BUTTON_CANCEL_MIDI': {'type': 'midi', 'default': 'None', 'section': 'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 1'},

    'BUTTON_UP_MIDI': {'type': 'midi', 'default': 'None', 'section': 'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 2'},
    'BUTTON_DOWN_MIDI': {'type': 'midi', 'default': 'None', 'section': 'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 2'},
    'BUTTON_FUNC_MIDI': {'type': 'midi', 'default': 'None', 'section': 'MIDI BUTTON NAVIGATION FOR SYSTEM MODE 2'},

    'BUTTON_LEFT_GPIO': {'type': 'int', 'default': 26, 'section': 'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 1'},
    'BUTTON_RIGHT_GPIO': {'type': 'int', 'default': 13, 'section': 'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 1'},
    'BUTTON_ENTER_GPIO': {'type': 'int', 'default': 6, 'section': 'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 1'},
    'BUTTON_CANCEL_GPIO': {'type': 'int', 'default': 12, 'section': 'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 1'},

    'BUTTON_UP_GPIO': {'type': 'int', 'default': 13, 'section': 'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 2'},
    'BUTTON_DOWN_GPIO': {'type': 'int', 'default': 26, 'section': 'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 2'},
    'BUTTON_FUNC_GPIO': {'type': 'int', 'default': 6, 'section': 'GPIO BUTTONS PIN SETUP FOR SYSTEM MODE 2'},

    'GPIO_LCD_RS': {'type': 'int', 'default': 7, 'section': 'GPIO LCD HD44780 PIN SETUP'},
    'GPIO_LCD_E': {'type': 'int', 'default': 8, 'section': 'GPIO LCD HD44780 PIN SETUP'},
    'GPIO_LCD_D4': {'type': 'int', 'default': 27, 'section': 'GPIO LCD HD44780 PIN SETUP'},
    'GPIO_LCD_D5': {'type': 'int', 'default': 17, 'section': 'GPIO LCD HD44780 PIN SETUP'},
    'GPIO_LCD_D6': {'type': 'int', 'default': 18, 'section': 'GPIO LCD HD44780 PIN SETUP'},
    'GPIO_LCD_D7': {'type': 'int', 'default': 4, 'section': 'GPIO LCD HD44780 PIN SETUP'},

    'GPIO_7SEG': {'type': 'int', 'default': 1, 'section': 'GPIO FOR A 7 SEGMENT DISPLAY'}

}

if __name__ == "__main__":
    import configparser_samplerbox

    cp = configparser_samplerbox.Setup('../config.ini')

    for c in configdefaults.iteritems():

        cp.update_config(section=c[1].get('section'), option=c[0], value=c[1].get('default'))
