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
    ("danube_tc", "danube_tc"), #87MB
    ("components", "components"), #103MB
    ("common_software", "common_software"), #130MB
    ("porta_kernel_2_4_31", "porta_kernel_2_4_31"), #194MB
    ("porta_kernel", "porta_kernel"), #206MB
    ("porta_tools", "porta_tools"), #449MB
    ("porta", "porta"), #882MB
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
