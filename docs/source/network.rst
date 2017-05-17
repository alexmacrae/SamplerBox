RPi access and Network setup
****************************

Since SamplerBox runs on Raspberry Pi, you can gain access to the internet via the on-board Ethernet or WiFi (Raspberry Pi 3).

Accessing Raspberry Pi
======================

.. _`monitor`:

Via HDMI monitor and keyboard
-----------------------------

You can gain access to the Raspberry Pi's commandline by connecting to a monitor using a HDMI cable and USB keyboard.

Login is: ``root/root``

.. _`ssh`:

Via SSH
-------

This section assumes you have already successfully :ref:`set up your network <network-setup>`.

You can gain access to the Raspberry Pi's commandline using an SSH client. Have a look at `this comparison of SSH clients <https://en.wikipedia.org/wiki/Comparison_of_SSH_clients>`_ for some options.

Login is: ``root/root``

.. _`sftp`:

Via SFTP
--------

This section assumes you have already successfully :ref:`set up your network <network-setup>`.

Using your favourite FTP client, eg `FileZilla <https://filezilla-project.org/>`_ you can access your SD card storage directly from your PC. You will need to know your
Pi's IP address. You can find this using the ``ifconfig`` command on the commandline, or your router's admin interface may be able to tell you.

+------------+--------------------------------+
|Host        |<YOUR PI'S IP ADDRESS>          |
+------------+--------------------------------+
|Protocol    |SFTP                            |
+------------+--------------------------------+
|Logon Type  |Normal                          |
+------------+--------------------------------+
|User        |root                            |
+------------+--------------------------------+
|Password    |root                            |
+------------+--------------------------------+


.. warning::

    File-systems are mounted as read-only. To modify files you will need to remount as read-write by issuing one of these commands (depending on what you want to modify):
    ``mount -o remount,rw /``, ``mount -o remount,rw /`boot`, ``mount -o remount,rw /samples``


.. _`network-setup`:

Network setup
=============

Ethernet configuration
----------------------


WiFi configuration
------------------

If you are using a Raspberry Pi 3 you can configure its on-board WiFi. For other RPi versions a USB WiFi dongle can be used, however they may require extra configuration.

1. Access your Pi via a :ref:`HDMI monitor and keyboard <monitor>` or :ref:`SSH <ssh>` and log in: ``Username: root`` ``Password: root``
2. Remount the root partition as read-write: ``mount -o remount,rw /``
3. Open the wireless networks configuration file: ``nano /etc/wpa_supplicant/wpa_supplicant.conf``
4. Uncomment the ``network={...}`` section and add your network SSID and passwork (psk).
5. Save and exit: ``CTRL-X`` and ``Y``
6. Reboot: ``reboot``
7. Check to see if wlan0 has acquired an IP address: ``ifconfig wlan0`` (there should be a line starting with 'inet addr')
8. Done!

.. hint::

   If your router supports static addresses, assign one to your Raspberry Pi so that it acquires the same IP address every time you power on!
