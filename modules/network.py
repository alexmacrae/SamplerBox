from wifi import Cell, Scheme
import os
import subprocess
import string
import time

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
        wpa_config_str = ['wpa_config', 'add', '-f', ssid, psk]
        subprocess.call(['wpa_config','migrate'])  # migrate any networks that may have been manually inputted into wpa_supplicant.conf to wpa_config
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

        if self.ssid_pos < len(self.ssids):

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
        self.strings.insert(0, 'SAVE')
        # string.printable # digits + letters + punctuation + whitespace. ie 0123...abcd...ABCD...!"#$%&\'...\t\n\r\x0b
        self.strings_pos = 0
        self.psk = ''

    def enter(self):

        if self.strings_pos > 0:

            self.psk += self.get_current_char()

            self.strings_pos = 0 # reset position in strings var

            return self.psk

        elif self.strings_pos == 0 and self.psk != None:

            if len(self.psk) >= 8 and len(self.psk) < 64:

                print self.selected_ssid, self.psk,'<<<<'

                self.save(ssid=self.selected_ssid, psk=self.psk)

                return 'Saving network: SSID="%s" Password="%s"' % (self.selected_ssid, self.psk)

            else:

                print 'Password is not long enough. Must be 8...63 characters'



    def get_current_char(self):

        return self.strings[self.strings_pos]


    def get_next_char(self):

        if self.strings_pos < len(self.strings):

            self.strings_pos += 1

            return self.strings[self.strings_pos]


    def get_prev_char(self):

        if self.strings_pos > 0:

            self.strings_pos -= 1

            return self.strings[self.strings_pos]



if __name__ == '__main__':

    print '----START TESTING WIFI----'

    w = Wifi()
    print w.ssids

    ss = SSIDSelector(w.ssids)

    print 'init SSID:',ss.get_selected_ssid_name()

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
