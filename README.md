SamplerBox
==========

An open-source audio sampler project based on RaspberryPi.

This modification is very much a work in progress and is likely to be buggy - please bare with me! You will need a HD44780 LCD screen and an external USB DAC. Configurations may need to be made in `lcd.py` and `globalvars.py`. I'll work to make this less painful in the future.

[Manual installation](#manual-installation)
----

####These are "start from scratch" installation instructions.

1. [Download Raspbian Jessie lite](https://www.raspberrypi.org/downloads/raspbian/) (291MB)

2. Write the image to a formatted SD card from your PC: 
[Linux](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md)
[Mac OS](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)
[Windows](https://www.raspberrypi.org/documentation/installation/installing-images/windows.md)


3. Log into RPi (pi:raspberry) and install the required dependencies (Python-related packages and audio libraries):
```
sudo apt-get update ; sudo apt-get -y install python-dev python-numpy cython python-smbus portaudio19-dev python-pip python-configparser python-psutil python-scipy git
git clone http://people.csail.mit.edu/hubert/git/pyaudio.git ; cd pyaudio ; sudo python setup.py install ; cd ..
git clone https://github.com/gesellkammer/rtmidi2 ; cd rtmidi2 ; sudo python setup.py install ; cd ..
git clone https://github.com/dbrgn/RPLCD ; cd RPLCD ; sudo python setup.py install ; cd ..
git clone https://gitorious.org/pyosc/devel.git ; cd devel ; sudo python setup.py install ; cd ..
```


4. Download and build SamplerBox from the RPi command-line:
```
git clone https://github.com/alexmacrae/SamplerBox.git ;
cd SamplerBox ; sudo python setup.py build_ext --inplace
sudo chmod -x SamplerBox/samplerbox.sh
```

5. Configure RPi to auto-run SamplerBox on startup
     1. Open `sudo nano /etc/rc.local`
     2. Before the last line (`exit 0`) enter `sh /home/pi/SamplerBox/samplerbox.sh`
     3. `CTRL-X` and `Y` to save
      
6. (**Optional**) Configure RPi to connect to your WiFi network (tested with RPi3):
    1. `sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`
    2. At the end of the file enter:
     ```
     network={
        ssid="your_wifi_network_name"
        psk="your_wifi_password"
     }
     ```
    3. `CTRL-X` and `Y` to save
    4. Find your RPi's IP address by entering `ifconfig wlan0`

More information in the links below; however they are not specific to this build.
[FAQ](http://www.samplerbox.org/faq) on [www.samplerbox.org](http://www.samplerbox.org).


[Modifications](#modifications)
----

This is a modified version (and work in progress) of [Joseph Ernest's ](https://github.com/josephernest/SamplerBox) SamplerBox, as well as pieces from [Hans](http://homspace.xs4all.nl/homspace/samplerbox/index.html) and [Erik](http://www.nickyspride.nl/sb2/)'s SamplerBox2. The original samplerbox.py code was getting too big to manage so I have split it up into modules.

####System settings
_Some_ settings are managed via `system config/config.ini`. Currently this is managed manually (and some pieces are still in `globalvars.py`), but will be managed via the [menu system](#user-content-menu-system) soon. Sorry about the mess! 

####Voices
You can now define voices within presets via a sample-set's `definition.txt` file using the new parameter `%voice%`.

For example, `sampleset_60_voice1.wav` and `sampleset_60_voice2.wav` would be found with `sampleset_%midinote_voice%voice.wav`. To switch between voices (max of 4) you will need to using the [MIDI Mapping](#user-content-midi-mapping) function to map your desired device controls.

####Freeverb
Reverb is available. You can map its parameters to MIDI controls via [MIDI Mapping](#user-content-midi-mapping) 

Thanks goes to [Erik](http://www.nickyspride.nl/sb2/).
 
####Menu System
A menu system has been implemented to access:

* [Setlist functions](#user-content-setlist-functions)
* ~~All songs~~ (incomplete)
* ~~Master volume~~ (incomplete)
* [MIDI mapping](#user-content-midi-mapping)
* ~~System settings~~ (incomplete)

The structure of the menu system is in `menudict.py`. If the node has a submenu this tells the system to enter that menu. If it doesn't it will look for a function (fn) to run.

This feature also assumes you have a [HD44780 LCD](https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller) module wired to your Raspberry Pi, although it is not required. **You may need to modify lcd.py to correctly define the GPIO pins you've connected it to**, or disable via `system config/config.ini`.

####Setlist functions
SamplerBox now manages your sample-sets with a setlist, so correct naming of your folders isn't a requirement anymore. On startup new folders will be detected and appended to the end of the setlist. Using the menu system you can reorder your sample-sets.

* **Rearrange**
    Select a song and move it to a new position in the setlist.
* **Remove missing**
    If a folder has been deleted, it will appear in the setlist with an asterix (*) beside it. This function removes missing folders from the setlist. 
* **Delete songs**
    Currently this just removes the sample-set from the setlist without deleting the actual folder. A bit pointless since it will be readded upon restart!
    

####MIDI Mapping

* ~~Note remap~~
    Idea with this feature is to map notes to a device control. Useful if you want to map pads to samples at, for instance, C-2, C#-2, D-2 etc.  
* **Master Volume**
    Map any control to affect the SamplerBox's master volume. Min and max unavailable at this time.
* **Reverb**
    Map all parameters to MIDI controls. Room size, damping, wet, dry and width.
* **Voices**
    Map MIDI controls to each of the 4 voices.
* ~~Sustain~~
* ~~Pitch wheel~~
* ~~Mod wheel~~
* ~~SamplerBox Navigation~~


Website: [www.samplerbox.org](http://www.samplerbox.org)

[![](http://gget.it/flurexml/1.jpg)](https://www.youtube.com/watch?v=yz7GZ8YOjTw)

[![](http://img.youtube.com/vi/-JsubgWiJeg/sddefault.jpg)](https://www.youtube.com/watch?v=-JsubgWiJeg)




[About](#about)
----

####Authors

**Joseph Ernest** (twitter: [@JosephErnest](http:/twitter.com/JosephErnest), mail: [contact@samplerbox.org](mailto:contact@samplerbox.org))

**Alex MacRae** (mail: [alex.finlay.macrae@gmail.com](mailto:alex.finlay.macrae@gmail.com)

**Hans** (Web: http://homspace.xs4all.nl/homspace/samplerbox/index.html)

**Erik** (Web: http://www.nickyspride.nl/sb2/)


[License](#license)
----

[Creative Commons BY-SA 3.0](http://creativecommons.org/licenses/by-sa/3.0/)