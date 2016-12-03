Frequently asked questions
==========================

What is SamplerBox, and why this project?
-----------------------------------------

SamplerBox is an electronic musical instrument. Drop audio samples onto it, hook up a MIDI keyboard, and you'll be able to play with realistic piano, organ, drums, etc. sounds!
As strange as it may sound, if you wanted to add great piano sound to your MIDI keyboard or synthesizer, there was previously no hardware solution except using a computer (ok it works, but sometimes you don't feel like using a computer to do music) or buying an expensize sampler / expander. Now SamplerBox provides a sub-99€ solution!

What kind of MIDI keyboads can I connect to SamplerBox?
-------------------------------------------------------

There is no limitation about MIDI keyboards. Both USB MIDI keyboards (with a USB plug) and MIDI (with a MIDI plug) are accepted. You can use small 25-keys keyboards, such as the Akai LPK25 we use in some videos ; you can use 49 keys MIDI keyboards, or even 61 keys or 88 keys if you want!

Where can I find instrument sample-sets to use with SamplerBox?
---------------------------------------------------------------

You can find `some instruments here <http://www.samplerbox.org/instruments>`_. But you can also do some sample-sets yourself in a few seconds only (no sample-set-making skills required)! See questions :ref:`how-to-create-my-own-sample-set-easy` and :ref:`how-to-create-my-own-sample-set-advanced`.

Is velocity sensitivity possible?
---------------------------------

Yes. See :ref:`how-to-create-my-own-sample-set-advanced`.

.. _how-to-create-my-own-sample-set-easy:

How to create my own sample-set to use with SamplerBox? (easy)
--------------------------------------------------------------

If your samples are numbered by their usual MIDI note like this: ``36.wav``, ``37.wav``, ..., you just need to put these files in a folder named like this: ``/1 Piano/``, ``/17 Trumpet/``, ..., i.e. a number + a white space + a name. The number will be the preset number.

No sample-set definition file required in this simple case!

.. _how-to-create-my-own-sample-set-advanced:

How to create my own sample-set to use with SamplerBox? (advanced)
------------------------------------------------------------------

Sometimes, a picture speaks more than words, so don't forget to look at this blog article before reading what follows.

If your samples are not named like ``36.wav``, ``37.wav``, and/or you want advanced features like many velocity layers, you need to create a folder (as described before) and have a definition.txt file in it.
Let's say your samples are:

.. code-block:: txt

    /1 PIANO/MyPiano_60_vel70.wav
    /1 PIANO/MyPiano_60_vel100.wav
    /1 PIANO/MyPiano_61_vel70.wav
    /1 PIANO/MyPiano_61_vel100.wav
    ...

Then just create a file named ``/1 PIANO/definition.txt`` containing this single line:

.. code-block:: txt

    MyPiano_%midinote_vel%velocity.wav

Then SamplerBox will automatically detect and assign all the .wav files to the right notes and velocity layers! It's magic!

Is it possible to change the MIDI channel and load two patches at once? (Let’s say bass samples on channel 1 and horn samples on channel 2?)
--------------------------------------------------------------------------------------------------------------------------------------------

Currently SamplerBox reads all incoming MIDI notes, regardless the MIDI channel. But MIDI channel handling could be easily added, if this feature is really requested. Loading two patches at once is currently unsupported.

Where should I put the sample-sets?
-----------------------------------

If you installed SamplerBox via the `image file <http://www.samplerbox.org/makeitsoftware>`_ (RECOMMENDED INSTALL), you have to put the sample-sets on a USB-stick (or on a SD card in a USB SD card reader) that you will plug into the Raspberry Pi. This USB-stick / SD card should contain folders containing your .WAV samples, like this:

.. code-block:: txt

    /0 Piano/
    /1 Flute/
    ...

*Why not using the Raspberry Pi's built-in microSD card? Two reasons:*

1. *Because SamplerBox is a box! The user doesn't normally have access to the internal microSD card. The internal microSD card is used for OS and software, not for user sample-sets!*

2. *Because you want to be able to plug in / remove / plug another SD card into the SamplerBox live! This wouldn't be possible by using the internal microSD card.*

If you installed SamplerBox via the `MANUAL INSTALL <http://www.samplerbox.org/makeitsoftware>`_, you can change the config in one line to use whatever you want as the sample-set source directory.

How to change the current preset?
---------------------------------

Most MIDI keyboards have buttons called ``PROGRAM +`` / ``PROGRAM -`` that will send *ProgramChange* MIDI messages. These MIDI messages are used to change SamplerBox's current preset. How to change the current preset if you don't have such buttons on your keyboard? Use SamplerBox's `hardware buttons <http://www.samplerbox.org/article/anotherprototype>`_, it's exactly what they are made for!

What audio formats are supported?
---------------------------------

SamplerBox uses standard WAV files, stereo or mono, 16 bits or 24 bits, at a sampling rate of 44.1 Khz. It doesn't support AIFF, MP3, OGG, FLAC, etc. files.

Do I need a Raspberry Pi 2 or will it work as well with a Raspberry B / B+?
---------------------------------------------------------------------------

It will work on a Raspberry Pi B / B+, but better performances / higher polyphony will be achieved with a Raspberry Pi 2.

How do I put the SamplerBox image file on a microSD card?
---------------------------------------------------------

See `instructions here <https://www.raspberrypi.org/documentation/installation/installing-images/README.md>`_.

(For developers only) Why is the filesystem mounted as read-only by default, when I use the SamplerBox image file?
------------------------------------------------------------------------------------------------------------------

In short, removing the power cord without doing ``halt`` on a normal read-write filesystem could cause filesystem corruption.

So if we want everything to work well, there are two solutions: either we have a normal read-write filesystem, and then we need to use ``halt`` command to shutdown safely the SamplerBox (but this is impossible, as everything is embedded in a box, with no keyboard!), or we use a read-only filesystem, and we can safely shut down the SamplerBox ... by just removing the power cord or using an ON/OFF switch (like on every synthesizer, for instance)! We used this second solution. If you know a better solution (read-write filesystem + safe shutdown when we remove the power cord), please contact us.

Please note that it's always possible to remount as read-write after boot by doing ``mount -o remount,rw /``

What about looping? I have a sample of an organ which is 1 second long, what happens if I press the key for two seconds?
------------------------------------------------------------------------------------------------------------------------

You just need to save **loop markers** in the WAV files with your traditional sound editor (I recommend Sony Soundforge), and SamplerBox will recognize them and loop the sound!

.. image:: http://www.samplerbox.org/files/loops.jpg


How to permanently change the sound volume?
-------------------------------------------

This will evolve and be simpler in the future. For now, run this:

``alsamixer && mount -o remount,rw / && alsactl store``

Then select your soundcard with the key ``<F6>``, change the volume, and exit with ``<ESC>``. The sound volume will be permanently saved.

The audio output quality is bad. Why, and how to solve it?
----------------------------------------------------------

This is a well-known problem: the Raspberry Pi has a very poor built-in soundcard, resulting in noisy and sometimes stuttering sound. The only solution for this is to use a DAC, such as `this 6€ DAC <http://www.ebay.fr/sch/sis.html?_nkw=1Pc%20PCM2704%205V%20Mini%20USB%20Alimente%20Sound%20Carte%20DAC%20decodeur%20Board%20pr%20ordinateur%20PC&_itemId=231334667385>`_, which has a very good audio output.

When I boot the Raspberry Pi with the SamplerBox image, the software doesn't start automatically. How to solve this?
--------------------------------------------------------------------------------------------------------------------

The `SamplerBox image <http://www.samplerbox.org/makeitsoftware>`_ is designed to be ready-to-use. The SamplerBox software should start automatically on boot. If not, there's a configuration issue. Open ``/root/SamplerBox/samplerbox.py` and try another value for ``AUDIO_DEVICE_ID``, it should solve the issue (try with the value 0 for example). If not, `come to the forum <http://www.samplerbox.org/forum>`_ and give some details about your configuration!

Do I really need to build the whole thing (electronic parts, etc.) to use SamplerBox?
-------------------------------------------------------------------------------------

No, you don't need to. You can start with just a bare Raspberry Pi and no electronic parts. `Read more about it here <http://www.samplerbox.org/article/startsmall>`_.

Why is it impossible to edit the samples directly on SamplerBox? Why not add a screen, a graphical user interface and editing features on SamplerBox, like on an Akai MPC?
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

This would be possible with some work, but it would become a new, different project.

The philosophy of SamplerBox is a bit different than a "DIY Akai MPC". My initial goal for SamplerBox was to design what we could call a **customizable expander**. It's designed to be able to comfortably load 500MB sample-sets, like big beautiful Piano sample-sets, with many velocity layers, etc. Such sample-sets cannot really be created on the small screen of a sampler. In a word, to program such sample-sets, you need a computer anyway.

The initial philosophy was: prepare the sample-sets on a computer, drop them on a SD-card, and then insert the SD-card in SamplerBox, and that's it!

Instead of doing two things badly (playing samples + poor editing on a small screen, with no keyboard, no mouse, etc.), I prefer to focus on doing one thing well: to be able to load big nice sample-sets that you've prepared on computer.