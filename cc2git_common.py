
__author__="langiewi_m"
__date__ ="$Jun 25, 2010 10:21:13 AM$"

import os
import os.path
from time import time


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

def run_command(cmd, log=True):
    if log:
        print "    START COMMAND:", cmd
        starttime = time()
    os.system(cmd)
    if log:
        endtime = time()
        print "    END COMMAND: ", cmd, " (time: ", endtime - starttime, ")"

if __name__ == "__main__":
    raise Exception
