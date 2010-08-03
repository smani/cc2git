#! /usr/bin/python

__author__="langiewi_m"
__date__ ="$Jul 9, 2010 1:18:27 PM$"

from cc2git import stage1
from cc2git import stage2
from cc2git import main
from time import time
from common import time_str

if __name__ == "__main__":

    starttime = time()

    """
    stage2(
        "/home/langiewi_m/p2_latest/develop/source/siemens/applications/cma",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma_git",
        use_global_db_value=False,
        clearcasepretend=True
    )
    """

    VIEW = "MAREK_PORTA"
    """
    include_porta_vobs = "porta(_(kernel(_2_4_31)?)|(tools))?"
    include_vobs = "(common_software)|(components)|(danube_tc)|(" + include_porta_vobs + ")"
    exclude = "(?!/view/" + VIEW + "/vobs((/(" + include_vobs + "))?)).+"
    exclude = "(.*/.*/.*/.*/.*/.*/.*/.*/.*)|(" + exclude + ")"
    """


    full_vobs_dir = "/view/" + VIEW + "/vobs"
    porta_alternative = "$|(_tools)|(_kernel($|(_2_4_31)))"
    alternative = "$|(/components)|(/common_software)|(/danube_tc)|(/porta(" + porta_alternative + "))"
    exclude = "^((?!"+ full_vobs_dir +")|(" + full_vobs_dir + "(?!" + alternative + ")))"                
    exclude = "((.*/){7})|(lost\\+found)|(" + exclude + ")"




    cc_topdir = "/view/" + VIEW
    meta_topdir = "/home/langiewi_m/cc2git_tests/test_04_all_meta"
    git_topdir = "/home/langiewi_m/cc2git_tests/test_04_all_git"
    main(cc_topdir, meta_topdir, git_topdir, exclude)


    endtime = time()

    print "calkowity czas dzialania:", time_str(endtime - starttime)
