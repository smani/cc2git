#! /usr/bin/python

__author__="langiewi_m"
__date__ ="$Jul 9, 2010 1:18:27 PM$"

from cc2git import stage1
from cc2git import stage2
from cc2git import main
from time import time
from cc2git_common import time_str
from cc2git_common import run_command
from pprint import pprint

VIEW = "MAREK_PORTA"
VOBS_DIR = "/view/" + VIEW + "/vobs" #TODO: czy napewno
#VOBS_DIR = "/home/marek.langiewicz/tmp/walktest/vobs" #TODO: usunac
#VOBS_DIR = "/home/marek.langiewicz/git-repos/porta/vobs" #TODO: usunac
VCT = "/build/vct" #TODO: upewnic sie ze u slawka to tez taka sciezka
CREATE_VIEW_CMD = "sudo " + VCT + " mkview --prj Porta_BAS_052_Maint --cnf STANDARD " + VIEW
HOME_DIR = "/home/kesicki_sl"
RESULTS_DIR = HOME_DIR + "/cc2git_results"
TESTS = [ #TODO; utrzymujemy to mniejwiecej wedlug rozmiaru od najmniejszego
    ("31", "common_software/sw/develop/source/siemens/interfaces"),
    ("32", "common_software/sw/develop/makefiles"),
    ("33", "porta/sw/develop/source/siemens/applications/cma/digitmap"),
    ("34", "porta/sw/develop/source/siemens/applications/cma/doc"),
    ("35", "porta/sw/develop/makefiles"),
    ("36", "porta/sw/develop/profiles"),
    ("37", "porta/sw/develop/source/siemens/applications/cma/callcontrol"),
    ("38", "porta/sw/develop/source/siemens/applications/cma/b2bua"),
    ("39", "porta/sw/develop/source/siemens/applications/cma/endpoint"),
    ("40", "porta/sw/develop/source/siemens/applications/cma/resourcemanagement"),
    ("41", "common_software/sw/develop/source/siemens/applications"),
    ("42", "porta/sw/develop/source/siemens/applications/cma"),
    ("43", "porta/sw/develop/source/siemens/applications/scm_app"),
    ("44", "porta/sw/webcommon"),
    ("45", "porta/sw/develop/source/siemens/applications/html"),
    ("46", "common_software/sw/develop/source/siemens/libraries"),
    ("47", "porta/sw/develop/source/siemens/applications"),
    ("48", "porta/sw/develop/source/siemens/libraries"),
    ("49", "common_software/sw/develop/source/opensource/components"),
    ("50", "common_software/sw/develop/source/allegro"),
]


if __name__ == "__main__":

    starttime = time()

    #run_command(CREATE_VIEW_CMD) #TODO: odpalic ale tylko raz

    for (test_dirrest, cc_dirrest) in TESTS:
        test_topdir = RESULTS_DIR + "/" + test_dirrest
        cc_topdir = VOBS_DIR + "/" + cc_dirrest
        meta_topdir = test_topdir + "_meta"
        git_topdir = test_topdir + "_git"

        startmaintime = time()

        print "!!! ODPALAMY MAIN !!!"
        print "main(" + cc_topdir + ", " + meta_topdir + ", " + git_topdir + ")"
        main(cc_topdir, meta_topdir, git_topdir)
        #main(cc_topdir, meta_topdir, git_topdir, pretend_stage1=True, pretend_stage2=True)
        #run_command("ls " + cc_topdir)
        print "!!! ZAKONCZONE MAIN !!!"
        
        endmaintime = time()
        print "czas dzialania main:", time_str(endmaintime - startmaintime)

    endtime = time()

    print "!!!!!!!!!!!! ZAKONCZONE WSZYSTKO !!!!!!!!!!"
    print "calkowity czas dzialania:", time_str(endtime - starttime)
