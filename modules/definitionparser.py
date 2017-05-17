import os
from modules import globalvars as gv
import systemfunctions as sysfunc

keywords_to_try = (('gv.gain', 'gain'),
                   ('gv.globaltranspose', 'transpose'),
                   ('gv.PRERELEASE', 'release'),
                   ('gv.pitchnotes', 'pitchbend'),
                   ('gv.sample_mode', 'mode'),
                   ('gv.velocity_mode', 'velmode'),
                   ('gv.fillnotes', 'fillnotes'))

keywords_dict = {
    0: {'name': '%%gain', 'type': 'range', 'min': 0.1, 'max': 10.0, 'increment': 0.1, 'default': 1.0},
    1: {'name': '%%mode', 'type': 'options', 'options': ['Keyb', 'Once', 'On64', 'Loop', 'Loo2'], 'default': 0},
    2: {'name': '%%velmode', 'type': 'options', 'options': ['Sample', 'Accurate'], 'default': 1},
    3: {'name': '%%release', 'type': 'range', 'min': 0, 'max': 127, 'increment': 1, 'default': 30},
    4: {'name': '%%transpose', 'type': 'range', 'min': -48, 'max': 48, 'increment': 1, 'default': 0},
    5: {'name': '%%pitchbend', 'type': 'range', 'min': 0, 'max': 24, 'increment': 1, 'default': 7},
    6: {'name': '%%fillnotes', 'type': 'options', 'options': ['Y','N'], 'default': 0}
}

###############################
# GET DEFAULT VALUE FOR KEYWORD
###############################

def get_default(name):
    keyword_item = {}
    for item in keywords_dict.iteritems():
        if item[1].get('name') == name: keyword_item = item[1]

    if keyword_item.get('type') == 'range':
        return keyword_item.get('default')
    elif keyword_item.get('type') == 'options':
        val = keyword_item.get('options')[keyword_item.get('default')]
        if type(val) == str:
            return val.title()
        else:
            return val

def get_option_index(item, option):
    options_list = item.get('options')
    option = option.title()
    indices = [i for i, s in enumerate(options_list) if option in s]
    return indices[0]  # there will only ever be 1 item in the list of indices

class DefinitionParser:
    def __init__(self, basename):

        self.basename = basename
        self.dirname = os.path.join(gv.SAMPLES_DIR, basename)
        self.definitionfname = os.path.join(self.dirname, "definition.txt")
        self.existing_patterns = {}
        self.new_patterns = {}
        self.combined_patterns = {}

        self.keywords_dict = keywords_dict

        # self.keywords_defaults_dict = keywords_defaults_dict

        self.existing_patterns = self.get_patterns_from_file()
        self.original_patterns = self.existing_patterns.copy() # in case we cancel

        print '##### Existing definition.txt patterns #####'
        print self.existing_patterns
        print '############################################', '\r'

    ############################################
    # COMPARE EXISTING
    # And overwrite settings with newer value(s)
    ############################################

    def update_existing_patterns(self):
        print '\r#### START COMPARING NEW AND INITIAL PATTERNS ####'
        print 'New patterns to save: %s' % str(self.new_patterns)
        for n, value in self.new_patterns.iteritems():

            if n in self.existing_patterns:
                print 'OVERWRITING EXISTING: %s is in the definition.txt already. ' \
                      'Overwriting its value: Old=%s, New=%s' % (n, str(self.existing_patterns.get(n)), str(value))  # debug
                self.existing_patterns.pop(n)

        self.combined_patterns = self.new_patterns.copy()
        self.combined_patterns.update(self.existing_patterns)  # merge self.new_patterns and existing_patterns dicts
        self.existing_patterns = self.combined_patterns
        print self.existing_patterns

        print '#### END COMPARING NEW AND INITIAL PATTERNS ####\r'

    #################
    # SET NEW KEYWORD
    #################

    def set_new_keyword(self, keyword, value):
        keyword = keyword.lower()
        print '\r\r#### START SETTING NEW KEYWORDS ####\r'
        if type(value) == float:
            value = round(value, 1) # bug: value sometimes is 1.299999999. round() to 1 dec point. eg 1.3
        print 'Setting %s to %s' % (keyword, str(value))
        self.new_patterns[keyword] =  value
        print self.new_patterns
        # for i, item in self.keywords_dict.iteritems():
        #     for k, v in item.iteritems():
        #         print k, v
        #         if k == 'name':
        #             if value in v:
        #                 new_definition = (keyword, value)
        #                 # print 'Setting ', new_definition  # debug
        #                 print 1
        #                 self.new_patterns[keyword] = value
        #                 break
        #             else:
        #                 print 'ERROR: %s is not a suitable value for %s' % (value, keyword)  # debug

        print '\r#### END SETTING NEW KEYWORDS ####\r'



    def update_samples_dict(self, preset, name, value):

        actual_preset = gv.samples_indices[preset] # in case setlist has been rearranged this session

        print name, value
        for k,v in gv.samples[actual_preset]['keywords'].iteritems():
            if k in name:
                print k,v
                gv.samples[actual_preset]['keywords'][k] = value # update the preset's keywords dict


        print gv.samples[actual_preset]['keywords']

    #########################
    # WRITE DEFINITION FILE #
    #########################

    def write_definition_file(self):
        print '\r#### START WRITING %s/definition.txt ####\r' % self.basename
        sysfunc.mount_samples_dir_rw()  # remount `/samples` as read-write (if using SD card)
        f = open(self.definitionfname, 'w')
        for keyword, value in self.combined_patterns.iteritems():
            if 'wav_definition' not in keyword:
                line = keyword + '=' + str(value) + '\n'
                f.write(line)
                print line.strip('\n')  # debug
        for keyword, value in self.combined_patterns.iteritems():  # 2 loops so that wav_definition(s) are last lines
            if 'wav_definition_lines' in keyword: # wav_definition_lines is a dict. ie 'wav_definition_lines': {0:'C.wav', 1:'D.wav'}
                for k, v in value.iteritems():
                    line = str(v) + '\n'
                    f.write(line)
                    print line.strip('\n')  # debug
        f.close()
        sysfunc.mount_samples_dir_ro()  # remount `/samples` back to read-only (if using SD card)
        print '\r#### END WRITING %s/definition.txt ####\r' % self.basename

    ##########################
    # GET PATTERNS FROM FILE #
    ##########################

    def get_patterns_from_file(self):
        print '#### START GET PATTERNS FROM FILE ####'
        existing_patterns = {}
        existing_patterns['wav_definition_lines'] = {}
        with open(self.definitionfname, 'r') as definitionfile:
            w = 0
            for i, pattern in enumerate(definitionfile):
                for k, item in self.keywords_dict.iteritems():
                    keyword = item.get('name')
                    if keyword in pattern:
                        print 'Found %s' % pattern
                        value = pattern.split('=')[1].strip() # is a string
                        if item.get('type') == 'range':
                            # if type is range, value will be an int or float
                            if '.' in value:
                                value = float(value)
                            else:
                                value = int(value)

                        existing_patterns[keyword] = value

                if '%%' not in pattern or '.wav' in pattern:  # get sample lines
                    existing_patterns['wav_definition_lines'][w] = pattern.strip('\n')
                    # existing_patterns['wav_definition_' + str(w)] = pattern.strip('\n')
                    w += 1

        print '#### END GET PATTERNS FROM FILE ####'

        return existing_patterns


    def change_item_value(self, preset, item, direction=None):

        keyword = item.get('name')  # eg %%gain or %%mode etc
        value_new = None

        if direction:
            value_existing = self.existing_patterns.get(keyword)
        else:
            value_existing = get_default(keyword)
            value_new = value_existing # value_exists is default, and isn't in the definition.txt yet. Therefore also make it value_new

        if item.get('type') == 'range':

            min_val = item.get('min')
            max_val = item.get('max')
            inc = item.get('increment')

            if direction == 'DOWN':
                inc *= -1

            if direction:
                value_new = max(min(max_val, (value_existing + inc)), min_val)  # keeps value within min/max range


        elif item.get('type') == 'options':

            value_existing = value_existing.title()
            options_length = len(item.get('options'))
            i = item.get('options').index(value_existing)
            inc = 1
            if direction == 'DOWN':
                inc *= -1
            new_index = max(min(options_length, (i + inc)), 0)

            if direction:
                value_new = item.get('options')[new_index]

        self.set_new_keyword(keyword=keyword, value=value_new)
        self.update_samples_dict(preset, keyword, value_new)
        self.set_global_from_keyword(keyword, value_new)
        self.update_existing_patterns()

        if keyword.lower() == '%%mode' or keyword.lower() == '%%fillnotes':

            # need to write definition because ls.actually_load() reads the file again
            self.write_definition_file()

            # need to destroy Sample objects associated with dict because %%mode determines how they are loaded
            # TODO: we can probably tell every Sound object to update themselves for %%mode. %%fillnotes can have the fillnotes dict cleared
            gv.ls.kill_preset(preset=preset)
            gv.ls.load_preset() # reload samples. %%mode and %%fillnotes determines how they are loaded


    def set_global_from_keyword(self, keyword, value):
        keyword = keyword.strip('%%')
        if isinstance(value, str): value = value.title()
        for gvar, k in keywords_to_try:
            if k == keyword:
                print '\r>>>> Setting global from keyword. %s: %s' % (keyword, str(value))  # debug
                exec (gvar + '=value')  # set the global variable


    def revert_to_original_settings(self, preset, keyword):

        self.new_patterns = {}
        self.existing_patterns = self.original_patterns
        value_original = self.existing_patterns.get(keyword)
        value_default = get_default(keyword)
        if value_original:
            value = value_original
        else:
            value = value_default

        self.update_samples_dict(preset, keyword, value)
        self.set_global_from_keyword(keyword, value)
        self.update_existing_patterns()