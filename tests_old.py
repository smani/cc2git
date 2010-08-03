#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="langiewi_m"
__date__ ="$Jul 1, 2010 12:17:34 PM$"

import common
from pprint import pprint

def test_walk(arg, dir, files):
    print "test_walk: arg:", arg, "dir:", dir
    print "files:"
    for file in files:
        print file
    print

if __name__ == "__main__":







    VIEW = "MAREK_PORTA"
    """
    include_porta_vobs = "porta(_(kernel(_2_4_31)?)|(tools))?"
    include_vobs = "(common_software)|(components)|(danube_tc)|(" + include_porta_vobs + ")"
    exclude = "/view/" + VIEW + "/vobs/(?!(" + include_vobs + ")).+"
    print exclude
    exclude = "(.*/.*/.*/.*/.*/.*/.*/.*/.*/.*)|(" + exclude + ")"
    #common.walk_exclude("/home/langiewi_m/tmp/walktest/", test_walk, "dupa", exclude)
    """

    """
        view/gjsdfkljsd
        view/MAREK_PORTA/vla
    x   view/MAREK_PORTA/vobs
    x   view/MAREK_PORTA/vobs/components
    x   view/MAREK_PORTA/vobs/common_software
    x   view/MAREK_PORTA/vobs/danube_tc
    x   view/MAREK_PORTA/vobs/porta
    x   view/MAREK_PORTA/vobs/porta_kernel
    x   view/MAREK_PORTA/vobs/porta_kernel_2_4_31
    x   view/MAREK_PORTA/vobs/porta_tools
        view/MAREK_PORTA/vobs/dupa
    """

    #/view/MAREK_PORTA/vobs/(?!((common_software)|(components)|(danube_tc)|(porta(_(kernel(_2_4_31)?)|(tools))?))).+


    """
    (?!
    view/MAREK_PORTA/vobs
    (
        /
        (
            (components)|
            (common_software)|
            (danube_tc)|
            (
                porta(
                    (_kernel(_2_4_31)?)|
                    (_tools)
                )?	
            )
        )
    )?
    )
    """


    """
    (
        (?!
            /view/MAREK_PORTA/vobs
        )
    |
        /view/MAREK_PORTA/vobs
        (?!
            (
                $
            |
                (/components)
            |
                (/common_software)
            |
                (/danube_tc)
            |
                (
                    /porta
                    (
                        $
                    |
                        (_tools)
                    |
                        (_kernel)
                        (
                            $
                        |
                            (_2_4_31)
                        )
                    )
                )
            )
        )
    )

    """
    #full_vobs_dir = "/view/" + VIEW + "/vobs"
    full_vobs_dir = "/home/langiewi_m/tmp/walktest/vobs"
    porta_alternative = "$|(_tools)|(_kernel($|(_2_4_31)))"
    alternative = "$|(/components)|(/common_software)|(/danube_tc)|(/porta(" + porta_alternative + "))"
    exclude = "^((?!"+ full_vobs_dir +")|(" + full_vobs_dir + "(?!" + alternative + ")))"                
    exclude = "((.*/){8})|(lost\\+found)|(" + exclude + ")"
    common.walk_exclude("/home/langiewi_m/tmp/walktest/", test_walk, "dupa", exclude)
