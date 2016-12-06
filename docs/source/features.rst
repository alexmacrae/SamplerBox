Features
********

Basic features
==============

SamplerBox allows for the manipulation of some basic features such as ``preset change``, ``volume``, ``MIDI channel``,
``sustain``, ``pitch bend``, ``transpose``, and ``panic/kill sound``.


Two system modes
================

SamplerBox has two system modes available which is determined by the ``SYSTEM_MODE`` option in ``config.ini``.
:ref:`system-mode-1` (by Alex MacRae) has more advanced features such as setlist mode, ability to modify
system settings, MIDI mapping, and more. :ref:`system-mode-2` (by Hans Hommersom) is a simpler and arguably easier system
to use but with less features.

Voices
======

You can now define voices within presets via a sample-set's ``definition.txt`` file using the new parameter ``%voice``.

For example, ``piano_60_voice1.wav`` and ``piano_60_voice2.wav`` would be found with ``piano_%midinote_voice%voice.wav``.
To switch between voices (max of 4) you will need to using the :ref:`midi-mapping` function to
map your desired device controls.

Sample randomization
====================

If you have multiple versions of the same sample (eg different snare samples) you can number them. Then by using the
``%seq`` keyword in your definition.txt for the set, a random sample will be selected for playback.

Freeverb
========

A reverb module (`Freeverb <https://ccrma.stanford.edu/~jos/pasp/Freeverb.html>`_) is available. Thanks goes to
`Erik <http://www.nickyspride.nl/sb2/>`_ for this feature.

.. hint::

    You can map its parameters to MIDI controls via :ref:`midi-mapping`.

.. warning::

    If you experience performance issues, try setting ``USE_FREEVERB = false`` in ``config.ini``.

Auto-chords
===========

Builds and plays back a chord from a single note.

.. _menu-system:

Menu system
===========

A menu system is available to change the behaviour of the SamplerBox.

.. note::
    This feature assumes you have a `HD44780 LCD <https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller>`_
    module connected to your Raspberry Pi. You will need to define the GPIO pins you are connect to in the ``config.ini``.

.. warning::

    :ref:`system-mode-1` only

Setlist
=======

SamplerBox now manages your sample-sets with a setlist, so correct naming of your folders (with preceding ``01``,
``02``, ``03`` etc) isn't a requirement.

On startup new folders will be detected and appended to the end of the setlist. Using this menu system you can reorder
your sample-sets.

.. warning::

    :ref:`system-mode-1` only


Sample-set definition management
================================

:ref:`global-keywords` for every sample-set can be modified using this feature. This includes ``%%mode``,
``%%velmode``, ``%%release``, ``%%gain``, ``%%transpose`` and ``%%pitchbend``.

.. warning::

    :ref:`system-mode-1` only


MIDI mapping
============

Many features of the SamplerBox can be mapped to :ref:`midi-mapping`

.. warning::

    :ref:`system-mode-1` only

System settings
===============

Some of the system settings found in the ``config.ini`` file can be edited and saved from this menu.

More information in the :ref:`system-settings` section.

.. warning::

    :ref:`system-mode-1` only