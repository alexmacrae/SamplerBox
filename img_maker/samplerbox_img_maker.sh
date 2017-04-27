#!/bin/bash -v
# CREATE A RASPBIAN JESSIE IMAGE FOR SAMPLERBOX
# 2017-03-30
#
# USAGE: sudo chmod 777 samplerbox_img_maker.sh ; nohup sudo samplerbox_img_maker.sh &
# Append " | tee -a output.log" to the end of the sh run line to output console lines to output.log
# To print additions to output.log in realtime from another machine "tail -f output.log". Perhaps you want to
# monitor progress or errors from another machine or remotely from your mobile!
#

set -e

#sudo apt-get update && sudo apt-get install -y cdebootstrap kpartx parted sshpass zip
# !! Might need to sudo, depending on your setup
apt-get update && apt-get install -y cdebootstrap kpartx parted sshpass zip dosfstools

image_name=$(date "+%Y-%m-%d")_samplerbox.img
boot_size=64
raspbian_size=1300
samples_size=128
image_size=$(($boot_size+$raspbian_size+$samples_size+64))
hostname=samplerbox
root_password=root
http=http://mirror.internode.on.net/pub/raspbian/raspbian/
#http=http://mirrordirector.raspbian.org/raspbian/ # at time of compile, some packages were not found and failed. Might work again now

dd if=/dev/zero of=$image_name  bs=1M  count=$image_size
fdisk $image_name <<EOF
o
n



+$(($boot_size))M
p
a
t
c
n



+$(($raspbian_size))M
p
n
p


+$(($samples_size))M
p
w
EOF


kpartx -av $image_name
partprobe /dev/loop0
bootpart=/dev/mapper/loop0p1
rootpart=/dev/mapper/loop0p2
samplespart=/dev/mapper/loop0p3

mkdosfs -n BOOT $bootpart
mkfs.ext4 -L ROOT $rootpart
mkfs.ext4 -L SAMPLES $samplespart
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
echo "deb http://archive.raspberrypi.org/debian/ jessie main" >> sdcard/etc/apt/sources.list

echo Etc/UTC > sdcard/etc/timezone
echo en_GB.UTF-8 UTF-8 > sdcard/etc/locale.gen
cp -v /etc/default/keyboard sdcard/etc/default/keyboard
echo $hostname > sdcard/etc/hostname
echo "127.0.1.1 $hostname" >> sdcard/etc/hosts
chroot sdcard locale-gen LANG="en_GB.UTF-8"
chroot sdcard dpkg-reconfigure -f noninteractive locales

cat <<EOF > sdcard/boot/cmdline.txt
root=/dev/mmcblk0p2 ro rootwait console=tty1 selinux=0 plymouth.enable=0 smsc95xx.turbo_mode=N dwc_otg.lpm_enable=0 elevator=noop bcm2708.uart_clock=3000000 fastboot noswap
EOF
# http://k3a.me/how-to-make-raspberrypi-truly-read-only-reliable-and-trouble-free/ @ 4.4 Disable filesystem check and swap
# added: fastboot noswap

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
/dev/sda1       /media          auto    nofail                  0       0
/dev/mmcblk0p1  /boot           vfat    ro,auto,exec            0       2
/dev/mmcblk0p2  /               auto    defaults,noatime,ro     0       1
EOF

# /dev/mmcblk0p3  /samples        auto    ro,auto,exec            0       0 # Add this after filesystem resize script on first run

mkdir -v sdcard/samples
mount -v -t ext4 -o sync $samplespart sdcard/samples

# Install packages required for SamplerBox
chroot sdcard apt-get update
chroot sdcard apt-get -y upgrade
chroot sdcard apt-get -y dist-upgrade
chroot sdcard apt-get -y install libraspberrypi-bin libraspberrypi-dev libraspberrypi0 raspberrypi-bootloader ssh wireless-tools usbutils python-tk ntpdate unzip
chroot sdcard apt-get clean
chroot sdcard apt-get -y install wpasupplicant dhcpcd5 firmware-brcm80211 # on-board wifi
chroot sdcard apt-get -y install parted dosfstools # partitioning tools
chroot sdcard apt-get -y install psmisc # contains `killall` command
chroot sdcard apt-get -y install dos2unix # converts windows files to unix
chroot sdcard apt-get clean
chroot sdcard apt-get -y install build-essential python-dev python-pip cython python-smbus python-numpy python-rpi.gpio python-serial
chroot sdcard apt-get -y install python-configparser python-psutil python-scipy git portaudio19-dev alsa-utils libportaudio2 libffi-dev
chroot sdcard apt-get clean
chroot sdcard apt-get autoremove -y
chroot sdcard pip install pyaudio cffi sounddevice pyalsaaudio wifi
chroot sdcard sh -c "cd /root ; git clone https://github.com/gesellkammer/rtmidi2 ; cd rtmidi2 ; python setup.py install ; cd .. ; rm -rf rtmidi2"
chroot sdcard sh -c "cd /root ; git clone https://github.com/dbrgn/RPLCD ; cd RPLCD ; python setup.py install ; cd .. ; rm -rf RPLCD"
chroot sdcard sh -c "cd /root ; git clone https://gitorious.org/pyosc/devel.git ; cd devel ; python setup.py install ; cd .. ; rm -rf devel" # OSC support
chroot sdcard sh -c "cd /root ; git clone https://github.com/proxypoke/wpa_config.git ; cd wpa_config ; python setup.py install ; cd .. ; rm -rf wpa_config"

# Allowing root to log into $release with password... "
sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' sdcard/etc/ssh/sshd_config


###########################################
# NETWORKING

#cat <<EOF > /etc/systemd/system/dhcpcd5
#[Unit]
#Description=dhcpcd on all interfaces
#Wants=network.target
#Before=network.target
#
#[Service]
#Type=forking
#PIDFile=/var/run/dhcpcd.pid
#ExecStart=/sbin/dhcpcd -q -b
#ExecStop=/sbin/dhcpcd -x
#
#[Install]
#WantedBy=multi-user.target
#Alias=dhcpcd5
#EOF

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

#mkdir sdcard/etc/wpa_supplicant/ # is created after apt-get install wpasupplicant
cat <<EOF > sdcard/etc/wpa_supplicant/wpa_supplicant.conf
update_config=1

# Uncomment and edit below to include your WiFi network's login credentials
#network={
#    ssid="YOUR_NETWORK_NAME"
#    psk="YOUR_NETWORK_PASSWORD"
#}

EOF

#mkdir sdcard/boot/networking/wpa_config
cat <<EOF > sdcard/etc/wpa_config/wpa_supplicant.conf.head
update_config=1
EOF

cat <<EOF > sdcard/etc/wpa_config/wpa_supplicant.conf.tail

EOF

## Start wpa_supplicant
#chroot sdcard sh -c "wpa_supplicant -B -i wlan0 -c /boot/networking/wireless_networks.conf" # only need if wpa_supplicant.conf lives somewhere other than the default. eg /boot/networking/wireless_networks.conf
chroot sdcard sh -c "wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf" # only need if wpa_supplicant.conf lives somewhere other than the default. eg /boot/networking/wireless_networks.conf
#chroot sdcard systemctl enable wpa_supplicant # line may not be needed as package wpasupplicant seems to start service upon reboot
#chroot sdcard systemctl enable dhcpcd # dhcpcd5 enables itself after install

#echo "timeout 10;" >> sdcard/etc/dhcp/dhclient.conf
#echo "retry 1;" >> sdcard/etc/dhcp/dhclient.conf

###########################################

# SamplerBox
chroot sdcard sh -c "cd /root ; git clone https://github.com/alexmacrae/SamplerBox.git; cd SamplerBox; python setup.py build_ext --inplace"

cat <<EOF > sdcard/root/SamplerBox/samplerbox.sh
#!/bin/sh
python /root/SamplerBox/samplerbox.py
EOF

mkdir sdcard/boot/samplerbox
touch sdcard/boot/samplerbox/midimaps.pkl

# Move config.ini to /boot/samplerbox/ (read-writable)
cp sdcard/root/SamplerBox/config.ini sdcard/boot/samplerbox/config.ini
rm sdcard/root/SamplerBox/config.ini

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
  To remount a partition as read-write: rw_root / rw_boot / rw_samples
  To remount a partition as read-only:  ro_root / ro_boot / ro_samples
* The SamplerBox program (/root/SamplerBox/samplerbox.py) should be
  up and running. If not, try:  systemctl status samplerbox
* To see SamplerBox print statements, you need to restart the program:
  systemctl stop samplerbox ; cd ; cd SamplerBox/ ; python samplerbox.py
* The SamplerBox configuration file is found at /boot/samplerbox/config.ini
  Use this file to define system navigation MIDI/GPIO and LCD GPIO
######################

EOF

# Script to resize samples partition to fill user's SD card free space. This will be run once, and self-delete.
EOF="EOF"
self="\$0"
cat <<EOF > sdcard/boot/resize_samples_partition.sh
#!/bin/bash -v

set -e

mount -vo remount,rw /
mount -vo remount,rw /boot
umount -v /dev/mmcblk0p3 &
#apt-get install -y parted dosfstools
parted /dev/mmcblk0 <<EOF
resizepart
3
y
-1M
q
$EOF
# run again in case the `y` above fails
parted /dev/mmcblk0 <<EOF
resizepart
3
-1M
q
$EOF

mkfs.ext4 -L SAMPLES /dev/mmcblk0p3  # reformat
mount -v -t ext4 -o sync /dev/mmcblk0p3 /samples/

# Move /Saw/ sample-set from original /SamplerBox/media/ to /samples/ (partition)
cp -a /root/SamplerBox/media/. /samples/
rm -r /root/SamplerBox/media/
# Make empty setlist.txt file
touch /samples/setlist.txt
rm -r /samples/lost+found/

cat <<EOF >> /etc/fstab
/dev/mmcblk0p3  /samples        auto    ro,auto,exec            0       0
$EOF

# Delete this file - we don't want to accidentally reformat our /samples/ partition!
rm -- "$self" && reboot

exit 0
EOF

sed -i 's/ENV{pvolume}:="-20dB"/ENV{pvolume}:="-10dB"/' sdcard/usr/share/alsa/init/default
#sed -i '$ i\ntpdate &' sdcard/etc/rc.local

chroot sdcard systemctl enable /etc/systemd/system/samplerbox.service

echo 'i2c-dev' >> sdcard/etc/modules
echo 'snd_bcm2835' >> sdcard/etc/modules

#############################
# Prep for read-only system #
#############################

## Remove unnecessary services and files
#chroot sdcard apt-get -y remove --purge cron logrotate
#chroot sdcard insserv -r x11-common
#chroot sdcard apt-get autoremove --purge
#
## Replace log management with the busybox one - will be able to use the `logread` command
#chroot sdcard apt-get -y install busybox-syslogd
#chroot sdcard yes | dpkg --purge rsyslog
#
## Move some system files to temp filesystem
#chroot sdcard rm -rf /var/lib/dhcp/ /var/run /var/spool /var/lock /etc/resolv.conf
#chroot sdcard ln -s /tmp /var/lib/dhcp
#chroot sdcard ln -s /tmp /var/run
#chroot sdcard ln -s /tmp /var/spool
#chroot sdcard ln -s /tmp /var/lock
#chroot sdcard touch /tmp/dhcpcd.resolv.conf
#chroot sdcard ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf
#
## On Debian jessie move `random-seed` file to writable location
#chroot sdcard rm /var/lib/systemd/random-seed
#chroot sdcard ln -s /tmp/random-seed /var/lib/systemd/random-seed
#chroot sdcard sed -i '/ExecStart=\/lib\/systemd/ i\ExecStartPre=\/bin\/echo "" >\/tmp\/random-seed' /lib/systemd/system/systemd-random-seed.service
#chroot sdcard systemctl daemon-reload
## Remove some startup scripts
#chroot sdcard insserv -r bootlogs
#chroot sdcard insserv -r console-setup

#############################

# Unmounting mount points
sync

umount -v sdcard/boot
umount -lfv sdcard &
#umount -v sdcard
umount -v sdcard/samples &

kpartx -dv $image_name

sync

zip $image_name.zip $image_name

ls -la -h

#FINISHED

exit 0
