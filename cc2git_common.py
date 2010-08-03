import re

__author__="langiewi_m"
__date__ ="$Jun 25, 2010 10:21:13 AM$"

import os
import os.path
from time import time
from time import sleep
from commands import getstatusoutput


#TODO: ta funkcja ma byc prywatna
def ned_walk(filename, dir, elements):
    if dir.find("lost+found") != -1:
        return
    if len(elements) == 0:
        fullfilename = os.path.join(dir, filename)
        print "running: sudo touch \"" + fullfilename + "\""
        run_command("sudo touch \"" + fullfilename + "\"", log=False)

def noemptydirs(dir, filename):
    print "START noemptydirs(" + dir + ", " + filename + ")"
    starttime = time()
    os.path.walk(dir, ned_walk, filename)
    endtime = time()
    print "END noemptydirs(" + dir + ", " + filename + ") (time: ", endtime - starttime, ")"

class Log:
    NONE, LITTLE, MUCH = range(3)

def run_command(cmd, log=Log.MUCH, pretend=False):
    if log == Log.MUCH:
        print "    START COMMAND:",
        starttime = time()
    if log != Log.NONE:
        print cmd
    if not pretend:
        os.system(cmd)
    if log == Log.MUCH:
        endtime = time()
        print "    END COMMAND: ", cmd, " (time: ", endtime - starttime, ")"

def try_command_out(command, trials=20, pause=5):
    status = 0
    output = ""
    for i in range(trials):
        status, output = getstatusoutput(command)
        if status == 0:
            break
        sleep(pause)
        print "Warning: non 0 status when executing command:", command
        print "status:" , status
        print "output:"
        print output
        print
        print "trying again..."
    if status != 0:
        raise Exception("Error trying command: " + command + "\nstatus: " + str(status) + "\noutput:\n" + output)
    return output

def make_path(path):
    """
    make whole path if not exists
    """
    try:
        os.makedirs(path)
    except os.error: #TODO: lapac tylko wyjatek typu File exists
        pass

def time_str(sec):
    h = int(sec / 3600)
    sec -= h * 3600
    m = int(sec / 60)
    sec -= m * 60
    s = int(sec)
    sec -= s
    s100 = int(sec*100)
    result = str(s) + " seconds " + str(s100) + " miliseconds "
    if m > 0:
        result = str(m) + " minutes " + result
    if h > 0:
        result = str(h) + " hours " + result
    return result

def walk_exclude_walk(data, dir, fnames):
    """
    TODO: ta funkcja ma byc prywatna
    """
    walk, data, exclude = data
    for f in fnames[:]:
        ff = os.path.join(dir,f)
        if re.search(exclude, ff):
            fnames.remove(f)
    walk(data, dir, fnames)

def walk_exclude(topdir, walk, data, exclude):
    os.path.walk(topdir, walk_exclude_walk, (walk, data, exclude))

if __name__ == "__main__":
    raise Exception
