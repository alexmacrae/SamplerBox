The definition.txt files
========================




Definition of sample names
--------------------------

In the most basic situation, the sample files within the folders have to be called 0.wav, 2.wav and so on till 127.wav.
For the translation of notes to numbers, see the picture on the right.
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
|                   | | samples) you can number them. On playback a random sample will be selected.|
+-------------------+------------------------------------------------------------------------------+


Global behaviour keywords
-------------------------

The previous examples also showed the usage of global keywords. Available global keywords in the definition.txt for
influencing the playback on load of preset/patch (all lowercase).

%%mode
^^^^^^
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
^^^^^^^^^

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
^^^^^^^^^

Time to fadeout playback volume from the sample level to zero after the key is released (=note-off received) in
tenth's of seconds.

Default = 3 (0.3 seconds).

%%gain
^^^^^^

Adapts sample volume before alsamixer by means of a multiplication factor. With this you can adapt presets to
SamplerBox input without actually changing the wav files.

Default = 1. Possible values: 2, 1.5, 0.25, .5 etc.

%%transpose
^^^^^^^^^^^

The script assigns "middle C" (C4) to midi note 60. With this you can for instance normalize
presets using C3 or C5 without renaming the WAV-files.

Default = 0.

.. note::

    12 is 1 octave up. Conversely -12 is 1 octave down.

.. note::

    Original SamplerBox uses C5.

%%pitchbend
^^^^^^^^^^^

The depth of the pitchbend in semitones.

Possible values: 0-12, where 12 means range is 1 octave up and down and zero disables the pitchwheel/joystick.


Examples
--------

Example 1
^^^^^^^^^

The original GrandPiano set uses multiple lines specifying the wav's to be
selected and the corresponding fixed velocity value. Remember that default velocity is 127

+-----------|----------------------------------------
|D#5v16.wav | |
|D#5v16.wav | | %%mode=keyb
|D#5v16.wav | | %%velmode=sample
|D#5v16.wav | | %notenamev4.wav,%velocity=40
|D#5v16.wav | | %notenamev7.wav,%velocity=60
|D#5v16.wav | | %notenamev11.wav,%velocity=80
|D#5v16.wav | | %notenamev14.wav,%velocity=100
|D#5v16.wav | | %notenamev16.wav


03 Alesis-Fusion-Bass-Loop.wav