import threading
import time
import serial # pip install pyserial

class MIDISerial:

    def __init__(self, midicallback=None):

        self.midicallback = midicallback

    def start(self):
        try:
            # see hack in /boot/cmline.txt : 38400 is 31250 baud for MIDI!
            ser = serial.Serial('/dev/ttyAMA0', baudrate=38400)
            def midi_serial_callback():
                message = [0, 0, 0]
                runningstatus = 0
                while True:
                    i = 0
                    while i < 3:
                        data = ord(ser.read(1))  # read a byte
                        if data >> 7 != 0:
                            # status byte! this is the beginning of a midi message: http://www.midi.org/techspecs/midimessages.php
                            i = 0
                            runningstatus = data
                        elif i == 0 and runningstatus > 0:  # use stored running status if available
                            message[i] = runningstatus
                            i += 1
                        message[i] = data
                        i += 1
                        if i == 2 and message[0] >> 4 == 12:  # program change: don't wait for a third byte: it has only 2 bytes
                            message[2] = 0
                            i = 3

                    if self.midicallback:
                        self.midicallback.callback(src='MIDISERIALPORT', message=message, time_stamp=None)
                    else:
                        print message


            MidiThread = threading.Thread(target=midi_serial_callback)
            MidiThread.daemon = True
            MidiThread.start()
        except:
            print '\r\n [!] Could not start MIDI serial'




if __name__ == '__main__':

    print 'Testing MIDI serial'
    ms = MIDISerial()
    ms.start()
    while True:

        time.sleep(0.05)