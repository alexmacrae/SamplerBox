.. _config-ini:

Configuration
*************

The :ref:`config.ini <config-ini>` file contains settings for your SamplerBox. It is found in the ``/boot/samplerbox`` directory. The ``/boot`` partition is also accessible via a Windows or Mac machine.


.. note::

    If you have purchased a SamplerBox Player Pi HAT, the default configuration settings will work out of the box.

.. note::

    In :ref:`system-mode-1`'s :ref:`system settings <system-settings>` many of these settings are configurable from the menu system. However an initial setup of this file may be required.

Main configuration
==================

.. code-block:: text

    MAX_POLYPHONY = 40
    MIDI_CHANNEL = 1
    SAMPLERATE = 44100
    GLOBAL_VOLUME = 100
    USE_FREEVERB = False
    USE_I2C_7SEGMENTDISPLAY = False
    USE_SERIALPORT_MIDI = False
    USE_TONECONTROL = False
    USE_HD44780_16X2_LCD = True
    USE_HD44780_20X4_LCD = False
    USE_BUTTONS = True
    USE_GUI = False
    SAMPLES_DIR = None
    AUDIO_DEVICE_ID = -1
    AUDIO_DEVICE_NAME = autodetect
    BOXRELEASE = 30
    PRESET_BASE = 0
    SYSTEM_MODE = 1
    RAM_LIMIT_PERCENTAGE = 40
    INVERT_SUSTAIN = False


.. note::

    ``USE_FREEVERB`` may cause pops and clicks.

    ``RAM_LIMIT_PERCENTAGE`` determines how much RAM can be used for loading samples. This allows for preloading of sample-sets following the current one and, depending on
    the size of the library, seamless preset navigation.

System messages
===============

Useful for debugging issues (when connected to a screen or via SSH) and seeing what MIDI messages are being sent by a MIDI device.

.. code-block:: text

    PRINT_MIDI_MESSAGES = True
    PRINT_LCD_MESSAGES = True

GPIO pin setup for HD44780 LCD modules
======================================

If you're using a HD44780 LCD module (16x2 or 20x4) you must define the numbers of the GPIO pins they are connected to here.

.. code-block:: text

    GPIO_LCD_RS = 7
    GPIO_LCD_E = 8
    GPIO_LCD_D7 = 4
    GPIO_LCD_D6 = 18
    GPIO_LCD_D5 = 17
    GPIO_LCD_D4 = 27

System mode 1 controls
======================

Controls for controlling and navigating the SamplerBox when in :ref:`system-mode-1`.

If MIDI controls and/or GPIO pins connected to buttons are known, you may define them here.

.. note::

    When ``PRINT_MIDI_MESSAGES = true``, SamplerBox will return MIDI messages in the format required below.
    This only needs to be done once.

.. code-block:: text

    BUTTON_LEFT_MIDI = 176, 48, <MIDI CONTROLLER NAME>
    BUTTON_RIGHT_MIDI = 176, 50, <MIDI CONTROLLER NAME>
    BUTTON_ENTER_MIDI = 176, 49, <MIDI CONTROLLER NAME>
    BUTTON_CANCEL_MIDI = 176, 65, <MIDI CONTROLLER NAME>

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

    BUTTON_UP_MIDI = 176, 50, <MIDI CONTROLLER NAME>
    BUTTON_DOWN_MIDI = 176, 48, <MIDI CONTROLLER NAME>
    BUTTON_FUNC_MIDI = 176, 49, <MIDI CONTROLLER NAME>

    BUTTON_UP_GPIO = 13
    BUTTON_DOWN_GPIO = 26
    BUTTON_FUNC_GPIO = 6



GPIO pin setup for a 7 segment display
======================================

If you're using a 7 segment display you must define the number of the GPIO pin it is connected to here. This is not recommended as navigating the system menus with feedback is (near) impossible.

.. code-block:: text

    GPIO_7SEG = 1

