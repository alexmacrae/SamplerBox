import globalvars as gv

class Setlist:
    
    def __init__(self):
        pass

    def write_setlist(self, list_to_write):
        print('-= WRITING NEW SETLIST =-')
        setlist = open(gv.SETLIST_FILE_PATH, "w")
        list_to_write = list(filter(None, list_to_write))  # remove empty strings / empty lines
        for song in list_to_write:
            setlist.write(song + '\n')
        setlist.close()
        self.update_live_setlist()

    def update_live_setlist(self):
        gv.SETLIST_LIST = open(gv.SETLIST_FILE_PATH).read().splitlines()
    
    def find_missing_folders(self):
        # Check to see if the song name in the setlist matches the name of a folder.
        # If it doesn't, mark it by prepending an *asterix and rewrite the setlist file.
    
        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()
        songs_in_setlist = list(filter(None, songs_in_setlist))  # remove empty strings / empty lines
        changes = False
        k = 0
        for song_name in songs_in_setlist:
            i = 0
            for song_folder_name in gv.SONG_FOLDERS_LIST:
    
                if (song_name == song_folder_name):
                    # print(song_name + ' was found')
                    break
                elif (song_name.replace('* ', '') == song_folder_name):
                    # print(song_name + ' was found - previous lost')
                    songs_in_setlist[k] = song_name.replace('* ', '')
                    # break
                else:
                    if (i == len(gv.SONG_FOLDERS_LIST) - 1):
                        print(song_name + ' WAS NOT FOUND. ')
                        songs_in_setlist[k] = '* ' + song_name.replace('* ', '')
                        changes = True
                        break
    
                i += 1
            k += 1
    
        if (changes):
            self.write_setlist(songs_in_setlist)
        else:
            print('-= No missing folders detected =-\n')
    
    
    def find_and_add_new_folders(self):
        # Check for new song folders and add them to the end of the setlist
    
        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()
        songs_in_setlist = list(filter(None, songs_in_setlist))  # remove empty strings / empty lines
        changes = False
    
        if (set(songs_in_setlist).intersection(gv.SONG_FOLDERS_LIST) != len(gv.SONG_FOLDERS_LIST) and len(
                songs_in_setlist) != 0):
    
            for song_folder_name in gv.SONG_FOLDERS_LIST:
                i = 0
                for song_name in songs_in_setlist:
                    if (song_folder_name == song_name):
                        break
                    elif (i == len(songs_in_setlist) - 1):
                        print (song_folder_name + ' - NEW FOLDER')
                        changes = True
                        songs_in_setlist.append(song_folder_name)
                        break
    
                    i += 1
        elif (len(songs_in_setlist) == 0):
            songs_in_setlist = gv.SONG_FOLDERS_LIST
            changes = True
            print ('Setlist empty - adding all foldings')
    
        # print(songs_in_setlist)
        if (changes):
            self.write_setlist(songs_in_setlist)
        else:
            print('-= No new folders found =-\n')
    
    # ______________________________________________________________________________
    
    
    def remove_missing_setlist_songs(self):
        songs_in_setlist = open(gv.SETLIST_FILE_PATH).read().splitlines()
        i = 0
        for song in songs_in_setlist:
            if ('* ' in song):
                del songs_in_setlist[i]
                self.write_setlist(songs_in_setlist)
            i += 1


