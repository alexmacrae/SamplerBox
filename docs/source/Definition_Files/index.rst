.. _definition-files:

The definition.txt files
************************

If you're not naming your samples by the convention ``45.wav``, ``46.wav`` etc, or ``C1.wav``, ``C#1.wav`` etc, you can
create a ``definition.txt`` file inside a sample-set's directory. This file tells SamplerBox how to read and playback
samples.


Definition of sample names
==========================

In the most basic situation, the sample files within the folders have to be called ``0.wav``, ``2.wav`` and so on until ``127.wav``.

A more advanced way to manage sample-sets is to use a ``definition.txt`` which uses filename definitions and keywords to determine
how SamplerBox finds and performs samples.

------------------------------

.. _global-keywords:

Global behaviour keywords
=========================

These are global keywords in the definition.txt for influencing the playback upon load of a preset/sample-set.
For every keyword not defined in the file, the default value is used.

.. note::

    In :ref:`system-mode-1` it is possible to modify these keywords from menu.

%%mode
------

+--------+-----------------------------------------------------------------------------------------+
|%%mode= |Description                                                                              |
+========+=========================================================================================+
|Keyb    | | (Default) "Normal": end on note-off and use loop markers if any while key is pressed  |
|        | | (original SamplerBox).                                                                |
+--------+-----------------------------------------------------------------------------------------+
|Once    | | "Playback": play sample from start to end ignoring standard note-off.                 |
+--------+-----------------------------------------------------------------------------------------+
|On64    | | Like "once" but now only notes 0-63 can be used; use note+64 to stop playback         |
|        | | (=send note-off)                                                                      |
+--------+-----------------------------------------------------------------------------------------+
|Loop    | | Like "on64", but also loop markers will be recognized; more versitale than "On64"     |
+--------+-----------------------------------------------------------------------------------------+
|Loo2    | | Like "loop", but the loop will stop when playing the same note (=2nd keypress sends   |
|        | | note-off).If the sample has no loop markers it will stop when exhausted, but pressing |
|        | | the key a second time is still required before the sample can be played again!        |
|        | | This mode mimicks Korg-KAOSS and some groove samplers.                                |
+--------+-----------------------------------------------------------------------------------------+

%%velmode
---------

The way that volume is derived from the velocity.

+-----------+--------------------------------------------------------------------------------------+
|%%velmode= |Description                                                                           |
+===========+======================================================================================+
|Sample     | | (Default) Volume equals the value in the sample, so it requires multiple           |
|           | | samples using the %velocity parameter to get differentiation (original SamplerBox).|
+-----------+--------------------------------------------------------------------------------------+
|Accurate   | | "Playback": play sample from start to end ignoring standard note-off.              |
+-----------+--------------------------------------------------------------------------------------+


%%release
---------

Time to fadeout playback volume from the sample level to zero after the key is released in tenth's of seconds.

.. code-block:: text

    Default = 30 (~0.5s)
    Allowed values: 0-127 (range of 0-2s)

%%gain
------

Adapts sample volume before alsamixer by means of a multiplication factor. With this you can adapt presets to
SamplerBox input without actually changing the wav files.

.. code-block:: text

    Default = 1.0

.. warning::

    Setting this value too high may cause distorted playback.

%%transpose
-----------

Transpose up or down a desired number of semitones.

.. code-block:: text

    Default = 0


%%pitchbend
-----------

The depth of the pitchbend in semitones.

Possible values: 0-12, where 12 means range is 1 octave up and down and zero disables the pitch wheel/joystick.

.. code-block:: text

    Default = 7

-----------------------------------

.. _sample-level-keywords:

Sample-level behaviour keywords
===============================

In addition to global keywords, sample-level keywords can be used. Some of these override global keywords. For example:

.. code-block:: text

    saw2.wav, %midinote=60, %voice=2, %fillnote=N


%notename
---------

.. code-block:: text

    Values = C1, C2, C3, D#3, F#4, etc.

Define a sample's MIDI note by its note name.

%midinote
---------

.. code-block:: text

    Value range = 0-127

Define a sample's MIDI note. For example 60 corresponds to middle C = C4.

%channel
--------

.. code-block:: text

    Value range = 0-16

.. code-block:: text

    Default = 0

**NB:** 0 = all channels.

%velocity
---------

.. code-block:: text

    Value range = 1-127

.. code-block:: text

    Default = 127

A velocity sample is used from its value upwards till the next sample. Velocity values below lowest sample will use this lowest one.

%voice
------

.. code-block:: text

    Value range = 1-4

.. code-block:: text

    Default = 1

This enables loading different instruments in one sample set, so that switching between them has no delay.

%seq
----

.. code-block:: text

    Value range = 1-127

.. code-block:: text

    Default = 1

If you have multiple versions of the same sample (eg different snare samples) you can number them. On playback a random sample will be selected.

%fillnote
---------

.. code-block:: text

    Values = Y, N, G

.. code-block:: text

    Default = G (use global setting)

Determines whether the sample at the specified note will fill surrounding notes.


%mode
-----

.. code-block:: text

    Values = Once

.. code-block:: text

    Default = None

Currently only accepts Once. See ``%%mode`` above for its functionality.

%mutegroup
----------

.. code-block:: text

    Value range = 0-127

.. code-block:: text

    Default = 0 (no mute group)

Assign sample lines to a mutegroup. When performing a note from a mutegroup, any other sounds from the same
group will be stopped/choked. Useful for instruments like hi-hats.



-----------------------------------

Examples
========

.. toctree::
    :maxdepth: 3

    examples

