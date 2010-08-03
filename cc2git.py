#!/usr/bin/env python

"""Clearcase to Git Exporter

Exports the Clearcase history to git repo.
Usage: cc2git input_dir metadata_output_topdir git_output_dir exclude_regexp


"""
#TODO: stage2: linki i puste katalogi trzeba przekopiowac z drzewa meta do drzewa git. (dla pustych katalogow tworzyc .gitignore)
#TODO: albo poprostu skopiowac cale meta jako pierwsza wersje gita (czyli w meta musimy miec juz puste katalogi(.gitignore) i linki
#TODO: uzywac w yamlu "---" zeby moc czytac, pisac strumieniowo;

import os
import os.path
import sys
import yaml
import bisect
from time import time
from pprint import pprint
from cc2git_common import Log
from cc2git_common import run_command
from cc2git_common import try_command_out
from cc2git_common import make_path
from cc2git_common import time_str
from cc2git_common import walk_exclude

DEFAULT_DBFILE="db.yaml"

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
        if len(info["datetime"]) < 3:
            raise Exception #FIXME: tymczasowo bo czasem dodajemy chyba pusta date..
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
                #TODO: narazie olewam hyperlinki..
                lines = lines[i:]
            else:
                print "Error: unknown line found in describe output:"
                print lines[0].strip()
                print "ignoring..."
                lines = lines[1:]
    else:
        info["type"] = "unknown"
    return info

def file2db(cc_f, meta_f):
    global db
    print "file2db", cc_f
    cmd = "cleartool describe -long \"" + cc_f + "\""
    out = try_command_out(cmd)
    try:
    	info = parse_describe(out)
    except:
        print "Error: coudln\'t parse this cleartool describe output...:"
        print "The command was:", cmd
        print "The output was:"
        print out
        print
        return
    if info["type"] == "file":
        if info["version"]["nr"] == "CHECKEDOUT":
            cmd = "cleartool describe -long \""+cc_f+"@@"+info["version"]["from"]["branch"]+"/"+info["version"]["from"]["nr"]+"\""
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
        desc_list = []
        while info != None:
            try:
                key = [
                    info["datetime"],
                    info["creator"],
                    info["version"]["path"],
                    info["version"]["name"],
                    info["version"]["branch"],
                    info["version"]["nr"],
                ]
            except:
                print "Error: coudln\'t get enough information from parsed describe...:"
                print "info:"
                pprint(info)
                print
                break
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
        out = open(meta_f, 'w')
        yaml.dump(desc_list, out, default_flow_style=False, indent=4)
        out.close()
    else:
        pass #TODO: moze kiedys: lepsza obsluga innych typow (skrotow do plikow i do katalogow i plikow prywatnych czy cos..


def stage1_walk(top_dirs, cc_actdir, files, fileforemptydirs=".gitignore"):
    """
    fileforemptydirs - an empty file with that name will be placed in any empty directory in meta tree
    """
    global db
    cc_topdir, meta_topdir = top_dirs
    if cc_actdir.find(cc_topdir) != 0:
        raise Exception
    cc_dirrest = cc_actdir[len(cc_topdir):].strip("/")

    print "walk", cc_actdir

    if len(files) == 0:
        f = os.path.join(meta_topdir, cc_dirrest, fileforemptydirs)
        open(f, "w").close()
    else:
        for file in files:
            cc_fullfile = os.path.join(cc_actdir, file)
            meta_fullfile = os.path.join(meta_topdir, cc_dirrest, file)
            if os.path.isfile(cc_fullfile):
                file2db(cc_fullfile, meta_fullfile)
            elif os.path.isdir(cc_fullfile):
                make_path(meta_fullfile)
            elif os.path.islink(cc_fullfile):
                os.system("cp -d -f " + cc_fullfile + " " + meta_fullfile)

def stage1(cc_topdir, meta_topdir, exclude, dbfilename=DEFAULT_DBFILE):
    global db
    print "******** STAGE 1 **********"
    make_path(meta_topdir)
    try:
        walk_exclude(cc_topdir, stage1_walk, (cc_topdir, meta_topdir), exclude)
    finally:
        f = open(os.path.join(meta_topdir, dbfilename), 'w')
        yaml.dump(db, f, default_flow_style=False, indent=4)
        f.close()

def stage2(cc_topdir, meta_topdir, git_topdir, use_global_db_value=True, dbfilename=DEFAULT_DBFILE, clearcasepretend=False):
    """
    if use_global_db_value == True, it uses actual value of db variable instead of load it from dbfilename
    if clearcasepretend is True it does not use clearcase at all, but inserts some metadata to files in git tree for testing purposes
    """
    global db
    print "******** STAGE 2 **********"
    if not use_global_db_value:
        dbfile = open(os.path.join(meta_topdir, dbfilename))
        db = yaml.load(dbfile)
        dbfile.close()

    run_command("cp -d -f -R -v \"" + meta_topdir + "\" \"" + git_topdir + "\"")
    run_command("cd " + git_topdir + " ; git init")
    run_command("cd " + git_topdir + " ; git add -- .")
    run_command("cd " + git_topdir + " ; git commit -m \"cc2git_v01: metadata - initial commit\"")

    for key in db:
        date, author, dir, fname, branch, ver = key

        if dir.find(cc_topdir) != 0:
            raise Exception
        dirrest = dir[len(cc_topdir):].strip("/")
        dirrest_fname = os.path.join(dirrest, fname)
        cc_fullfile = os.path.join(dir, fname)
        meta_fullfile = os.path.join(meta_topdir, dirrest_fname) #TODO: tego chyba nawet nie uzyjemy przynajmniej narazie..
        git_actdir = os.path.join(git_topdir, dirrest)
        git_fullfile = os.path.join(git_actdir, fname)
        make_path(git_actdir)
        dirrest_fname_branch_ver = dirrest_fname + "@@" + branch + "/" + ver
        cc_dir_fname_branch_ver = os.path.join(cc_topdir, dirrest_fname_branch_ver)
        run_command("cp -d -f \"" + cc_dir_fname_branch_ver + "\" \"" + git_fullfile + "\"", log=Log.LITTLE, pretend=clearcasepretend)
        if clearcasepretend:
            f = open(git_fullfile, "w")
            yaml.dump(key, f)
            f.close()

        run_command("cd \"" + git_actdir + "\" ; git add -- \"" + fname + "\"", log=Log.LITTLE)
        email = "unknown@nowhere.todo" #TODO: get real email from author name
        vars = "export GIT_AUTHOR_NAME=\"" + author + "\"" + " GIT_AUTHOR_DATE=\"" + date + "\" GIT_AUTHOR_EMAIL=\"" + email + "\" GIT_COMMITTER_NAME=\"" + author + "\" GIT_COMMITTER_DATE=\"" + date + "\" GIT_COMMITTER_EMAIL=\"" + email + "\""
        run_command(vars + " ; cd \"" + git_topdir + "\"; git commit -m \"cc2git_v01: file: " + dirrest_fname_branch_ver + "\"", log=Log.LITTLE) #TODO: prawdziwy komentarz z clearcasea


def main(cc_topdir, meta_topdir, git_topdir, exclude="a^"): #FIXME: better default exclude (to match nothing)
    stage1(cc_topdir, meta_topdir, exclude) #creates metadata tree using clearcase
    stage2(cc_topdir, meta_topdir, git_topdir) #creates git repo using metadata tree and clearcase

if __name__ == '__main__':

    starttime = time()

    if len(sys.argv) != 5:
        print __doc__
        exit()
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    endtime = time()

    print "calkowity czas dzialania:", time_str(endtime - starttime)



