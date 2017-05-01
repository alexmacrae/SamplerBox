import globalvars as gv
import os
import re
import systemfunctions as sysfunc

IGNORE_FOLDERS = ['System Volume Information', 'System\ Volume\ Information', 'FOUND.000',
                  'FOUND.001', 'FOUND.002', 'FOUND.003', 'FOUND.004', 'FOUND.005', 'FOUND.006',
                  'FOUND.007', 'lost+found']


class Setlist:
    def __init__(self):

        self.song_folders_list = self.get_song_folders_list()

        if gv.SYSTEM_MODE == 1:

            self.find_missing_folders()
            self.remove_missing_setlist_songs()
            self.find_and_add_new_folders()
            self.update()

        elif gv.SYSTEM_MODE == 2:

            # Sort the song folder list alphanumerically
            self.song_folders_list.sort(key=self.natural_sort_key)
            gv.SETLIST_LIST = self.song_folders_list

        for i in xrange(len(gv.SETLIST_LIST)):
            gv.samples_indices.append(i)

    def natural_sort_key(self, s):
        # Alphanumeric sorting
        _nsre = re.compile('([0-9]+)')
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(_nsre, s)]

    def get_song_folders_list(self):

        all_folders = [d for d in os.listdir(gv.SAMPLES_DIR) if os.path.isdir(os.path.join(gv.SAMPLES_DIR, d))]
        all_qualified_folders = []

        for song_folder_name in all_folders:
            if os.path.isdir(gv.SAMPLES_DIR + '/' + song_folder_name) \
                    and song_folder_name not in IGNORE_FOLDERS \
                    and song_folder_name[0] != '.' \
                    and os.listdir(gv.SAMPLES_DIR + '/' + song_folder_name) != []:
                all_qualified_folders.append(song_folder_name)

        return all_qualified_folders

    def write_setlist(self, list_to_write):
        print('>>>> SETLIST: Writing the setlist to setlist.txt')
        sysfunc.mount_samples_rw()  # remount `/samples` as read-write (if using SD card)
        setlist = open(gv.SETLIST_FILE_PATH, "w")
        list_to_write = list(filter(None, list_to_write))  # remove empty strings / empty lines
        for song in list_to_write:
            setlist.write(song + '\n')
        setlist.close()
        sysfunc.mount_samples_ro()  # remount as read-only
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
            for song_folder_name in self.song_folders_list:

                if (song_name == song_folder_name):
                    # print song_name + ' was found'
                    break
                elif (song_name.replace('* ', '') == song_folder_name):
                    # print song_name + ' was found - previous lost'
                    songs_in_setlist[k] = song_name.replace('* ', '')
                    continue
                else:
                    if (i == len(self.song_folders_list) - 1):
                        print  '>>>> SETLIST: Folder for /%s/ was not found' % song_name
                        songs_in_setlist[k] = '* ' + song_name.replace('* ', '')
                        changes_in_dir = True
                        break

                i += 1
            k += 1

        if (changes_in_dir):
            self.write_setlist(songs_in_setlist)
        else:
            print('>>>> SETLIST: No missing folders detected')

    def find_and_add_new_folders(self):
        # Check for new song folders and add them to the end of the setlist

        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()
        songs_in_setlist = list(filter(None, songs_in_setlist))  # remove empty strings / empty lines
        changes_in_dir = False

        if (set(songs_in_setlist).intersection(self.song_folders_list) != len(self.song_folders_list) and len(songs_in_setlist) != 0):

            for song_folder_name in self.song_folders_list:
                i = 0
                # check if entry is a dir, and not a system dir and that dir is not empty
                if os.path.isdir(gv.SAMPLES_DIR + '/' + song_folder_name) \
                        and song_folder_name not in IGNORE_FOLDERS \
                        and os.listdir(gv.SAMPLES_DIR + '/' + song_folder_name) != []:
                    for song_name in songs_in_setlist:
                        if (song_folder_name == song_name):
                            break
                        elif (i == len(songs_in_setlist) - 1):
                            print '>>>> SETLIST: New setlist entry for /%s/' % song_folder_name
                            changes_in_dir = True
                            songs_in_setlist.append(song_folder_name)
                            break
                        i += 1
                else:
                    print '>>>> SETLIST: /%s/ is not a folder. Skipping.' % song_folder_name
        elif (len(songs_in_setlist) == 0):

            print '>>>> SETLIST: Is empty -> adding all foldings'

            for song_folder_name in self.song_folders_list:
                i = 0
                # check if entry is a dir, and not a system dir and that dir is not empty
                if os.path.isdir(gv.SAMPLES_DIR + '/' + song_folder_name) \
                        and song_folder_name not in IGNORE_FOLDERS \
                        and os.listdir(gv.SAMPLES_DIR + '/' + song_folder_name) != []:
                    print '>>>> SETLIST: Adding /%s/' % song_folder_name
                    songs_in_setlist.append(song_folder_name)
                    changes_in_dir = True

        if (changes_in_dir):
            self.write_setlist(songs_in_setlist)
        else:
            print('>>>> SETLIST: No new folders found -> do nothing')

    # ______________________________________________________________________________

    def remove_missing_setlist_songs(self):
        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()

        # Remove * marked songs (list comprehension)
        songs_in_setlist = [song for song in songs_in_setlist if '* ' not in song]

        self.write_setlist(songs_in_setlist)


if __name__ == "__main__":
    setlist = Setlist()
