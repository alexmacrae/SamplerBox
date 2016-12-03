Features
========

This is a modified version (and work in progress) of `Joseph Ernest's SamplerBox <https://github.com/josephernest/SamplerBox>`_, as well as merged pieces from `Hans <http://homspace.xs4all.nl/homspace/samplerbox/index.html>`_ and `Erik's SamplerBox2 <http://www.nickyspride.nl/sb2/>`_. The original samplerbox.py code was getting too big to manage so it has been split up into modules.


Voices
------

You can now define voices within presets via a sample-set's ``definition.txt`` file using the new parameter ``%voice``.

For example, ``piano_60_voice1.wav`` and ``piano_60_voice2.wav`` would be found with ``piano_%midinote_voice%voice.wav``. To switch between voices (max of 4) you will need to using the [MIDI Mapping](#user-content-midi-mapping) function to map your desired device controls.

Freeverb
--------

Reverb is available. You can map its parameters to MIDI controls via :ref:`midi-mapping`.

Thanks goes to `Erik <http://www.nickyspride.nl/sb2/>`_.

.. _menu-system:

Menu System
-----------

A menu system has been implemented to access:

* :ref:`setlist-functions`
* Master volume
* :ref:`midi-mapping`
* :ref:`system-settings`

This feature also assumes you have a `HD44780 LCD <https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller>`_ module wired to your Raspberry Pi, although it is not required. You will need to define the GPIO pins you are connect to in the ``config.ini file``

.. _setlist-functions:

Setlist functions
^^^^^^^^^^^^^^^^^

SamplerBox now manages your sample-sets with a setlist, so correct naming of your folders isn't a requirement anymore. On startup new folders will be detected and appended to the end of the setlist. Using the menu system you can reorder your sample-sets.

Rearrange
`````````
Select a song and move it to a new position in the setlist.

Remove missing
``````````````
If a folder has been deleted, it will appear in the setlist with an asterix (*) beside it. This function removes missing folders from the setlist.

Delete songs
````````````
Currently this just removes the sample-set from the setlist without deleting the actual folder. A bit pointless since it will be re-added upon restart!
    
.. _midi-mapping:

MIDI Mapping
^^^^^^^^^^^^

Note remap
``````````
Idea with this feature is to map notes to a device control. Useful if you want to map pads to samples at, for instance, C-2, C#-2, D-2 etc.

.. warning::

    Feature not implemented yet.


Master Volume
`````````````
Map any control to affect the SamplerBox's master volume. Min and max unavailable at this time.

Reverb
``````
Map all parameters to MIDI controls. Room size, damping, wet, dry and width.

Voices
``````
Map MIDI controls to each of the 4 voices.

Sustain
```````
.. warning::

    Feature not implemented yet.

Pitch wheel
```````````

.. warning::

    Feature not implemented yet.

Mod wheel
`````````
.. warning::

    Feature not implemented yet.

SamplerBox Navigation
`````````````````````
Map MIDI controls to each of the 4 navigation buttons (left, right, enter and cancel). Mapping a control to one of these functions will not override any other controls mapped to the same function, thus allowing


.. _system-settings:

System Settings
^^^^^^^^^^^^^^^

Some settings are managed via ``config.ini``. Currently this is managed manually (and some pieces are still in ``globalvars.py``), but will be managed via the :ref:`menu-system` soon. Sorry about the mess!