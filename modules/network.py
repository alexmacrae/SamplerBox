from wifi import Cell, Scheme
import os
import subprocess
import shlex
import string
import time
import globalvars as gv


# TODO: Option to show the IP address on the LCD


class Wifi():
    def __init__(self):

        self.ssids = None
        self.networksd = '/etc/wpa_config/networks.d/'
        self.get_ssids()

    def get_ssids(self):

        # get all cells from the air and make a list

        self.ssids = [cell.ssid for cell in Cell.all('wlan0')]

        return self.ssids

    def readwrite(self):
        if __name__ == '__main__':
            subprocess.call(['mount', '-vo', 'remount,rw', '/'])
            subprocess.call(['mount', '-vo', 'remount,rw', '/boot'])
        else:
            sysfunc.mount_boot_rw()
            sysfunc.mount_root_rw()

    def readonly(self):
        if __name__ == '__main__':
            subprocess.call(['mount', '-vfo', 'remount,ro', '/'])
            subprocess.call(['mount', '-vfo', 'remount,ro', '/boot'])
        else:
            sysfunc.mount_boot_ro()
            sysfunc.mount_root_ro()

    def save(self, ssid, psk):
        # using wpa_config save the ssid to /etc/wpa_supplicant/wpa_supplicant.conf
        # -f forces overwrite of entry if it exists
        self.readwrite()

        if psk:
            wpa_config_str = ['wpa_config', 'add', '-f', ssid, psk]
        else:
            wpa_config_str = ['wpa_config', 'add', '-fo', ssid, psk]  # -o = open, for open network

        subprocess.call(['wpa_config', 'migrate'])  # migrate any networks that may have been manually inputted into wpa_supplicant.conf to wpa_config
        subprocess.call(wpa_config_str)  # add to wpa_config (but not to wpa_supplicant.conf yet)
        subprocess.call(['wpa_config', 'make'])  # write to wpa_supplicant.conf
        time.sleep(0.5)
        self.readonly()

    def delete(self, ssid):
        self.readwrite()
        subprocess.call(['wpa_config', 'del', ssid])
        self.readonly()

    def exists(self, ssid):
        # Tests if ssid exists in wpa_supplicant.
        # Stored as a file temporarily in /etc/wpa_config/networks.d/ and wpa_config inserts into wpa_supplicant.conf upon `make`
        if os.path.isfile(self.networksd + ssid + '.conf'):
            return True
        else:
            return False

            # subprocess.call('wpa_config show \"' + ssid + '\"')

    def enable(self, ssid):
        subprocess.call(['ifup', 'wlan0'])
        subprocess.call(['dhcpcd', 'wlan0'])


class SSIDSelector(Wifi):
    def __init__(self, ssids):

        # Wifi.__init__(self)

        self.ssids = ssids
        self.ssid_pos = 0
        self.selected_ssid_name = None

    def get_selected_ssid_name(self):

        ssid_name = self.ssids[self.ssid_pos]

        return str(ssid_name)

    def next_ssid(self):

        if self.ssid_pos < len(self.ssids) - 1:

            self.ssid_pos += 1

            self.selected_ssid_name = self.get_selected_ssid_name()

            return self.selected_ssid_name

        else:

            return

    def prev_ssid(self):

        if self.ssid_pos > 0:

            self.ssid_pos -= 1

            self.selected_ssid_name = self.get_selected_ssid_name()

            return self.selected_ssid_name

        else:

            return

    def enter(self):
        pass


class PasswordInputer(SSIDSelector):
    def __init__(self, ssid):

        # Wifi.__init__(self)
        # SSIDSelector.__init__(self)
        self.selected_ssid = ssid
        self.strings = list(' ' + string.letters + string.digits + string.punctuation)
        self.strings.insert(0, ' None ')
        self.strings.insert(0, 'SAVE')
        # string.printable # digits + letters + punctuation + whitespace. ie 0123...abcd...ABCD...!"#$%&\'...\t\n\r\x0b
        self.strings_pos = 0
        self.psk = ''
        self.page = 0

    def enter(self):

        if self.strings_pos > 1:

            self.psk += self.get_current_char()

            self.strings_pos = 0  # reset position in strings var

            return self.psk

        elif self.strings_pos == 1:  # No password (None)

            self.save(ssid=self.selected_ssid, psk=None)

            return 'Saving open network: SSID="%s" (no password)' % self.selected_ssid

        elif self.strings_pos == 0 and self.psk != None:  # SAVE

            if len(self.psk) >= 8 and len(self.psk) < 64:

                self.save(ssid=self.selected_ssid, psk=self.psk)

                return 'Saving network: SSID="%s" Password="%s"' % (self.selected_ssid, self.psk)

            else:

                print 'Password is not long enough. Must be 8...63 characters'

    def get_current_char(self):

        return self.strings[self.strings_pos]

    def get_next_char(self):

        if self.strings_pos > ((gv.LCD_COLS * self.page) - 11 + gv.LCD_COLS):  # subtract 11 because 'SAVE' and 'None' are like 2 characters
            self.page += 1

        if self.strings_pos < len(self.strings):
            self.strings_pos += 1

            return self.strings[self.strings_pos]

    def get_prev_char(self):

        if self.strings_pos < ((gv.LCD_COLS * self.page) - 11 + gv.LCD_COLS):  # subtract 11 because 'SAVE' and 'None' are like 2 characters
            self.page -= 1

        if self.strings_pos > 0:
            self.strings_pos -= 1

            return self.strings[self.strings_pos]


class NetworkInfo:

    def get_ip_address(self, interface):

        # Not a simple subprocess.call due to the need for a PIPE in the command
        # https://docs.python.org/2/library/subprocess.html#replacing-shell-pipeline
        command_line_1 = "ip addr show " + interface
        args1 = shlex.split(command_line_1)
        command_line_2 = "grep -Po 'inet \K[\d.]+'"
        args2 = shlex.split(command_line_2)

        command_line_1 = subprocess.Popen(args1, stdout=subprocess.PIPE)
        command_line_2 = subprocess.Popen(args2, stdin=command_line_1.stdout, stdout=subprocess.PIPE)
        command_line_1.stdout.close()

        ip_address = command_line_2.communicate()[0]
        ip_address = ip_address.rstrip()

        if ip_address == '':
            ip_address = 'NOT CONNECTED'

        return str(ip_address)


if __name__ == '__main__':

    print '----START TESTING WIFI----'

    w = Wifi()
    print w.ssids

    ss = SSIDSelector(w.ssids)

    print 'init SSID:', ss.get_selected_ssid_name()

    ss.next_ssid()
    ss.next_ssid()
    ss.next_ssid()

    print 'selected SSID:', ss.get_selected_ssid_name()

    pi = PasswordInputer(ss.get_selected_ssid_name())

    pi.get_next_char()
    pi.get_next_char()
    print pi.enter()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    print pi.enter()
    pi.get_next_char()
    pi.get_next_char()
    print pi.enter()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    print pi.enter()
    pi.get_next_char()
    pi.get_next_char()
    print pi.enter()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    print pi.enter()
    pi.get_next_char()
    pi.get_next_char()
    print pi.enter()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    pi.get_next_char()
    print pi.enter()

    print pi.enter()

else:
    import systemfunctions as sysfunc
