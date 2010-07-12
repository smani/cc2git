#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="langiewi_m"
__date__ ="$Jul 1, 2010 12:17:34 PM$"

import cc2git_common
from pprint import pprint

def test_walk(arg, dir, files):
    print "test_walk: arg:", arg, "dir:", dir
    print "files:"
    for file in files:
        print file
    print

if __name__ == "__main__":


    #Test shell stuff:
    """
    os.system("A=bla ; B=blee ; echo test1: A=$A B=$B ; export")
    os.system("export")
    os.system("echo test2: A=$A B=$B")
    os.system("export")
    os.system("cd ~/tmp ; pwd")
    os.system("pwd")
    """



    """
    #test popen2
    import popen2
    import time
    (fout, fin, ferr) = popen2.popen3("cleartool")
    fin.write("help\n")
    fin.write("exit\n")
    fin.flush()
    l = fout.readline()
    while len(l) > 0:
        print "linia:", l
        l = fout.readline()
    print "koniec"
    fout.close()
    fin.close()
    ferr.close()
    #fout.write("help rebase\n\n")
    #fout.flush()
    #sleep(5)
    #l = fin.readline(),
    #while l != "":
    #    print l
    #    l = fin.readline(),
    #fout.close()
    #fin.close()
    """

    """
    #test commands
    import commands
    (sts, out) = commands.getstatusoutput("cleartool describe burek")
    print "status:", sts
    print "output:"
    print out
    """

    """
    lines = cc2git_common.try_command_out("ls").splitlines()
    #print cc2git_common.try_command_out("ls dupasatana")
    
    for i in range(2,len(lines)):
        if lines[i].strip() == "loggger.sh":
            break
    print "\n".join(lines[2:i])
    print i
    pprint(lines)
    """

    """
    l = [1, 1.2, 4.5, 20, 61, 119.99, 456785.53728953, 3700, 3600]
    for x in l:
        print x, cc2git_common.time_str(x)
    """
    VIEW = "PORTA_MAREK"
    include_porta_vobs = "porta(_(kernel(_2_4_31)?)|(tools))?"
    include_vobs = "(common_software)|(components)|(danube_tc)|(" + include_porta_vobs + ")"
    exclude = "/view/" + VIEW + "/vobs/(?!(" + include_vobs + ")).+"
    exclude = "(.*/.*/.*/.*/.*/.*/.*/.*/.*/.*)|(" + exclude + ")"
    cc2git_common.walk_exclude("/home/langiewi_m/tmp/walktest/", test_walk, "dupa", exclude)

