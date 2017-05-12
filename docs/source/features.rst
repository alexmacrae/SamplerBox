Features
********

Basic features
==============

SamplerBox allows for the manipulation of some basic features such as ``preset changing``, ``sample looping``,  ``velocity sensitivity``, ``volume``,
``sustain``, ``pitch bend``, ``transpose``, ``playback mode``, and ``voices``.


Two system modes
================

SamplerBox has two system modes available which is determined by the ``SYSTEM_MODE`` option in :ref:`config.ini <config-ini>`.

:ref:`system-mode-1` (by Alex MacRae) has more advanced features such as setlist mode, ability to modify
system settings, MIDI mapping, and more. :ref:`system-mode-2` (by Hans Hommersom) is a simpler and easier system
to use but with less features.

This section requires that you have an understanding of how :ref:`definition.txt files <definition-files>` work

Accurate velocity
=================



Examples :ref:`here <definition-examples>`.

Voices
======

You can now define up to 4 voices within presets via a sample-set's ``definition.txt`` file using the parameter ``%voice``.

For example, ``piano_60_v1.wav`` and ``juno_60_v2.wav`` can be found like this:

.. code-block:: text

    piano_%midinote_v%voice.wav
    juno_%midinote_v%voice.wav

You can also write something like this:

.. code-block:: text

    piano_%midinote.wav_v1, %voice=1
    juno_%midinote.wav_v2, %voice=2

More examples :ref:`here <definition-examples>`.

.. note::

    To switch between voices you will need to using the :ref:`midi-mapping` function to map your desired device controls.

Sample randomization
====================

If you have multiple versions of the same sample, for example alternative samples of the same snare drum, you can tell SamplerBox to randomize them by
using the ``%seq`` keyword in your :ref:`definition.txt file <definition-files>`.

More examples :ref:`here <definition-examples>`.

Freeverb
========

A reverb module (`Freeverb <https://ccrma.stanford.edu/~jos/pasp/Freeverb.html>`_) is available. Thanks goes to `Erik <http://www.nickyspride.nl/sb2/>`_ for this feature.

Reverb can be enabled in :ref:`config.ini <config-ini>` either via the text file directly in `/boot/samplerbox/config.ini` or via :ref:`system-mode-1`'s menu under ``System Settings``.

.. note::

    You must map its parameters to some MIDI controls via :ref:`midi-mapping`.

.. warning::

    This is currently experimental as it sometimes produces undesirable pops and clicks.

Auto-chords
===========

Builds and plays back a chord from a single note.

Panic key
=========

Control change messages CC120 and CC123 will trigger the panic function, killing all playing sounds. This can also be :ref:`MIDI Mapped <midi-mapping>`.

.. _menu-system:

Menu system
===========

A menu system is available to change the behaviour of the SamplerBox.

.. note::

    This feature assumes you have a `HD44780 LCD <https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller>`_
    module connected to your Raspberry Pi. You will need to define the GPIO pins you are connect to in the :ref:`config.ini <config-ini>`.

.. warning::

    :ref:`system-mode-1` only

Setlist
=======

SamplerBox manages your sample-sets with a ``setlist.txt`` file found in the root of your sample-sets directory. If one cannot be found,
a new one is generated and populated with all sample-sets ordered alphanumerically.

Upon startup, new folders will be detected and appended to the end of the setlist.

You can rearrange the setlist via the menu system.

.. warning::

    :ref:`system-mode-1` only. For :ref:`system-mode-2` sample-sets will be ordered by directory names alphanumerically.


Sample-set definition management
================================

:ref:`global-keywords` for every sample-set can be modified using this feature. This includes ``%%mode``,
``%%velmode``, ``%%release``, ``%%gain``, ``%%transpose``, ``fillnotes`` and ``%%pitchbend``.

.. warning::

    :ref:`system-mode-1` only


MIDI mapping
============

Many features of the SamplerBox can be mapped to :ref:`MIDI controls <midi-mapping>` via the menu system.

.. warning::

    :ref:`system-mode-1` only

System settings
===============

Some of the system settings found in the :ref:`config.ini <config-ini>` file can be edited and saved from this menu.

More in the :ref:`system-settings` section.

.. warning::

    :ref:`system-mode-1` only