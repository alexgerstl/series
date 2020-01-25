import os
import re
import subprocess
from os.path import expanduser
from shutil import move

incoming_dir = "F:\Incoming"
series_dir = "F:\Data\Serien"
converted_dir = "F:\Wondershare Video Converter Ultimate\Converted"
desktop_dir = expanduser("~") + "\Desktop"


def check_for_subtitles(_file):
    counter = 0
    cmd = subprocess.Popen("mkvmerge -i " + _file, shell=True, stdout=subprocess.PIPE)
    try:
        for line in cmd.stdout:
            if "subtitle" in line.decode('utf_8'):
                counter = counter + 1
        return counter
    except Exception as r:
        print(r)


def remove_subtitle(_source, _destination):
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
    m = re.search('S[0-9]{2}E[0-9]{2}', _episode.upper())
    found = m.group(0)
    index = _episode.upper().find(found)
    series_name = _episode[:index - 1]
    m = re.search('S[0-9]{2}', found)
    season = m.group(0)
    m = re.search('E[0-9]{2}', found)
    episode = m.group(0)

    if not os.path.exists(series_dir + "/" + series_name + "." + season):
        print("\t" + "No folder for " + series_name + " found!")
        print("\t" + "Creating folder...")
        try:
            os.makedirs(series_dir + "/" + series_name + "." + season)
            print("\t" + "Folder for " + series_name + " Season " + season + " created!")
        except OSError as _e:
            print("\t" + "Could not create folder for " + series_name)
            print("\t" + "Reason: " + str(_e))
    print("-----------------------------------")
    return series_name, season, episode


def list_files(_list):
    print("Listing files - " + str(len(_list)) + " files found")
    if len(_list) > 0:
        for e in _list:
            print(e)
    print("-----------------------------------")
    print()


def check_and_move_video_file(_file):
    series_name, season, episode = search_for_existing_folder(_file)
    destination = series_dir + "\\" + series_name + "." + season
    print("Checking and moving video file")
    print("-----------------------------------")
    try:
        if check_for_subtitles(incoming_dir + "/" + _file) > 0:
            print("\t" + "Embedded subtitles found")
            print("\t" + "Removing subtitles...")
            remove_subtitle(incoming_dir + "/" + _file, destination + "/" + _file)
            os.remove(incoming_dir + "/" + _file)
        else:
            move(incoming_dir + "/" + _file, destination)
        print("\t" + "File " + _file + " moved")
    except Exception as e:
        print("\t" + "Could not move file: " + _file)
        print(e)


converted_files = read_folder_content(converted_dir, ".mkv")


try:
    if len(converted_files) > 0:
        print("Converted files - " + str(len(converted_files)) + " files found")
        print("-----------------------------------")
        print("moving them to Incoming")
        for _c in converted_files:
            try:
                move(converted_dir + "\\" + _c, incoming_dir + "\\" + _c)
                print("\t" + "File moved: " + _c)
            except Exception as e:
                print("\t" + "Could not move file: " + _c)
        print()
    incoming_files = read_folder_content(incoming_dir, ".mkv")
    subtitle_files = read_folder_content(desktop_dir, ".srt")
    list_files(incoming_files)
    list_files(subtitle_files)
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
                        os.rename(desktop_dir + "\\" + _sub, desktop_dir + "\\" + _video + ".srt")
                        try:
                            _n, _s, _e = get_video_info(_video)
                            move(desktop_dir + "\\" + _video + ".srt", series_dir + "\\" + _n + "." + _s)
                            print("\t" + "Subtitle moved")
                            print()
                            subtitle_files.remove(_sub)
                        except Exception as e:
                            print(e)
                            print("\t" + "Could not move file: " + desktop_dir + "\\" + _sub + ".srt")
except Exception as e:
    print("\t" + "something happened: " + str(e))

