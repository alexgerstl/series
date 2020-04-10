import os
import re
import subprocess
from os.path import expanduser
from shutil import move

INCOMING_DIR = "F:\Incoming"
SERIES_DIR = "F:\Data\Serien"
CONVERTED_DIR = "F:\Wondershare Video Converter Ultimate\Converted"
DESKTOP_DIR = expanduser("~") + "\Desktop"


def check_for_softcoded_subtitles(_file):
    counter = 0
    cmd = subprocess.Popen("mkvmerge -i " + _file, shell=True, stdout=subprocess.PIPE)
    try:
        for line in cmd.stdout:
            if "subtitle" in line.decode('utf_8'):
                counter = counter + 1
        return counter
    except Exception as r:
        print(r)


def remove_softcoded_subtitle(_source, _destination):
    try:
        subprocess.call("mkvmerge -o " + _destination + " --no-subtitles " + _source)
    except Exception as e:
        print(e)


def read_folder_content(_path, _file_ending):
    _list = []
    for f in os.listdir(_path):
        if f.endswith(_file_ending):
            _list.append(f)
    return _list


def normalize_series_name(_series_name):
    _series_name = re.sub(r'[^A-Za-z]', '', _series_name)
    return _series_name.lower()


def get_video_info(_file):
    m = re.search('S[0-9]{2}E[0-9]{2}', _file.upper())
    found = m.group(0)
    index = _file.upper().find(found)
    series_name = _file[:index - 1]
    m = re.search('S[0-9]{2}', found)
    season = m.group(0)
    m = re.search('E[0-9]{2}', found)
    episode = m.group(0)
    return series_name, season, episode


def get_subtitle_info(_file):
    m = re.search('[0-9]{2}[A-Z][0-9]{2}', _file.upper())
    found = m.group(0)
    index = _file.upper().find(found)
    series_name = _file[:index - 1]
    m = re.search('[0-9]{2}', found)
    season = m.group(0)
    m = re.search('[A-Z][0-9]{2}', found)
    episode = m.group(0)
    return series_name, season, episode


def compare_video_and_sub(_video, _sub):
    _n, _s, _e = get_video_info(_video)
    _n1, _s1, _e1 = get_subtitle_info(_sub)
    return normalize_series_name(_n) == normalize_series_name(_n1) and _s[1:] == _s1 and _e[1:] == _e1[1:]


def search_for_existing_folder(_episode):
    series_name, season, episode = get_video_info(_episode)
    destination_dir = os.path.join(SERIES_DIR, series_name + "." + season)
    if not os.path.exists(destination_dir):
        print("\t" + "No folder for " + series_name + " found!")
        print("\t" + "Creating folder...")
        try:
            os.makedirs(destination_dir)
            print("\t" + "Folder for " + series_name + " Season " + season + " created!")
        except OSError as _e:
            print("\t" + "Could not create folder for " + series_name)
            print("\t" + "Reason: " + str(_e))
    print("-----------------------------------")
    return destination_dir


def list_files(_list, folder):
    print("Listing files in " + folder + " - " + str(len(_list)) + " files found")
    if len(_list) > 0:
        for e in _list:
            print(e)
    print("-----------------------------------")
    print()


def check_and_move_video_file(_file):
    destination = search_for_existing_folder(_file)
    print("Checking and moving video file")
    print("-----------------------------------")
    try:
        if check_for_softcoded_subtitles(INCOMING_DIR + "/" + _file) > 0:
            print("\t" + "Embedded subtitles found")
            print("\t" + "Removing subtitles...")
            remove_softcoded_subtitle(INCOMING_DIR + "/" + _file, destination + "/" + _file)
            os.remove(INCOMING_DIR + "/" + _file)
        else:
            move(INCOMING_DIR + "/" + _file, destination)
        print("\t" + "File " + _file + " moved")
    except Exception as e:
        print("\t" + "Could not move file: " + _file)
        print(e)


if __name__ == "__main__":
    try:
        files_in_converted_dir = read_folder_content(CONVERTED_DIR, ".mkv")
        subtitle_files = read_folder_content(DESKTOP_DIR, ".srt")
        if len(files_in_converted_dir) > 0:
            list_files(files_in_converted_dir, CONVERTED_DIR)
            print("moving them to Incoming")
            for _c in files_in_converted_dir:
                try:
                    move(CONVERTED_DIR + "\\" + _c, INCOMING_DIR + "\\" + _c)
                    print("\t" + "File moved: " + _c)
                except Exception as e:
                    print("\t" + "Could not move file: " + _c)
            print()
        incoming_files = read_folder_content(INCOMING_DIR, ".mkv")
        list_files(incoming_files, INCOMING_DIR)
        list_files(subtitle_files, DESKTOP_DIR)
        if len(incoming_files) > 0:
            for _video in incoming_files:
                check_and_move_video_file(_video)
                print()
                print("-----------------------------------")
                print("Searching for subtitle for: " + _video)
                print("-----------------------------------")
                print()
                if len(subtitle_files) > 0:
                    for _sub in subtitle_files:
                        if compare_video_and_sub(_video, _sub):
                            print("\t" + "Proper subtitle found: " + _sub)
                            os.rename(DESKTOP_DIR + "\\" + _sub, DESKTOP_DIR + "\\" + _video + ".srt")
                            try:
                                _n, _s, _e = get_video_info(_video)
                                move(DESKTOP_DIR + "\\" + _video + ".srt", SERIES_DIR + "\\" + _n + "." + _s)
                                print("\t" + "Subtitle moved")
                                print()
                                subtitle_files.remove(_sub)
                            except Exception as e:
                                print(e)
                                print("\t" + "Could not move file: " + DESKTOP_DIR + "\\" + _sub + ".srt")
    except Exception as e:
        print("\t" + "something happened: " + str(e))
