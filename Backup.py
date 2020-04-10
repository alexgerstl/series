import os
import sys
import shutil
import msvcrt
from filecmp import dircmp
from termcolor import colored

target_dir = 'X:\\Serien'
#target_dir = 'C:\\Test'
source_dir = 'F:\\Data\\Serien'
source_root = [f.path for f in os.scandir(source_dir) if f.is_dir()]
os.system('color')


class ProgressBar(object):
    def __init__(self, message, width=20, progressSymbol='+', emptySymbol='-'):
        self.width = width

        if self.width < 0:
            self.width = 0

        self.message = message
        self.progressSymbol = progressSymbol
        self.emptySymbol = emptySymbol

    def update(self, progress):
        totalBlocks = self.width
        filledBlocks = int(round(progress / (100 / float(totalBlocks))))
        emptyBlocks = totalBlocks - filledBlocks

        progressBar = self.progressSymbol * filledBlocks + \
                      self.emptySymbol * emptyBlocks

        if not self.message:
            self.message = u''

        progressMessage = u'\r{0} {1}  {2}%'.format(self.message,
                                                    progressBar,
                                                    progress)

        sys.stdout.write(progressMessage)
        sys.stdout.flush()

    def calculateAndUpdate(self, done, total):
        progress = int(round((done / float(total)) * 100))
        self.update(progress)


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


def possible_backups():
    _list = []
    for s in source_root:
        _series, _season = get_series_season(s)
        target_dir_series_season = os.path.join(os.path.join(target_dir, _series), _season)
        if not os.path.exists(target_dir_series_season):
            _list.append(s)
        else:
            if len(get_diff(s, target_dir_series_season)) > 0:
                _list.append(s)

    return _list


def get_size(folder):
    _files = os.listdir(folder)
    return len(_files)


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
    p = ProgressBar('Copying files...')
    numCopied = 0
    for f in content:
        try:
            print(colored("Copying file %s" % f, "blue"))
            shutil.copy(os.path.join(source, f), os.path.join(target, f))
            numCopied += 1
            p.calculateAndUpdate(numCopied, len(content))
            print()
        except:
            print(colored("Error while copying file: %s" % f, "red"))


def action_move(source, target, content):
    p = ProgressBar('Moving files...')
    numCopied = 0
    for f in content:
        try:
            print(colored("Moving file %s" % f, "blue"))
            shutil.move(os.path.join(source, f), os.path.join(target, f))
            numCopied += 1
            p.calculateAndUpdate(numCopied, len(content))
            print()
            print(colored("\n" + "Delete folder - (Y)es or (N)o? ", "yellow", "on_blue"))
            action = msvcrt.getch()
            if ord(action.lower()) == ord("y"):
                shutil.rmtree(source)
        except:
            print(colored("Error while moving file: %s" % f, "red"))


if __name__ == "__main__":
    print(colored("Listing possible backups:", "white"))
    _p = possible_backups()
    for _l in _p:
        _series, _season = get_series_season(_l)
        _s = "Detected: {} - {}".format(_series, _season)
        print(colored("\t" + _s, "yellow"))
    print()

    for _l in _p:
        _series, _season = get_series_season(_l)
        print(colored(_series + " - " + _season + ": do Backup (B) or do Nothing (N)? ", "yellow", "on_red"))
        _action = msvcrt.getch()
        if ord(_action.lower()) == ord("b"):
            create_backup_tree(_series, _season, target_dir)
            target_dir_series_season = os.path.join(os.path.join(target_dir, _series), _season)
            diff = get_diff(_l, target_dir_series_season)
            print(colored("Diff in series: %s" % _series, "yellow"),
                  colored("%d file(s) local but not on NAS" % len(diff), "magenta"))
            action = request_input()
            if action == ord("c"):
                print(colored("Start copying files", "grey"))
                action_copy(_l, target_dir_series_season, diff)
            if action == ord("m"):
                print(colored("Start moving files", "grey"))
                action_move(_l, target_dir_series_season, diff)
            if action == ord("n"):
                continue
            print()
        if ord(_action.lower()) == ord("n"):
            continue
    print(colored("Done!!", "yellow"))
