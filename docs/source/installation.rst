Installation
============

**These are "start from scratch" installation instructions.**

1. `Download Raspbian Jessie lite <https://www.raspberrypi.org/downloads/raspbian/>`_ (291MB)

2. Write the image to a formatted SD card from your PC: 
 | `Linux <https://www.raspberrypi.org/documentation/installation/installing-images/linux.md>`_
 | `Mac OS <https://www.raspberrypi.org/documentation/installation/installing-images/mac.md>`_
 | `Windows <https://www.raspberrypi.org/documentation/installation/installing-images/windows.md>`_


3. Log into RPi (pi:raspberry) and install the required dependencies (Python-related packages and audio libraries)::

    sudo apt-get update ; sudo apt-get -y install python-dev python-numpy cython python-smbus portaudio19-dev python-pip python-configparser python-psutil python-scipy git libffi-dev python-tk
    git clone http://people.csail.mit.edu/hubert/git/pyaudio.git ; cd pyaudio ; sudo python setup.py install ; cd ..
    git clone https://github.com/gesellkammer/rtmidi2 ; cd rtmidi2 ; sudo python setup.py install ; cd ..
    git clone https://github.com/dbrgn/RPLCD ; cd RPLCD ; sudo python setup.py install ; cd ..
    git clone https://gitorious.org/pyosc/devel.git ; cd devel ; sudo python setup.py install ; cd ..
    pip install cffi --user
    pip install libportaudio2
    pip install sounddevice --user
    pip install RPi

4. Download and build SamplerBox from the RPi command-line::

    git clone https://github.com/alexmacrae/SamplerBox.git ;
    cd SamplerBox ; sudo python setup.py build_ext --inplace; cd ..
    sudo chmod -x SamplerBox/sb.sh


5. Configure RPi to auto-run SamplerBox on startup

     1. Open ``sudo nano /etc/rc.local``
     2. Before the last line (``exit 0``) enter ``sh /home/pi/SamplerBox/samplerbox.sh``
     3. ``CTRL-X`` and ``Y`` to save
      
6. (Optional) Configure RPi to connect to your WiFi network (tested with RPi3)

    1. ``sudo nano /etc/wpa_supplicant/wpa_supplicant.conf``
    2. At the end of the file enter::

         network={
            ssid="your_wifi_network_name"
            psk="your_wifi_password"
         }

    3. ``CTRL-X`` and ``Y`` to save
    4. Find your RPi's IP address by entering ``ifconfig wlan0``

More information in the links below; however they are not specific to this build.
`FAQ <http://www.samplerbox.org/faq>`_ on `www.samplerbox.org <http://www.samplerbox.org>`_.