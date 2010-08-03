import sys
import os
import popen2
import common
import pprint

def tshell():
    os.system("A=bla ; B=blee ; echo test1: A=$A B=$B ; export")
    os.system("export")
    os.system("echo test2: A=$A B=$B")
    os.system("export")
    os.system("cd ~/tmp ; pwd")
    os.system("pwd")

def tpopen2():
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

def tcommands():
    import commands
    (sts, out) = commands.getstatusoutput("cleartool describe burek")
    print "status:", sts
    print "output:"
    print out

def tassert_raises():
    common.run_command("dupa")

def tfixme_try_command_out():
        
    lines = common.try_command_out("ls", trials=3, pause=1).splitlines()

    for i in range(2,len(lines)):
        if lines[i].strip() == "loggger.sh":
            break
    print "\n".join(lines[2:i])
    print i
    pprint(lines)
    
    common.try_command_out("ls dupasatana", trials=3, pause=1)

def ttime_str():
    l = [1, 1.2, 4.5, 20, 61, 119.99, 456785.53728953, 3700, 3600]
    for x in l:
        print x, common.time_str(x)
       
if __name__ == "__main__":
    tshell()
    tpopen2()
    tcommands()
    tassert_raises()
    tfixme_try_command_out()
    ttime_str()

    
