import cPickle
import os



class MidiMapping:

    maps = None

    def __init__(self):

        self.filename = 'midimaps.pkl'
        # Load the current mappings into maps var
        MidiMapping.maps = self.loadMaps()



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


    def saveMaps(self, obj):
        with open(self.filename, 'wb') as f:
            cPickle.dump(obj, f, 0)
            print '-- Saving pkl file --'

    def loadMaps(self):
        if os.path.isfile(self.filename):
            with open(self.filename, 'rb') as f:
                try:
                    return cPickle.load(f)
                except:
                    return {}  # file exists but it's empty. Start afresh with an empty dict

        else:
            self.saveMaps({})  # file not found: create a new empty file

