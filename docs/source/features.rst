Features
********

This is a modified version (and work in progress) of `Joseph Ernest's SamplerBox <https://github.com/josephernest/SamplerBox>`_,
as well as merged pieces from `Hans <http://homspace.xs4all.nl/homspace/samplerbox/index.html>`_ and
`Erik's SamplerBox2 <http://www.nickyspride.nl/sb2/>`_. The original samplerbox.py code was getting too big to manage
so it has been split up into modules.

Basic features
==============

SamplerBox allows for the manipulation of some basic features such as ``preset change``, ``volume``, ``MIDI channel``,
``sustain``, ``pitch bend``, ``transpose``, and ``panic/kill sound``.


Voices
======

You can now define voices within presets via a sample-set's ``definition.txt`` file using the new parameter ``%voice``.

For example, ``piano_60_voice1.wav`` and ``piano_60_voice2.wav`` would be found with ``piano_%midinote_voice%voice.wav``.
To switch between voices (max of 4) you will need to using the [MIDI Mapping](#user-content-midi-mapping) function to
map your desired device controls.

Sample randomization
====================

If you have multiple versions of the same sample (eg different snare samples) you can number them. Then by using the
``%seq`` keyword in your definition.txt for the set, a random sample will be selected for playback.

Freeverb
========

Reverb is available. You can map its parameters to MIDI controls via :ref:`midi-mapping`.

Thanks goes to `Erik <http://www.nickyspride.nl/sb2/>`_.

Auto-chords
===========

This function allows the playback of a chord from a single note.

.. _menu-system:

Menu system (System mode 1 only)
================================

A menu system is available in :ref:`system-mode-1` allowing the user to change the behaviour of the SamplerBox.

.. note::
    This feature also assumes you have a `HD44780 LCD <https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller>`_
    module connected to your Raspberry Pi. You will need to define the GPIO pins you are connect to in the ``config.ini`` file.

Setlist (System Mode 1 only)
============================

SamplerBox now manages your sample-sets with a setlist, so correct naming of your folders (with preceding ``01``,
``02``, ``03`` etc) isn't a requirement in this mode.

On startup new folders will be detected and appended to the end of the setlist. Using this menu system you can reorder
your sample-sets.

Sample-set definition management (System Mode 1 only)
=====================================================

:ref:`global-keywords` for every sample-set can be modified using this feature. This includes ``%%mode``,
``%%velmode``, ``%%release``, ``%%gain``, ``%%transpose`` and ``%%pitchbend``.

    
MIDI mapping (System mode 1 only)
=================================

Many features of the SamplerBox can be mapped to :ref:`midi-mapping`

System settings (System mode 1 only)
====================================

Some of the system settings found in the ``config.ini`` file can be edited and saved from this menu.

More information in the :ref:`system-settings` section.