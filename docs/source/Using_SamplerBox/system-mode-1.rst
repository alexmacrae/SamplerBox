.. _system-mode-1:

System mode 1
*************


A menu system has been implemented to access:

* :ref:`setlist-functions`
* Master volume
* :ref:`midi-mapping`
* :ref:`system-settings`

.. warning::

    This feature assumes you have a `HD44780 LCD <https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller>`_
    module wired to your Raspberry Pi. You will need to manually define the GPIO pins it is connected
    to in the ``config.ini`` file.

.. _setlist-functions:

Setlist functions
=================

SamplerBox now manages your sample-sets with a setlist, so correct naming of your folders isn't a requirement anymore.
On startup new folders will be detected and appended to the end of the setlist. Using the menu system you can reorder
your sample-sets.

+----------------------+---------------------------------------------------------------------------------------+
|Function              || Description                                                                          |
+======================+=======================================================================================+
|Rearrange             || Select a song and move it to a new position in the setlist using the                 |
|                      || left, right and enter buttons.                                                       |
+----------------------+---------------------------------------------------------------------------------------+
|Remove missing        || If a folder has been deleted, it will appear in the setlist with an asterisk (*)     |
|                      || beside it. This function removes missing folders from the setlist.                   |
+----------------------+---------------------------------------------------------------------------------------+
|Delete songs          || Select a song to delete from the setlist.                                            |
+----------------------+---------------------------------------------------------------------------------------+



.. _midi-mapping:

MIDI Mapping
============


+----------------------+-------------------------------------------------------------------------+
|Function to map       || Description                                                            |
+======================+=========================================================================+
|Master volume         || Map any control, ideally a fader or pot, to affect the SamplerBox's    |
|                      || master volume.                                                         |
+----------------------+-------------------------------------------------------------------------+
|Reverb                || Map any control, ideally a potentiometer, to any of the 5 reverb       |
|                      || parameters. Room size, damp, wet, dry, and width.                      |
+----------------------+-------------------------------------------------------------------------+
|Voices                || Map any control to each of the 4 voices.                               |
+----------------------+-------------------------------------------------------------------------+
|Sustain               || Map any control to the pedal sustain function. Useful if your          |
|                      || keyboard doesn't have a sustain pedal input.                           |
+----------------------+-------------------------------------------------------------------------+
|Pitch bend            || Map any control to the pitch bending function. Useful if your          |
|                      || keyboard doesn't have a pitch wheel.                                   |
+----------------------+-------------------------------------------------------------------------+
|Mod wheel             || Map any control to the mod wheel function. Useful if your keyboard     |
|                      || doesn't have a mod wheel.                                              |
+----------------------+-------------------------------------------------------------------------+
|SamplerBox Navigation || Map MIDI controls to each of the 4 navigation buttons (left, right,    |
|                      || enter and cancel). Mapping a control to one of these functions will not|
|                      || override any other controls mapped to the same function, thus allowing |
|                      || multiple mappings.                                                     |
+----------------------+-------------------------------------------------------------------------+


.. _system-settings:

System Settings
===============

Some system settings can be modified from this menu. Changing these options will save
their values to the ``config.ini`` and be read again upon a restart.

+-----------------+------------------------------------------------------------------------------+
|Option           || Description                                                                 |
+=================+==============================================================================+
|Max polyphony    || Range: 1-128. The maximum number of samples that can be played              |
|                 || simultaneously.                                                             |
+-----------------+------------------------------------------------------------------------------+
|MIDI channel     || Range: 0-13. 0 = all channels.                                              |
+-----------------+------------------------------------------------------------------------------+
|Audio device     || Select a different audio device from a list of ones available.              |
+-----------------+------------------------------------------------------------------------------+
|Audio channels   || Range: 2-4                                                                  |
|                 || The number of audio channels your audio device is capable of. 3 to 4        |
|                 || channels is currently experimental.                                         |
+-----------------+------------------------------------------------------------------------------+
|Sample rate      || Options: 44100, 48000.                                                      |
|                 || Choose a sample rate compatible with your audio device and sample-sets.     |
|                 || 44100 is usually safe.                                                      |
+-----------------+------------------------------------------------------------------------------+

