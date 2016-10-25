import cPickle
import os

filename = 'midimaps.pkl'
class MidiMapping:
    maps = None
    def __init__(self):
        MidiMapping.maps = self.loadMaps()
        print '------------------'


    # maps = {
#     'Launchkey 61 3': {
#         (176, 41): {
#             'name': 'Attack',
#             'fn': 'attack'
#             # maybe a velocity range
#         },
#         (144, 60): {
#             'note': 1
#         },
#         (128, 60): {
#             'note': 1
#         }
#     },
#     'nanoKONTROL2 1': {
#         (176, 64): {
#             'name': 'Decay',
#             'fn': 'decay'
#         }
#     }
# }


    def saveMaps(self, obj):
        global filename

        with open(filename, 'wb') as f:
            cPickle.dump(obj, f, 0)
            print '-- Saving pkl file --'


    def loadMaps(self):
        global filename

        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                try:
                    return cPickle.load(f)
                except:
                    return {} # file exists but it's empty. Start afresh with an empty dict

        else:
            self.saveMaps({}) # file not found: create a new empty file




#maps = loadMaps()



#print maps

#print devices.keys()

#exit()