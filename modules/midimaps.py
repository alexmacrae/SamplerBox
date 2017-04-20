import cPickle
import os
import globalvars as gv
import systemfunctions as sysfunc

class MidiMapping:

    maps = None

    def __init__(self):

        self.filename = gv.MIDIMAPS_FILE_PATH
        # Load the current mappings into maps var
        self.maps = self.load_maps()


########################
# EXAMPLE OF MAPPING
# STORED IN midimaps.pkl
########################
#
# {u'iCON G_Boar V1.01': {(176, 78): {'name': 'Voice 4', 'fn': 'Voices.voice4'},
#                         (176, 75): {'name': 'Voice 1', 'fn': 'Voices.voice1'},
#                         (176, 77): {'name': 'Voice 3', 'fn': 'Voices.voice3'},
#                         (176, 76): {'name': 'Voice 2', 'fn': 'Voices.voice2'}},
#  u'Launchkey 61': {(153, 37): {'name': 'Voice 2', 'fn': 'Voices.voice2'},
#                    (153, 38): {'name': 'Voice 3', 'fn': 'Voices.voice3'},
#                    (153, 36): {'name': 'Voice 1', 'fn': 'Voices.voice1'},
#                    (153, 39): {'name': 'Voice 4', 'fn': 'Voices.voice4'}},
#  u'nanoKONTROL2': {(176, 54): {'name': 'Voice 4', 'fn': 'Voices.voice4'}}}


    def save_maps(self, obj):
        sysfunc.mount_boot_rw()  # remount `/samples` as read-write (if using SD card)
        with open(self.filename, 'w') as f:
            cPickle.dump(obj, f, 0)
            print '##### Saving new file (%s) #####' % (gv.MIDIMAPS_FILE_PATH)
        sysfunc.mount_boot_ro()  # remount as read-only

    def load_maps(self):
        if os.path.isfile(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    return cPickle.load(f)
                except:
                    return {}  # file exists but it's empty. Start afresh with an empty dict

        else:
            self.save_maps({})  # file not found: create a new empty file
            return {}  # file has been created, but maps needs an empty dict

