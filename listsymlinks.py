#! /usr/bin/python

__author__="langiewi_m"
__date__ ="$Jun 25, 2010 10:25:58 AM$"

import os
import os.path
from pprint import pprint
from time import time

def lsld_walk((ldonieistniejacych, ldolinkow, ldokatalogow, ldoplikow), dir,files):
    print "lsld_walk", dir
    for f in files:
        ff = os.path.abspath(os.path.join(dir, f))
        if os.path.islink(ff):
            rl = os.path.abspath(os.path.join(os.path.dirname(ff), os.readlink(ff)))
            if not os.path.exists(rl):
                ldonieistniejacych.append((ff, rl))
            elif os.path.islink(rl):
                ldolinkow.append((ff, rl))
            elif os.path.isdir(rl):
                ldokatalogow.append((ff, rl))
            elif os.path.isfile(rl):
                ldoplikow.append((ff, rl))
            else:
                print ff, rl
                raise Exception

def usunniewazne(listalinkow):
    wynik = []
    for (src, dst) in listalinkow:
        if src.find("lost+found") != -1:
            continue
        if src.find("vobs/porta") != -1 and dst.find("vobs/porta") != -1:
            continue
        wynik.append((src,dst))
    return wynik

def listsymlinks(top):
    ldonieistniejacych = []
    ldolinkow = []
    ldokatalogow = []
    ldoplikow = []
    os.path.walk(top, lsld_walk, (ldonieistniejacych, ldolinkow, ldokatalogow, ldoplikow))
    ldonieistniejacych = usunniewazne(ldonieistniejacych)
    ldolinkow = usunniewazne(ldolinkow)
    ldokatalogow = usunniewazne(ldokatalogow)
    ldoplikow = usunniewazne(ldoplikow)
    print "Linki do nieistniejacych miejsc:"
    pprint(ldonieistniejacych)
    print "Linki do linkow:"
    pprint(ldolinkow)
    print "Linki do katalogow:"
    pprint(ldokatalogow)
    print "Linki do plikow:"
    pprint(ldoplikow)


if __name__ == "__main__":
    starttime = time()
    listsymlinks("/view/LANGIEWI_M_PORTA_BAS_052_MAINT_PREINT/vobs/porta")
    endtime = time()
    print "calkowity czas dzialania:", endtime - starttime
