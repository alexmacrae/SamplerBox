The config.ini
**************

The ``config.ini`` file contains settings for your SamplerBox.

.. note::

    In :ref:`system-mode-1` many of these settings are configurable from the menu. However an initial setup of this
    file is likely required.

Main configuration
==================

.. code-block:: text

    MAX_POLYPHONY = 80
    MIDI_CHANNEL = 0
    CHANNELS = 2
    BUFFERSIZE = 64
    SAMPLERATE = 44100
    GLOBAL_VOLUME = 87
    USE_BUTTONS = false
    USE_HD44780_16X2_LCD = false
    USE_HD44780_20x4_LCD = false
    USE_I2C_7SEGMENTDISPLAY = false
    USE_FREEVERB = true
    USE_TONECONTROL = false
    USE_SERIALPORT_MIDI = false
    SAMPLES_DIR = /media/media
    AUDIO_DEVICE_ID = 2
    MIXER_CARD_ID = 0
    MIXER_CONTROL = Speaker
    USE_ALSA_MIXER = false
    PRESET_BASE = 0
    AUDIO_DEVICE_NAME = your_device_name
    SYSTEM_MODE = 1
    MEMORY_LIMIT_PERCENTAGE = 10


System messages
===============

Useful for debugging issues (when connected to a screen or via SSH) and seeing what MIDI messages are being sent by a MIDI device.

.. code-block:: text

    PRINT_MIDI_MESSAGES = true
    PRINT_LCD_MESSAGES = true


System mode 1 controls
======================

Controls for controlling and navigating the SamplerBox when in :ref:`system-mode-1`.

If MIDI controls and/or GPIO pins connected to buttons are known, you may define them here.

.. note::

    When ``PRINT_MIDI_MESSAGES = true``, SamplerBox will return MIDI messages in the format required below.
    This only needs to be done once.

.. code-block:: text

    BUTTON_LEFT_MIDI = 176, 48, <nanoKONTROL2>
    BUTTON_RIGHT_MIDI = 176, 50, <nanoKONTROL2>
    BUTTON_ENTER_MIDI = 176, 49, <nanoKONTROL2>
    BUTTON_CANCEL_MIDI = 176, 65, <nanoKONTROL2>

    BUTTON_LEFT_GPIO = 26
    BUTTON_RIGHT_GPIO = 13
    BUTTON_ENTER_GPIO = 6
    BUTTON_CANCEL_GPIO = 12

System mode 2 controls
======================

Controls for controlling and navigating the SamplerBox when in :ref:`system-mode-2`.

If MIDI controls and/or GPIO pins connected to buttons are known, you may define them here.

.. note::

    When ``PRINT_MIDI_MESSAGES = true``, SamplerBox will return MIDI messages in the format required below.
    This only needs to be done once.

.. code-block:: text

    BUTTON_UP_MIDI = 176, 50, <nanoKONTROL2>
    BUTTON_DOWN_MIDI = 176, 48, <nanoKONTROL2>
    BUTTON_FUNC_MIDI = 176, 49, <nanoKONTROL2>

    BUTTON_UP_GPIO = 13
    BUTTON_DOWN_GPIO = 26
    BUTTON_FUNC_GPIO = 6

GPIO pin setup for HD44780 LCD modules
======================================

If you're using a HD44780 LCD module (16x2 or 20x4) you must define the numbers of the GPIO pins they are connected to here.

.. code-block:: text

    GPIO_LCD_RS = 7
    GPIO_LCD_E = 8
    GPIO_LCD_D4 = 27
    GPIO_LCD_D5 = 17
    GPIO_LCD_D6 = 18
    GPIO_LCD_D7 = 4

GPIO pin setup for a 7 segment display
======================================

If you're using a 7 segment display you must define the number of the GPIO pin it is connected to here.

.. code-block:: text

    GPIO_7SEG = 1

