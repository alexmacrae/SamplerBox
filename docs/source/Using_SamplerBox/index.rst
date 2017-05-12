Using SamplerBox
****************

.. _system-modes:

Introduction
============

SamplerBox has two system modes available which is determined by the ``SYSTEM_MODE`` option in :ref:`config.ini <config-ini>`.

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

Samples
=======


Where to put samples
--------------------

SamplerBox looks for sample-set directories in three places, in this order of priority:

1. User-defined directory in ``config.ini``
2. ``/media/`` (USB drive)
3. ``/samples/`` (SD card)

.. note::

    If the user-defined directory cannot be found, SamplerBox will look for a mounted USB drive. Failing that, the default ``/samples/`` directory
    will be used.

USB drive
---------

This is the easiest way to get samples from your computer to your SamplerBox. By default, SamplerBox will look for directories in the root of your
USB drive. A setlist.txt file will be automatically generated that will include the name of every directory listed alphanumerically. You can
reorder the lines in the setlist.txt file on your PC, or do it via the :ref:`system-mode-1` menu.

.. hint::

    If you'd prefer to have your sample-sets in a subdirectory on your USB drive (or indeed anywhere else) find the line ``SAMPLES_DIR = None`` in your ``config.ini`` and change it to
    ``SAMPLES_DIR = /media/subdirectory``.


SD card (advanced)
------------------

A third partition on your SD card is available for samples (mounted to ``/samples/``). When the Raspberry Pi is running it is
mounted as read-only to extend the life of the SD card.

To manage your sample-sets here you must first remount the partition as read-write by entering the following on the Raspberry Pi's command line:

``mount -o remount,rw /samples``

You can now upload/delete sample-sets via your SFTP client.

It is also possible to manage samples on your PC computer. However, Windows machines only detect the first partition of an SD card.
In the case of SamplerBox this is the ``/boot/`` partition. There are ways to gain access to other partitions but that is not covered here.

.. note::

    SamplerBox issues mounting commands from the program. This is how it can manage sample-sets and the setlist from the within the program.



--------------------------------------

System modes
============

.. toctree::
    :maxdepth: 3

    system-mode-1
    system-mode-2
