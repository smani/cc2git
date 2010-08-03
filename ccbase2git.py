#! /usr/bin/python

__author__="langiewi_m"
__date__ ="$Jun 25, 2010 10:17:40 AM$"

import os
import os.path
from time import time
from common import run_command
from common import noemptydirs
from porta_baselines import PORTA_BASELINES

VCT_CMD = "/build/vct"

def ccbase2git(baselines, view_dir, git_dir, guarddirs):
    """
        guarddirs - list of dirs where to guard empty subdirs
        (this will insert empty .gitignore file in any empty dir in guarddirs list)
    """
    #TODO: obsluga bledow.. :(
    for baseline in baselines:
        starttime = time()
        print "  START exporting baseline:", baseline
        run_command("cd " + view_dir + " ; sudo " + VCT_CMD + " rmprivate")
        run_command("cd " + view_dir + " ; " + VCT_CMD + " rebase " + baseline)
        for dir in guarddirs:
            noemptydirs(dir, ".gitignore")
        run_command("cd " + view_dir + " ; git --git-dir=" + git_dir + " --work-tree=" + view_dir + " add -v -A .")
        run_command("cd " + view_dir + " ; git --git-dir=" + git_dir + " --work-tree=" + view_dir + " commit -v -m \"ccbase2git_v2 " + baseline + "\"")
        endtime = time()
        print "  END exporting baseline", baseline, "(time:", endtime - starttime, ")"

if __name__ == "__main__":
    print "START script"
    starttime = time()
    """
    BASELINES = [
        "PORTA_MAINT_BAS_052_015",
        "PORTA_MAINT_BAS_052_016",
        "PORTA_MAINT_BAS_052_017",
        "PORTA_MAINT_BAS_052_018"
    ]
    """
    BASELINES = PORTA_BASELINES

    VIEW_DIR = "/view/PORTA_TO_GIT"
    GIT_DIR = "/home/langiewi_m/projects/porta_to_git.git"
    VOBS_DIR = os.path.join(VIEW_DIR, "vobs")
    VOBS = ["common_software", "components", "danube_tc", "porta", "porta_kernel", "porta_kernel_2_4_31", "porta_tools"]
    guarddirs = []
    for vob in VOBS:
        guarddirs.append(os.path.join(VOBS_DIR, vob))
    ccbase2git(BASELINES, VIEW_DIR, GIT_DIR, guarddirs)
    endtime = time()
    print "Total working time:", endtime - starttime
