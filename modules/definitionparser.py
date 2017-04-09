import os
from modules import globalvars as gv

keywords_to_try = (('gv.gain', 'gain'),
                   ('gv.globaltranspose', 'transpose'),
                   ('gv.PRERELEASE', 'release'),
                   ('gv.pitchnotes', 'pitchbend'),
                   ('gv.sample_mode', 'mode'),
                   ('gv.velocity_mode', 'velmode'))

keywords_dict = {
            0: {'%%gain': (0.1, 10.0)},
            1: {'%%mode': ['keyb', 'once', 'on64', 'loop', 'loo2']},
            2: {'%%velmode': ['sample', 'accurate']},
            3: {'%%release': (0, 127)},
            4: {'%%transpose': (-48, 48)},
            5: {'%%pitchbend': (0, 24)}
}
keywords_defaults_dict = {
            '%%gain': 1.0,
            '%%mode': gv.SAMPLE_MODE_DEFAULT.lower(),
            '%%velmode': gv.VELOCITY_MODE_DEFAULT.lower(),
            '%%release': gv.BOXRELEASE,
            '%%transpose': 0,
            '%%pitchbend': gv.PITCHRANGE_DEFAULT,
        }

class DefinitionParser:
    def __init__(self, basename):

        self.basename = basename
        self.dirname = os.path.join(gv.SAMPLES_DIR, basename)
        self.definitionfname = os.path.join(self.dirname, "definition.txt")
        self.existing_patterns = {}
        self.new_patterns = {}
        self.combined_patterns = {}

        self.keywords_dict = keywords_dict

        self.keywords_defaults_dict = keywords_defaults_dict

        self.existing_patterns = self.get_patterns_from_file(self.definitionfname, self.keywords_dict)

        print '##### Existing definition.txt patterns #####'
        print self.existing_patterns
        print '############################################', '\r'

    ############################################
    # COMPARE EXISTING
    # And overwrite settings with newer value(s)
    ############################################

    def compare_existing_patterns(self):
        print '\r#### START COMPARING NEW AND INITAL PATTERNS ####'
        print self.new_patterns, '<<<<<<<<<<<<<<<<<<<<<<<'
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
        for i, item in self.keywords_dict.iteritems():
            for k, v in item.iteritems():
                print k, v
                if k == keyword:
                    if isinstance(v, list):
                        if value in v:
                            new_definition = (keyword, value)
                            print 'Setting ', new_definition  # debug
                            self.new_patterns[keyword] = value
                        else:
                            print 'ERROR: %s is not a suitable value for %s' % (value, keyword)  # debug
                    elif isinstance(v, tuple):
                        minn = v[0]
                        maxn = v[1]
                        if minn <= value <= maxn:
                            new_definition = (keyword, value)
                            print 'Setting ', new_definition  # debug
                            self.new_patterns[keyword] = value
                        else:
                            print 'ERROR: Value (%d) is out of range for %s. Min=%d, Max=%d' % (
                                value, keyword, minn, maxn)  # debug

        print '\r#### END SETTING NEW KEYWORDS ####\r'

    #########################
    # WRITE DEFINITION FILE #
    #########################

    def write_definition_file(self):
        print '\r#### START WRITING definition.txt ####\r'
        definitionfname = os.path.join(self.dirname, "definition.txt")
        f = open(definitionfname, 'w')
        for keyword, value in self.combined_patterns.iteritems():
            if 'wav_definition' not in keyword:
                line = keyword + '=' + str(value) + '\n'
                f.write(line)
                print line.strip('\n')  # debug
        for keyword, value in self.combined_patterns.iteritems():  # 2 loops so that wav_definition(s) are last lines
            if 'wav_definition' in keyword:
                line = str(value) + '\n'
                f.write(line)
                print line.strip('\n')  # debug
        f.close()
        print '\r#### END WRITING definition.txt ####\r'

    ##########################
    # GET PATTERNS FROM FILE #
    ##########################

    def get_patterns_from_file(self, definitionfname, keywords_dict):
        print '#### START GET PATTERNS FROM FILE ####'
        existing_patterns = {}
        with open(definitionfname, 'r') as definitionfile:
            w = 1
            for i, pattern in enumerate(definitionfile):
                for k, item in keywords_dict.iteritems():
                    keyword = item.items()[0][0]
                    if keyword in pattern:
                        print pattern
                        value = pattern.split('=')[1].strip()
                        existing_patterns[keyword] = value

                if '%%' not in pattern or '.wav' in pattern:  # get .wav lines
                    existing_patterns['wav_definition_' + str(w)] = pattern.strip('\n')
                    w += 1

        print '#### END GET PATTERNS FROM FILE ####'

        return existing_patterns

