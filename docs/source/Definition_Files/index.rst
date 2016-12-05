The definition.txt files
************************

If you're not naming your samples by the convention ``45.wav``, ``46.wav`` etc, or ``C1.wav``, ``C#1.wav`` etc, you can
create a ``definition.txt`` file inside a sample-set's directory. This file tells SamplerBox how to read and playback
samples.


Definition of sample names
==========================

In the most basic situation, the sample files within the folders have to be called 0.wav, 2.wav and so on till 127.wav.

The structure of names within this folder can described in the definition.txt on or more line(s) using keywords and fixed
text (wildcards can be used).

+-------------------+------------------------------------------------------------------------------+
|Definition keyword |Description                                                                   |
+===================+==============================================================================+
|%notename          | | C1, C2, C3, D#3, F#4, etc.                                                 |
+-------------------+------------------------------------------------------------------------------+
|%midinote          | | 0-127. 60 corresponds with middle C = C4.                                  |
+-------------------+------------------------------------------------------------------------------+
|%velocity          | | 1-127. 127 is default. A velocity sample is used from its value upwards    |
|                   | | till the next sample. Velocity values below lowest sample will use this    |
|                   | | lowest one.                                                                |
+-------------------+------------------------------------------------------------------------------+
|%voice             | | 1-127. 1 is default. This enables loading different instruments in one     |
|                   | | sample set, so that switching between them has no delay.                   |
+-------------------+------------------------------------------------------------------------------+
|%seq               | | If you have multiple versions of the same sample (eg different snare       |
|                   | | samples) you can number them. On playback a random sample will             |
|                   | | be selected.                                                               |
+-------------------+------------------------------------------------------------------------------+


.. _global-keywords:

Global behaviour keywords
=========================

These are global keywords in the definition.txt for influencing the playback upon load of a preset/sample-set.
For every keyword not defined in the file, the default value is used.

.. note::

    In ``system-mode-1`` it is possible to modify these keywords from menu.

%%mode
------

+--------+-----------------------------------------------------------------------------------------+
|%%mode= |Description                                                                              |
+========+=========================================================================================+
|keyb    | | (Default) "Normal": end on note-off and use loop markers if any while key is pressed  |
|        | | (original SamplerBox).                                                                |
+--------+-----------------------------------------------------------------------------------------+
|once    | | "Playback": play sample from start to end ignoring standard note-off.                 |
+--------+-----------------------------------------------------------------------------------------+
|on64    | | Like "once" but now only notes 0-63 can be used; use note+64 to stop playback         |
|        | | (=send note-off)                                                                      |
+--------+-----------------------------------------------------------------------------------------+
|loop    | | Like "on64", but also loop markers will be recognized; more versitale than "On64"     |
+--------+-----------------------------------------------------------------------------------------+
|loo2    | | Like "loop", but the loop will stop when playing the same note (=2nd keypress sends   |
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
|sample     | | (Default) Volume equals the value in the sample, so it requires multiple           |
|           | | samples using the %velocity parameter to get differentiation (original SamplerBox).|
+-----------+--------------------------------------------------------------------------------------+
|accurate   | | "Playback": play sample from start to end ignoring standard note-off.              |
+-----------+--------------------------------------------------------------------------------------+


%%release
---------

Time to fadeout playback volume from the sample level to zero after the key is released (=note-off received) in
tenth's of seconds.

.. code-block:: text

    Default = 3 (0.3 seconds)

%%gain
------

Adapts sample volume before alsamixer by means of a multiplication factor. With this you can adapt presets to
SamplerBox input without actually changing the wav files.

.. code-block:: text

    Default = 1
    Possible values: 2, 1.5, 0.25, .5 etc.

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

Examples
========

.. toctree::
    :maxdepth: 3

    examples

