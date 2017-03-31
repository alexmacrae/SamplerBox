import globalvars as gv
from os.path import isdir
import re


# Alphanumeric sorting
_nsre = re.compile('([0-9]+)')
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


class Setlist:
    def __init__(self):

        if gv.SYSTEM_MODE == 1:

            self.find_missing_folders()
            self.remove_missing_setlist_songs()
            self.find_and_add_new_folders()
            self.update()

        elif gv.SYSTEM_MODE == 2:

            # Sort the song folder list alphanumerically
            gv.SONG_FOLDERS_LIST.sort(key=natural_sort_key)
            gv.SETLIST_LIST = gv.SONG_FOLDERS_LIST

        for i in xrange(len(gv.SETLIST_LIST)):
            gv.samples_indices.append(i)


    def write_setlist(self, list_to_write):
        print('>>>> SETLIST: Writing to setlist')
        setlist = open(gv.SETLIST_FILE_PATH, "w")

        list_to_write = list(filter(None, list_to_write))  # remove empty strings / empty lines
        for song in list_to_write:
            setlist.write(song + '\n')
        setlist.close()
        # Let's keep SETLIST_LIST the same as before any rearrangements. We let the samples_indices find the name
        # self.update()

    def update(self):
        gv.SETLIST_LIST = open(gv.SETLIST_FILE_PATH).read().splitlines()

    def find_missing_folders(self):
        # Check to see if the song name in the setlist matches the name of a folder.
        # If it doesn't, mark it by prepending an *asterix and rewrite the setlist file.

        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()
        songs_in_setlist = list(filter(None, songs_in_setlist))  # remove empty strings / empty lines
        changes_in_dir = False
        k = 0
        for song_name in songs_in_setlist:
            i = 0
            for song_folder_name in gv.SONG_FOLDERS_LIST:

                if (song_name == song_folder_name):
                    # print song_name + ' was found'
                    break
                elif (song_name.replace('* ', '') == song_folder_name):
                    # print song_name + ' was found - previous lost'
                    songs_in_setlist[k] = song_name.replace('* ', '')
                    continue
                else:
                    if (i == len(gv.SONG_FOLDERS_LIST) - 1):
                        print  '>>>> SETLIST: Folder for [%s] was not found\n' % song_name
                        songs_in_setlist[k] = '* ' + song_name.replace('* ', '')
                        changes_in_dir = True
                        break

                i += 1
            k += 1

        if (changes_in_dir):
            self.write_setlist(songs_in_setlist)
        else:
            print('>>>> SETLIST: No missing folders detected\n')

    def find_and_add_new_folders(self):
        # Check for new song folders and add them to the end of the setlist

        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()
        songs_in_setlist = list(filter(None, songs_in_setlist))  # remove empty strings / empty lines
        changes_in_dir = False

        if (set(songs_in_setlist).intersection(gv.SONG_FOLDERS_LIST) != len(gv.SONG_FOLDERS_LIST) and len(
                songs_in_setlist) != 0):

            for song_folder_name in gv.SONG_FOLDERS_LIST:
                i = 0
                if isdir(gv.SAMPLES_DIR + '/' + song_folder_name):  # check if entry is a folder
                    for song_name in songs_in_setlist:
                        if (song_folder_name == song_name):
                            break
                        elif (i == len(songs_in_setlist) - 1):
                            print '>>>> SETLIST: New setlist entry for [%s]\n' % song_folder_name
                            changes_in_dir = True
                            songs_in_setlist.append(song_folder_name)
                            break
                        i += 1
                else:
                    print '>>>> SETLIST: [%s] is not a folder. Skipping.\n' % song_folder_name
        elif (len(songs_in_setlist) == 0):
            songs_in_setlist = gv.SONG_FOLDERS_LIST
            changes_in_dir = True
            print '>>>> SETLIST: Is empty -> adding all foldings\n'

        if (changes_in_dir):
            self.write_setlist(songs_in_setlist)
        else:
            print('>>>> SETLIST: No new folders found -> do nothing\n')

    # ______________________________________________________________________________


    def remove_missing_setlist_songs(self):
        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()
        i = 0
        for song in songs_in_setlist:
            if ('* ' in song):
                del songs_in_setlist[i]
                self.write_setlist(songs_in_setlist)
            i += 1
