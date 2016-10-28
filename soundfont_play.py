from sf2utils.sf2parse import Sf2File
with open('rhodes.sf2', 'rb') as sf2_file:
    sf2 = Sf2File(sf2_file)



sf2dict = sf2.raw.pdta


for s in sf2dict['Shdr']:
    for i in s:
        print i

#print sf2dict['Shdr']


for s in sf2.samples:
    print s
    print '\n'