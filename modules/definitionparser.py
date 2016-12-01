import os
from modules import globalvars as gv

keywords_to_try = (('gv.gain', 'gain'),
                   ('gv.globaltranspose', 'transpose'),
                   ('gv.FADEOUTLENGTH', 'release'),
                   ('gv.PITCHBITS', 'pitchbend'),
                   ('gv.sample_mode', 'mode'),
                   ('gv.velocity_mode', 'velmode'))


def get_patterns_from_file(definitionfname, keywords_dict):
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

    return existing_patterns


class DefinitionParser:
    def __init__(self, basename):

        self.basename = basename
        self.dirname = os.path.join(gv.SAMPLES_DIR, basename)
        self.definitionfname = os.path.join(self.dirname, "definition.txt")
        self.existing_patterns = {}
        self.new_patterns = {}
        self.combined_patterns = {}

        self.keywords_dict = {
            0: {'%%gain': (-10, 10)},
            1: {'%%mode': ['keyb', 'once', 'on64', 'loop', 'loo2']},
            2: {'%%velmode': ['sample', 'accurate']},
            3: {'%%release': (0, 100)},
            4: {'%%transpose': (-100, 100)},
            5: {'%%pitchbend': (-24, 24)}
        }

        self.keywords_defaults_dict = {
            '%%gain': 1,
            '%%mode': 0,
            '%%velmode': gv.VELOCITY_MODE_DEFAULT.lower(),
            '%%release': 3,
            '%%transpose': 0,
            '%%pitchbend': 2,
        }

        self.existing_patterns = get_patterns_from_file(self.definitionfname, self.keywords_dict)

        print '##### Existing definition.txt patterns #####'
        print self.existing_patterns
        print '############################################', '\n'

    def compare_existing_patterns(self):
        print self.new_patterns, '<<<<<<<<<<<<<<<<<<<<<<<'
        for n, value in self.new_patterns.iteritems():

            if n in self.existing_patterns:
                print 'OVERWRITING EXISTING: %s is in the definition.txt already.' \
                      'Overwritting its value (%s)' % (n, str(value))  # debug
                self.existing_patterns.pop(n)

        self.combined_patterns = self.new_patterns.copy()
        self.combined_patterns.update(self.existing_patterns)  # merge self.new_patterns and existing_patters dicts

    def set_new_keyword(self, keyword, value):
        keyword = keyword.lower()
        print type(value), '##########'
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

    def write_definition_file(self):
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

# dp = DefinitionParser('WAIDH')
# print dp.basename,'<<<<<<<'

# print '##### New patterns #####'
# dp.set_new_keyword('%%mode', 'once')
# dp.set_new_keyword('%%release', 100)
# dp.set_new_keyword('%%release', 101)
# dp.set_new_keyword('%%gain', 5)
# dp.set_new_keyword('%%velmode', 'accurate')
# print '########################', '\n'

# print '##### Write new patterns #####'
# dp.compare_existing_patterns()
# print '##############################', '\n'

# print '##### Write to definition.txt #####'
# dp.write_definition_file()
# print '###################################', '\n'
