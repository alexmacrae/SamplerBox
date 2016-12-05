Using SamplerBox
****************

Introduction
============

SamplerBox has two available system modes which is determined by the SYSTEM_MODE option in the ``config.ini`` file.

+----------------------+---------------------------------------------------------------------------------------+
|:ref:`system-mode-1`  || config.ini: ``SYSTEM_MODE = 1``                                                      |
|                      ||                                                                                      |
|                      || A more advanced system that allows the user to:                                      |
|                      |                                                                                       |
|                      | * manage the order of their sample-sets (setlist mode)                                |
|                      | * manage variables defined in a sample-set's definition.txt                           |
|                      | * map MIDI controls to various playback and system functions                          |
|                      | * manage system settings by modifying the config.ini                                  |
+----------------------+---------------------------------------------------------------------------------------+
|:ref:`system-mode-2`  || config.ini: ``SYSTEM_MODE = 2``                                                      |
|                      ||                                                                                      |
|                      || A simpler system that relies on the user preparing sample-sets and                   |
|                      || config.ini on a computer. Some functions available.                                  |
+----------------------+---------------------------------------------------------------------------------------+

--------------------------------------

System modes
============

.. toctree::
    :maxdepth: 3

    system-mode-1
    system-mode-2
