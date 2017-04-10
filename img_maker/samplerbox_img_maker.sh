#!/bin/bash -v
# CREATE A RASPBIAN JESSIE IMAGE FOR SAMPLERBOX
# 2017-03-30
#
# USAGE: sudo chmod 777 samplerbox_img_maker.sh ; nohup sudo ./samplerbox_img_maker.sh &
#
# TODO:
#       * Sample-sets on SD card:
#               Need to make a read-writable partition that expands to fill the remaining
#               SD card space on a user's SD card on first boot.
#       * config.ini and other read-writable files:
#               Where will config.ini, setlist.txt and midimaps.pkl live? config.ini needs to be accessible
#               to users. The others can be hidden. A setlist.txt will appear on a user's USB stick if they
#               choose to use one instead of the SD card.
#       * wlan0 issue for RPi3 on-board WiFi:
#               Persistent issue where only eth0 works. On the right path: ``apt-get install firmware-brcm80211``
#               installs the firmware and causes wlan0 to become available, but more needs to be configured.
#       * System is read-writable:
#               For now I have made the system read-writable (cmdline.txt: ``rw`` instead of ``ro``) so that
#               config.ini, setlist.txt and midimaps.pkl can be rewritten. This is temporary.

set -e

#sudo apt-get update && sudo apt-get install -y cdebootstrap kpartx parted sshpass zip
# !! Might need to sudo, depending on your setup
apt-get update && apt-get install -y cdebootstrap kpartx parted sshpass zip firmware-brcm80211 wpasupplicant dhcpcd

image_name=$(date "+%Y-%m-%d")_samplerbox.img
image_size=1300
hostname=samplerbox
root_password=root
http=http://mirror.internode.on.net/pub/raspbian/raspbian/
# http=http://mirrordirector.raspbian.org/raspbian/ # at time of compile, some packages were not found and failed. Might work again now

dd if=/dev/zero of=$image_name  bs=1M  count=$image_size
fdisk $image_name <<EOF
o
n



+64M
a
t
c
n




w
EOF

kpartx -av $image_name
partprobe /dev/loop0
bootpart=/dev/mapper/loop0p1
rootpart=/dev/mapper/loop0p2

mkdosfs -n BOOT $bootpart
mkfs.ext4 -L ROOT $rootpart
sync

fdisk -l $image_name
mkdir -v sdcard
mount -v -t ext4 -o sync $rootpart sdcard

cdebootstrap --arch=armhf jessie sdcard $http --include=locales --allow-unauthenticated

sync

mount -v -t vfat -o sync $bootpart sdcard/boot

echo root:$root_password | chroot sdcard chpasswd

wget -O sdcard/raspberrypi.gpg.key http://archive.raspberrypi.org/debian/raspberrypi.gpg.key
chroot sdcard apt-key add raspberrypi.gpg.key
rm -v sdcard/raspberrypi.gpg.key
wget -O sdcard/raspbian.public.key http://mirrordirector.raspbian.org/raspbian.public.key
chroot sdcard apt-key add raspbian.public.key
rm -v sdcard/raspbian.public.key
chroot sdcard apt-key list

sed -i sdcard/etc/apt/sources.list -e "s/main/main contrib non-free firmware/"
#echo "deb http://archive.raspberrypi.org/debian/ wheezy main" >> sdcard/etc/apt/sources.list
echo "deb http://archive.raspberrypi.org/debian/ jessie main" >> sdcard/etc/apt/sources.list

echo Etc/UTC > sdcard/etc/timezone
echo en_GB.UTF-8 UTF-8 > sdcard/etc/locale.gen
cp -v /etc/default/keyboard sdcard/etc/default/keyboard
echo $hostname > sdcard/etc/hostname
echo "127.0.1.1 $hostname" >> sdcard/etc/hosts
chroot sdcard locale-gen LANG="en_GB.UTF-8"
chroot sdcard dpkg-reconfigure -f noninteractive locales

# Currently read-writable (``rw`` instead of ``ro`` below). This is so config.ini, midimaps.pkl and setlist.txt can be written
cat <<EOF > sdcard/boot/cmdline.txt
root=/dev/mmcblk0p2 rw rootwait console=tty1 selinux=0 plymouth.enable=0 smsc95xx.turbo_mode=N dwc_otg.lpm_enable=0 elevator=noop bcm2708.uart_clock=3000000
EOF

cat <<EOF > sdcard/boot/config.txt
device_tree_param=i2c_arm=on
init_uart_clock=2441406
init_uart_baud=38400
gpu_mem=64
boot_delay=0
disable_splash=1
disable_audio_dither=1
dtparam=audio=on
EOF

cat <<EOF > sdcard/etc/fstab
/dev/sda1       /media          auto    nofail            0       0
EOF
#/dev/sdb1       /media          auto    nofail            0       0
#/dev/           /sdsamples      auto    nofail            0       0 #TODO: 3rd partition. Maybe change from auto because it's expected

# "allow-hotplug" instead of "auto" very important to prevent blocking on boot if no network present
cat <<EOF > sdcard/etc/network/interfaces
auto lo
iface lo inet loopback

allow-hotplug eth0
iface eth0 inet dhcp

allow-hotplug wlan0
iface wlan0 inet manual
	wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

allow-hotplug wlan1
iface wlan0 inet manual
	wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf	

EOF

###########################################
# NETWORK
#
# WiFi / wlan0 fix: manually download firmware for RPi3 WiFi module. https://ubuntu-mate.community/t/solved-update-mate-15-10-for-the-raspberry-pi3-wont-boot/4508
#chroot sdcard sh -c "cd /lib ; mkdir firmware ; mkdir firmware/brcm ; cd firmware/brcm ; wget https://github.com/RPi-Distro/firmware-nonfree/raw/master/brcm80211/brcm/brcmfmac43430-sdio.bin ; wget https://github.com/RPi-Distro/firmware-nonfree/raw/master/brcm80211/brcm/brcmfmac43430-sdio.txt"

# Create wpa_supplicant.conf

# !! Last try got: "cannot create sdcard/etc/network/wpa_supplicant/wpa_supplicant.conf: Directory nonexistent"

#cat <<EOF > sdcard/etc/network/wpa_supplicant/wpa_supplicant.conf
#ctrl_interface=/run/wpa_supplicant
#update_config=1
#EOF
#
#chmod 777 sdcard/etc/network/wpa_supplicant/wpa_supplicant.conf
#
## Start wpa_supplicant
#chroot sdcard sh -c "wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf"
###########################################

#echo "timeout 10;" >> sdcard/etc/dhcp/dhclient.conf
#echo "retry 1;" >> sdcard/etc/dhcp/dhclient.conf

chroot sdcard apt-get update
chroot sdcard apt-get -y upgrade
chroot sdcard apt-get -y dist-upgrade
chroot sdcard apt-get -y install libraspberrypi-bin libraspberrypi-dev libraspberrypi0 raspberrypi-bootloader ssh wireless-tools usbutils python-tk ntpdate unzip
chroot sdcard apt-get clean
chroot sdcard apt-get -y install build-essential python-dev python-pip cython python-smbus python-numpy python-rpi.gpio python-serial
chroot sdcard apt-get -y install python-configparser python-psutil python-scipy git portaudio19-dev alsa-utils libportaudio2 libffi-dev pyalsaaudio
chroot sdcard apt-get clean
chroot sdcard apt-get autoremove -y
chroot sdcard pip install pyaudio cffi sounddevice
chroot sdcard sh -c "cd /root ; git clone https://github.com/gesellkammer/rtmidi2 ; cd rtmidi2 ; python setup.py install ; cd .. ; rm -rf rtmidi2"
chroot sdcard sh -c "cd /root ; git clone https://github.com/dbrgn/RPLCD ; cd RPLCD ; python setup.py install ; cd .. ; rm -rf RPLCD"
chroot sdcard sh -c "cd /root ; git clone https://gitorious.org/pyosc/devel.git ; cd devel ; python setup.py install ; cd .. ; rm -rf devel"

# Allowing root to log into $release with password... "
sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' sdcard/etc/ssh/sshd_config

# SamplerBox
chroot sdcard sh -c "cd /root ; git clone https://github.com/alexmacrae/SamplerBox.git ; cd SamplerBox ; python setup.py build_ext --inplace"

#chroot sdcard mkdir /boot/user
#mkdir sdcard/boot/user


cat <<EOF > sdcard/root/SamplerBox/samplerbox.sh
#!/bin/sh
python /root/SamplerBox/samplerbox.py
EOF
#
#cat <<EOF > sdcard/boot/user/config.ini
## This will get generated later
#EOF
#
#cat <<EOF > sdcard/boot/user/setlist.txt
## This will get generated later
#EOF
#
#cat <<EOF > sdcard/boot/user/midimaps.pkl
## This will get generated later
#EOF

chmod 777 sdcard/root/SamplerBox/samplerbox.sh
#chmod 777 sdcard/boot/user
#chmod 777 sdcard/boot/user/setlist.txt
#chmod 777 sdcard/boot/user/midimaps.pkl
#chmod 777 sdcard/boot/user/config2.ini

cat <<EOF > sdcard/etc/systemd/system/samplerbox.service
[Unit]
Description=Starts SamplerBox
DefaultDependencies=false

[Service]
Type=simple
ExecStart=/root/SamplerBox/samplerbox.sh
WorkingDirectory=/root/SamplerBox/

[Install]
WantedBy=local-fs.target
EOF

cat <<EOF > sdcard/etc/motd

Welcome to SamplerBox!
######################
* The filesystem is read-only, see http://www.samplerbox.org/faq#readonly
  Here is how to remount as read-write:  mount -o remount,rw /
* The SamplerBox program (/root/SamplerBox/samplerbox.py) should be
  up and running. If not, try:  systemctl status samplerbox
* To see SamplerBox print statements, you need to restart the program:
  systemctl stop samplerbox ; cd ; cd SamplerBox/ ; python samplerbox.py
######################

EOF

sed -i 's/ENV{pvolume}:="-20dB"/ENV{pvolume}:="-10dB"/' sdcard/usr/share/alsa/init/default

chroot sdcard systemctl enable /etc/systemd/system/samplerbox.service

echo 'i2c-dev' >> sdcard/etc/modules
echo 'snd_bcm2835' >> sdcard/etc/modules

# Unmounting mount points
sync

umount -v sdcard/boot
umount -v sdcard

kpartx -dv $image_name

sync

zip $image_name.zip $image_name

ls -la -h

#FINISHED

exit 0