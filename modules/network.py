from wifi import Cell, Scheme
import os
import subprocess
import string

class Wifi():
    def __init__(self):
        self.ssids = None
        self.networksd = '/etc/wpa_config/networks.d/'

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
            subprocess.call(['mount', '-vo', 'remount,ro', '/'])
            subprocess.call(['mount', '-vo', 'remount,ro', '/boot'])
        else:
            sysfunc.mount_boot_ro()
            sysfunc.mount_root_ro()

    def save(self, ssid, psk):
        # using wpa_config save the ssid to /etc/wpa_supplicant/wpa_supplicant.conf
        # -f forces overwrite of entry if it exists
        self.readwrite()
        wpa_config_str = ['wpa_config', 'add', '-f', '\"'+ssid+'\"', '\"'+psk+'\"']
        subprocess.call(['wpa_config','migrate'])  # migrate any networks that may have been manually inputted into wpa_supplicant.conf to wpa_config
        subprocess.call(wpa_config_str)  # add to wpa_config (but not to wpa_supplicant.conf yet)
        subprocess.call(['wpa_config', 'make'])  # write to wpa_supplicant.conf
        self.readonly()

    def delete(self, ssid):
        self.readwrite()
        subprocess.call(['wpa_config', 'del', '\"' + ssid + '\"'])
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
    def __init__(self, wifi_obj):

        self.wifi_obj = wifi_obj
        self.get_ssids()
        self.strings = ' ' + string.digits + ' ' + string.letters + string.punctuation
        # string.printable # digits + letters + punctuation + whitespace. ie 0123...abcd...ABCD...!"#$%&\'...\t\n\r\x0b
        self.strings_pos = -1
        self.psk = ''


    def get_ssid(self, i=0):

        ssid_name = self.ssids[i]

        return ssid_name

    def enter(self):

        if self.strings_pos >= 0:
            self.psk += self.get_current_char()
            self.strings_pos = 0 # reset position in strings var
        # self.select_next_char()


    # def select_next_char(self):




    def get_current_char(self):

        if self.strings_pos >= 0:

            return self.strings[self.strings_pos]

        else:

            return 'SAVE'

    def get_next_char(self):

        if self.strings_pos < len(self.strings):

            self.strings_pos += 1

            return self.strings[self.strings_pos]


    def get_prev_char(self):

        if self.strings_pos > 0:

            self.strings_pos -= 1

            return self.strings[self.strings_pos]

        else:

            return 'SAVE'

    def get_strings(self):

        for i in self.strings:
            print i

        # return string.printable[30]



if __name__ == '__main__':
    w = Wifi()
    ssid_selector = SSIDSelector(w)
    # print w.get_ssids()

    ssid_selector.get_next_char()
    ssid_selector.get_next_char()
    ssid_selector.enter()
    ssid_selector.get_next_char()
    ssid_selector.enter()
    ssid_selector.get_next_char()
    ssid_selector.get_next_char()
    ssid_selector.enter()
    ssid_selector.get_next_char()
    ssid_selector.get_next_char()
    ssid_selector.get_next_char()
    ssid_selector.get_next_char()
    ssid_selector.enter()
    print ssid_selector.psk


    # w.save('New_SSID', 'New_password')

else:
    import systemfunctions as sysfunc
