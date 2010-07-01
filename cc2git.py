#!/usr/bin/env python

"""Clearcase to Git Exporter

Exports the Clearcase history to git repo.
Usage: cc2git input_dir output_dir dbfilename


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
#TODO: uzyc popen2 do zarzadzania cleartoolem ??
#TODO: commit --date i --author (olewamy GIT_COMMITER_DATE raczej, bo w yamlowym pliku sobie to zapiszemy
#TODO: uzywac w yamlu "---" zeby moc czytac, pisac strumieniowo
#TODO: cc2git.yaml -> cc2git_tmp->yaml, a ostateczny tworzyc strumieniowo przy odpalaniu gita i wpisywac tam hasze commitow
#TODO: liczbe prob w try_command_out dac na jakies 20 bo chyba warto... (i moze pause zmienic)

import os
import os.path
import yaml
import bisect
from time import time
from cc2git_common import try_command_out
from cc2git_common import run_command

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

def which_string_contains_oneof(stringlist, substringlist, start=0):
    """
    If none - returns len(stringlist)
    """
    for i in range(start, len(stringlist)):
        for substring in substringlist:
            if stringlist[i].find(substring) != -1:
                return i
    return len(stringlist)

def parse_describe(describe):
    SECTION_NAMES = [
        "Protection:",
        "element type:",
        "predecessor version:",
        "Labels:",
        "Hyperlinks:",
    ]
    lines = describe.splitlines()
    info = {}
    lines[0] = lines[0].strip().split(" ", 1)
    if lines[0][0] == "version":
        info["type"] = "file"
        info["version"] = parse_version(lines[0][1])
        if info["version"]["nr"] == "CHECKEDOUT":
            if lines[0][2] != "from":
                raise Exception
            info["version"]["from"] = parse_version(lines[0][3])
            return info #TODO: moze kiedys parsowac dokladniej wycheckoutowane pliki..
        created = lines[1].strip().split(" ", 1)
        if created[0].strip() != "created":
            raise Exception
        created = created[1].split("by", 1)
        info["datetime"] = created[0].strip() #TODO: parsowanie daty i czasu
        info["creator"] = created[1].strip()
        i = which_string_contains_oneof(lines, SECTION_NAMES, 2)
        info["comment"] = "\n".join(lines[2:i]).strip()
        if i == len(lines):
            return info
        lines = lines[i:]


        while len(lines) > 0:
            if lines[0].strip() == "Element Protection:":
                user = lines[1].split(":", 2)
                info["protection"] = {"user":{"name":user[1].strip(), "rights":user[2].strip()}}
                group = lines[2].split(":", 2)
                info["protection"]["group"] = {"name":group[1].strip(), "rights":group[2].strip()}
                other = lines[3].split(":", 2)
                info["protection"]["other"] = {"name":other[1].strip(), "rights":other[2].strip()}
                lines = lines[4:]
            elif lines[0].strip().startswith("element type:"):
                elemtype = lines[0].split(":", 1)
                info["elementtype"] = elemtype[1].strip()
                lines = lines[1:]
            elif lines[0].strip().startswith("predecessor version:"):
                predver = lines[0].split(":", 1)
                predver = os.path.split(predver[1].strip())
                info["predecessor"] = {"branch":predver[0], "nr":predver[1]}
                lines = lines[1:]
            elif lines[0].strip() == "Labels:":
                i = which_string_contains_oneof(lines, SECTION_NAMES, 1)
                info["labels"] = lines[1:i]
                lines = lines[i:]
            elif lines[0].strip() == "Hyperlinks:":
                i = which_string_contains_oneof(lines, SECTION_NAMES, 1)
                #FIXME: narazie olewam hyperlinki..
                lines = lines[i:]
            else:
                print "Error: unknown line found in describe output:"
                print lines[0].strip()
                print "ignoring..."
                lines = lines[1:]
    else:
        info["type"] = "unknown"
    return info

def file2db(cc_f, git_f):
    global db
    print "file2db", cc_f
    info = parse_describe(try_command_out("cleartool describe -long \"" + cc_f + "\""))
    if info["type"] == "file":
        if info["version"]["nr"] == "CHECKEDOUT":
            cmd = "cleartool describe -long \""+cc_f+"@@"+info["version"]["from"]["branch"]+"/"+info["version"]["from"]["nr"]+"\""
            info = parse_describe(try_command_out(cmd))
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
                cmd = "cleartool describe -long \""+cc_f+"@@"+info["predecessor"]["branch"]+"/"+info["predecessor"]["nr"]+"\""
                out = try_command_out(cmd)
                try:
                    info = parse_describe(out)
                except:
                    print "Error: coudln\'t parse this cleartool describe output...:"
                    print "The command was:", cmd
                    print "The output was:"
                    print out
                    print
                    info = None
            else:
                info = None
        #desc_list.reverse() #TODO: czy musimy to odwracac? chyba nie..
        out = open(git_f, 'w')
        yaml.dump(desc_list, out, default_flow_style=False, indent=4)
        out.close()
    else:
        pass #TODO:obsluga innych typow (skrotow do plikow i do katalogow i plikow prywatnych czy cos..


def walk(top_dirs, cc_dir, files):
    global db
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
                os.makedirs(git_f)
            except os.error: #TODO: lapac tylko wyjatek typu File exists
                pass
        elif os.path.islink(cc_f):
            os.system("cp -d " + cc_f + " " + git_f)

def stage2(cc_dir, git1_dir1, git2_dir, dbfilename):
    global db
    for key in db:
        pass #dupa!


def main(cc_dir, git_dir, dbfilename):
    global db

    try:
        os.makedirs(git_dir)
    except os.error: #TODO: lapac tylko wyjatek typu File exists
        pass

    try:
        os.path.walk(cc_dir, walk, (cc_dir, git_dir))
    finally:
        f = open(dbfilename, 'w')
        yaml.dump(db, f, default_flow_style=False, indent=4)
        f.close()

if __name__ == '__main__':
    starttime = time()
    """
    if len(sys.argv) != 4:
        print __doc__
        exit()
    main(sys.argv[1], sys.argv[2], sys.argv[3])
    """



    """
    main(
        "/home/langiewi_m/p2_latest/develop/source/siemens/applications/cma/digitmap",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma/digitmap",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma/db.yaml"
    )
    main(
        "/home/langiewi_m/p2_latest/develop/source/siemens/applications/cma/doc",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma/doc",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma/db.yaml"
    )
    main(
        "/home/langiewi_m/p2_latest/develop/source/siemens/applications/cma/callcontrol",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma/callcontrol",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma/db.yaml"
    )
    run_command("cd /home/langiewi_m/projects/cc2git_tests/ ; cp -a test_06_cma test_06_cma_git")
    run_command("cd /home/langiewi_m/projects/cc2git_tests/test_06_cma_git ; git init")
    stage2(
        "/home/langiewi_m/p2_latest/develop/source/siemens/applications/cma",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma_git",
        "/home/langiewi_m/projects/cc2git_tests/test_06_cma/db.yaml"
    )
    """




    VIEW = "LANGIEWI_M_PORTA_BAS_052_MAINT_PREINT"
    VOBS = ["common_software", "components", "danube_tc", "porta", "porta_kernel", "porta_kernel_2_4_31", "porta_tools"]
    OUT_DIR = "/home/langiewi_m/projects/cc2git_tests/test_07_all/"
    for vob in VOBS:
        main(
            "/view/" + VIEW + "/vobs/" + vob,
            OUT_DIR + "/vobs/" + vob,
            OUT_DIR + "db.yaml"

        )

    endtime = time()

    print "calkowity czas dzialania:", endtime - starttime



