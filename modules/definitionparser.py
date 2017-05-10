import os
from modules import globalvars as gv
from modules import systemfunctions as sysfunc

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
    5: {'name': '%%pitchbend', 'type': 'range', 'min': 0, 'max': 24, 'increment': 1, 'default': 0},
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

        print '##### Existing definition.txt patterns #####'
        print self.existing_patterns
        print '############################################', '\r'

    ############################################
    # COMPARE EXISTING
    # And overwrite settings with newer value(s)
    ############################################

    def compare_existing_patterns(self):
        print '\r#### START COMPARING NEW AND INITAL PATTERNS ####'
        print 'New patterns to save: %s' % str(self.new_patterns)
        for n, value in self.new_patterns.iteritems():

            if n in self.existing_patterns:
                print 'OVERWRITING EXISTING: %s is in the definition.txt already.' \
                      'Overwritting its value (%s)' % (n, str(value))  # debug
                self.existing_patterns.pop(n)

        self.combined_patterns = self.new_patterns.copy()
        self.combined_patterns.update(self.existing_patterns)  # merge self.new_patterns and existing_patters dicts

        print '#### END COMPARING NEW AND INITAL PATTERNS ####\r'

    #################
    # SET NEW KEYWORD
    #################

    def set_new_keyword(self, keyword, value):
        keyword = keyword.lower()
        print '\r\r#### START SETTING NEW KEYWORDS ####\r'
        print 'Setting %s to %s' % (keyword, str(value))
        self.new_patterns[keyword] = value
        # for i, item in self.keywords_dict.iteritems():
        #     for k, v in item.iteritems():
        #         print k, v
        #         if k == keyword:
        #             if value in v:
        #                 new_definition = (keyword, value)
        #                 print 'Setting ', new_definition  # debug
        #                 self.new_patterns[keyword] = value
        #             else:
        #                 print 'ERROR: %s is not a suitable value for %s' % (value, keyword)  # debug

        print '\r#### END SETTING NEW KEYWORDS ####\r'

    #########################
    # WRITE DEFINITION FILE #
    #########################

    def write_definition_file(self):
        print '\r#### START WRITING %s/definition.txt ####\r' % self.basename
        sysfunc.mount_samples_rw()  # remount `/samples` as read-write (if using SD card)
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
        sysfunc.mount_samples_ro()  # remount `/samples` back to read-only (if using SD card)
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
