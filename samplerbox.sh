#!/bin/sh
# samplerbox.sh
# update rc.local:
# >>> sudo nano /etc/rc.local
# before exit 0:
# >>> sudo /home/pi/SamplerBox/samplerbox.sh &

cd /home/pi/SamplerBox
sudo python samplerbox2.py