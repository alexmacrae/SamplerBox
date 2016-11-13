#########################################
# 7-SEGMENT DISPLAY
#########################################
import globalvars as gv
import time

if gv.USE_I2C_7SEGMENTDISPLAY and gv.IS_DEBIAN:
    import smbus

    bus = smbus.SMBus(gv.GPIO_7SEG)     # using I2C

    def display(s):
        for k in '\x76\x79\x00' + s:     # position cursor at 0
            try:
                bus.write_byte(0x71, ord(k))
            except:
                try:
                    bus.write_byte(0x71, ord(k))
                except:
                    pass
            time.sleep(0.002)

    display('----')
    time.sleep(0.5)
