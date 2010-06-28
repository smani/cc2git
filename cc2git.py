#!/usr/bin/env python

"""Clearcase to Git Exporter

Exports the Clearcase history to git repo.
Usage: cc2git input_dir output_dir


"""
#TODO: sprawdzic czy moge przyspieszyc jakims recznym skompilowaniem tego skryptu
#TODO: obsluga linkow (do plikow, do katalogow w tym samym vobie, do katalogow w innym vobie..)
"""
    o linkach: prosta wersja: linki (podobnie jak katalogi) traktujemy jako czesc szkieletu repozytorium gitowego,
    czyli tworzymy wszystkie na poczatku (przed pierwszym commitem gitowym) nawet linki do nieistniejacych jeszcze plikow,
    bo potem z czasem odpowiednie pliki beda sie pojawiac..

    jescze sprawa linkow do katalogow/plikow wychodzacych poza vob porty (a raczej poza korzen drzewa dla ktorego odpalilismy skrypt):
        - albo traktujemy je tak jak inne linki, ale wtedy musimy osobno puszczac skrypt dla brakujacych vobow i jakos to potem
            poustawiac zeby linki siegaly tam gdzie trzeba - trudne i problemy z wersjonowaniem (bo nie mamy juz tylko jednego lancuszka)
        - albo traktujemy je jak obiekty na ktore wskazuja - lepsza prostsza opcja, ale TODO: posprawdzac czy nie bedzie duplikatow!
"""
#TODO: posprawdzac czy linki nie spowoduja duplikacji plikow w jakis sposob (jesli np linki do innego voba pozamieniam na zwykle katalogi)
#TODO: pomysl na oszczedzenie pamieci: tworzyc jakas magiczna liczbe dla kazdej kulki
# taka zeby potem sortowanie bylo tylko po tej liczbie i bylo takie jak chcemy..
#TODO: uzyc popen2 do zarzadzania cleartoolem
#TODO: commit --date i --author (olewamy GIT_COMMITER_DATE raczej, bo w yamlowym pliku sobie to zapiszemy
#TODO: uzywac w yamlu "---" zeby moc czytac, pisac strumieniowo
#TODO: cc2git.yaml -> cc2git_tmp->yaml, a ostateczny tworzyc strumieniowo przy odpalaniu gita i wpisywac tam hasze commitow


import os
import os.path
import yaml
import bisect
from time import time

db = []

def parse_version(version):
    version = version.strip().strip("\"").split("@@", 1)
    result = {}
    if len(version) > 1 and len(version[0]) > 0:
        pathandname = os.path.split(version[0])
        if len(pathandname[0]) > 0:
            result["path"] = pathandname[0]
        if len(pathandname[1]) > 0:
            result["name"] = pathandname[1]
    branchandnr = ""
    if len(version) == 1:
        branchandnr = version[0]
    elif len(version[1]) > 0:
        branchandnr = version[1]
    if len(branchandnr) > 0:
        branchandnr = os.path.split(branchandnr)
        if len(branchandnr[0]) > 0:
            result["branch"] = branchandnr[0]
        if len(branchandnr[1]) > 0:
            result["nr"] = branchandnr[1]
    return result

def parse_hyperlink(link):
    link = link.split("@", 2)
    link = {"type":link[0].strip(), "nr":link[1].strip(), "link":link[2].strip()} #TODO: sparsowac pole "link"
    return link



def parse_describe(describe):
    info = {}
    line = describe.readline()
    line = line.strip().split()
    if line[0] == "version":
        info["type"] = "file"
        info["version"] = parse_version(line[1])
        if info["version"]["nr"] == "CHECKEDOUT":
            if line[2] != "from":
                raise Exception
            info["version"]["from"] = parse_version(line[3])
            return info #TODO: moze kiedys parsowac dokladniej wycheckoutowane pliki..
        line = describe.readline() #created...
        line = line.strip().split(" ", 1)
        if line[0].strip() != "created":
            raise Exception
        line = line[1].split("by", 1)
        info["datetime"] = line[0].strip() #TODO: parsowanie daty i czasu
        info["creator"] = line[1].strip()
        comment = ""
        line = describe.readline()
        while len(line) > 0 and line.strip() != "Element Protection:":
            comment += line
            line = describe.readline()
        info["comment"] = comment.strip()
        if len(line) == 0:
            return info
        #Element Protection:
        line = describe.readline() #User
        line = line.split(":", 2)
        if line[0].strip() != "User":
            raise Exception
        info["protection"] = {"user":{"name":line[1].strip(), "rights":line[2].strip()}}
        line = describe.readline() #Group
        line = line.split(":", 2)
        if line[0].strip() != "Group":
            raise Exception
        info["protection"]["group"] = {"name":line[1].strip(), "rights":line[2].strip()}
        line = describe.readline() #Other
        line = line.split(":", 2)
        if line[0].strip() != "Other":
            raise Exception
        info["protection"]["other"] = {"name":line[1].strip(), "rights":line[2].strip()}

        line = describe.readline()
        if line.strip().startswith("element type:"):
            line = line.split(":", 1)
            info["elementtype"] = line[1].strip()
            line = describe.readline()

        if line.strip().startswith("predecessor version:"):
            line = line.split(":", 1)
            line = os.path.split(line[1].strip())
            info["predecessor"] = {"branch":line[0], "nr":line[1]}
            line = describe.readline()
        
        if line.strip() == "Labels:":
            info["labels"] = []
            line = describe.readline()
            while len(line) > 0 and line.find(":") == -1:
                info["labels"].append(line.strip())
                line = describe.readline()

        dump_hyperlinks = False #TODO: chcemy hyperlinki? (sa dlugie i pliki z dumpami sa potem brzydkie bo linie sa lamane)

        if dump_hyperlinks and line.strip() == "Hyperlinks:":
            info["hyperlinks"] = []
            line = describe.readline()
            while len(line) > 0 and line.find(":") == -1:
                info["hyperlinks"].append(parse_hyperlink(line.strip()))
                line = describe.readline()
    else:
        info["type"] = "unknown"
    return info

def file2db(cc_f, git_f):
    print "file2db", cc_f
    describe = os.popen("cleartool describe -long " + cc_f)
    info = parse_describe(describe)
    describe.close()
    if info["type"] == "file":
        if info["version"]["nr"] == "CHECKEDOUT":
            describe = os.popen(
                "cleartool describe -long " +
                cc_f +
                "@@" +
                info["version"]["from"]["branch"] +
                "/" +
                info["version"]["from"]["nr"]
            )
            info = parse_describe(describe)
            describe.close()
        desc_list = []
        while info != None:
            key = [
                info["datetime"],
                info["creator"],
                info["version"]["path"],
                info["version"]["name"],
                info["version"]["branch"],
                info["version"]["nr"],
            ]
            bisect.insort(db, key)
            desc_list.append(info)
            if info.has_key("predecessor"):
                describe = os.popen(
                    "cleartool describe -long " +
                    cc_f +
                    "@@" +
                    info["predecessor"]["branch"] +
                    "/" +
                    info["predecessor"]["nr"]
                )
                info = parse_describe(describe)
                describe.close()
            else:
                info = None
        desc_list.reverse() #TODO: czy musimy to odwracac? chyba nie..
        out = open(git_f, 'w')
        yaml.dump(desc_list, out, default_flow_style=False, indent=4)
        out.close()
    else:
        pass #TODO:obsluga innych typow (skrotow do plikow i do katalogow i plikow prywatnych czy cos..



def walk(top_dirs, cc_dir, files):
    (cc_top, git_top) = top_dirs
    if cc_dir.find(cc_top) != 0:
        raise Exception
    cc_dirrest = cc_dir[len(cc_top):].strip("/")

    print "walk", cc_dir
    for f in files:
        cc_f = os.path.join(cc_dir, f)
        git_f = os.path.join(git_top, cc_dirrest, f)
        if os.path.isfile(cc_f):
            file2db(cc_f, git_f)
        elif os.path.isdir(cc_f):
            try:
                os.mkdir(git_f)
            except os.error: #TODO: lapac tylko wyjatek typu File exists
                pass


def main(cc_dir, git_dir):

    try:
        os.mkdir(git_dir)
    except os.error: #TODO: lapac tylko wyjatek typu File exists
        pass
    os.path.walk(cc_dir, walk, (cc_dir, git_dir))
    #print yaml.dump(db)
    #pprint(db)
    f = open(os.path.join(git_dir, "cc2git_db.yaml"), 'w')
    yaml.dump(db, f, default_flow_style=False, indent=4) #TODO: upewnic sie ze nawet jak cos po drodze sie wysypie to i tak ta linijka sie wykona..
    f.close()

if __name__ == '__main__':
    starttime = time()
    """
    if len(sys.argv) != 3:
        print __doc__
        exit()
    main(sys.argv[1], sys.argv[2])
    """
    #main("/home/langiewi_m/p2_latest/develop/source/siemens/applications/html/tests", "/home/langiewi_m/projects/cc2git/test2")
    #main("/home/langiewi_m/p2_latest/develop/source/siemens/applications/html/scripts", "/home/langiewi_m/projects/cc2git/test3")
    #main("/home/langiewi_m/p2_latest/develop/source/siemens/applications", "/home/langiewi_m/projects/cc2git/test_05_applications")
    #main("/home/langiewi_m/p2_latest/develop/source/siemens/applications/cma", "/home/langiewi_m/projects/cc2git/test_06_cma")

    




    #Test shell stuff:
    """
    os.system("A=bla ; B=ble ; echo test1: A=$A B=$B ; export")
    os.system("export")
    os.system("echo test2: A=$A B=$B")
    os.system("export")
    os.system("cd ~/tmp ; pwd")
    os.system("pwd")
    """



    #test popen2
    """
    import popen2, string
    fin, fout = popen2.popen2("cleartool")
    fout.write("help\n\n")
    fout.flush()
    #sleep(5)

    l = fin.readline(),
    while l != "":
        print l
        l = fin.readline(),
    #fout.close()
    #fin.close()
    fout.write("help rebase\n\n")
    fout.flush()
    #sleep(5)
    l = fin.readline(),
    while l != "":
        print l
        l = fin.readline(),
    #fout.close()
    #fin.close()
    """

    endtime = time()

    print "calkowity czas dzialania:", endtime - starttime



