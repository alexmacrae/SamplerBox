#!/bin/sh
# sb.sh
# update rc.local:
# >>> sudo nano /etc/rc.local
# before exit 0:
# >>> sudo /home/pi/SamplerBox/sb.sh &
cd /home/pi/SamplerBox
python setup.py build_ext --inplace
python samplerbox.py