import os
import shutil
import msvcrt
from filecmp import dircmp
from termcolor import colored

target_dir = 'X:\\Serien'
#target_dir = 'C:\\Test'
source_dir = 'F:\\Data\\Serien'
source_root = [f.path for f in os.scandir(source_dir) if f.is_dir()]
os.system('color')


def get_series_season(source):
    _folder = os.path.basename(os.path.normpath(source))
    _series = _folder[:_folder.rfind('.')].lower()
    _season = _folder[_folder.rfind('.') + 1:]
    return _series, _season


def create_backup_tree(_series, _season, target):
    if not os.path.exists(os.path.join(target, _series)):
        try:
            os.mkdir(os.path.join(target, _series))
        except OSError:
            print(colored("Could not create folder for series %s" % _series, "red"))
        else:
            print(colored("Folder for series %s created" % _series, "yellow"))

    if not os.path.exists(os.path.join(os.path.join(target, _series), _season)):
        try:
            os.mkdir(os.path.join(os.path.join(target, _series), _season))
        except OSError:
            print(colored("Could not create folder for season %s of series %s" % (_season, _series), "red"))
        else:
            print(colored("Folder for season %s of series %s created" % (_season, _series), "yellow"))
    return os.path.join(os.path.join(target_dir, _series), _season)


def get_size(folder):
    _size = 0
    _files = os.listdir(folder)
    for f in _files:
        _size += os.path.getsize(os.path.join(folder, f))
    return _size


def is_bigger(source, target):
    return get_size(source) > get_size(target)


def get_diff(source, target):
    dcmp = dircmp(source, target)
    return dcmp.left_only


def request_input():
    while True:
        print(colored("Move (M), Copy (C) or do Nothing (N)? ", "yellow", "on_blue"))
        _action = msvcrt.getch()
        if ord(_action.lower()) not in (ord('m'), ord('c'), ord('n')):
            print("Please select correct action!")
        else:
            break
    return ord(_action)


def action_copy(source, target, content):
    for f in content:
        try:
            print(colored("Copying file %s" % f, "blue"))
            shutil.copy(os.path.join(source, f), os.path.join(target, f))
        except:
            print(colored("Error while copying file: %s" % f, "red"))


def action_move(source, target, content):
    for f in content:
        try:
            print(colored("Moving file %s" % f, "blue"))
            shutil.move(os.path.join(source, f), os.path.join(target, f))
        except:
            print(colored("Error while moving file: %s" % f, "red"))


if __name__ == "__main__":
    for s in source_root:
        _series, _season = get_series_season(s)
        _s = "Detected {} - {}".format(_series, _season)
        print(_s.center(40, "-"))
        print(colored("Backup (B) or do Nothing (N)? ", "yellow", "on_blue"))
        action = msvcrt.getch()
        if ord(action.lower()) == ord("b"):
            create_backup_tree(_series, _season, target_dir)
            target_dir_series = os.path.join(target_dir, _series)
            target_dir_series_season = os.path.join(target_dir_series, _season)
            diff = get_diff(s, target_dir_series_season)
            if len(diff) > 0:
                diff = get_diff(s, target_dir_series_season)
                print(colored("Diff in series: %s" % _series, "yellow"), colored("%d file(s) local but not on NAS" % len(diff), "magenta"))
                print()
                action = request_input()
                if action == ord("c"):
                    print(colored("Start copying files", "grey"))
                    action_copy(s, target_dir_series_season, diff)
                if action == ord("m"):
                    print(colored("Start moving files", "grey"))
                    action_move(s, target_dir_series_season, diff)
                if action == ord("n"):
                    continue
            else:
                print(colored("No diff between local and NAS", "green"))
        if action == "n":
            continue
