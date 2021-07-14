import datetime
import os
import subprocess as sp
from ecflow import Defs,Suite,Family,Task,Edit,Trigger,RepeatDate
import ecflow


def create_task_script(task, cfg):
     t = task["Task"]
     path = cfg["home"] + t.get_abs_node_path().replace(t.name(),"")
     sp.check_output("mkdir -p %s" % path, shell=True)
     with open("%s/%s.ecf" % (path,t.name()) ,'w') as f:
         cat_file("src/head.h",f)
         f.write("\n")
         f.write("######### job start ########\n")
         f.write("\n")
         exports(f)
         f.write("export PATH=%s:$PATH\n" % cfg["bindir"])
         f.write("export BINDIR=%s\n" % cfg["bindir"])
         f.write("mkdir -p %s/%%DATE%%\n" % (cfg["scratch"]))
         f.write("cd %s/%%DATE%%\n" % (cfg["scratch"]))
         f.write("%s/%s %s\n" % (cfg["bindir"],task["prog"],task["args"]))
         f.write("\n")
         f.write("######### job end ########\n")
         f.write("\n")
         cat_file("src/tail.h",f)


def exports(f):
    f.write("export DATE=%DATE%\n")


def cat_file(fnam,dest):
    with open(fnam,"r") as head:
        for line in head:
            dest.write(line)


def cca_task(name,home):
    fam="Fetch"
    #sub = " qsub -N %s -o %%ECF_JOBOUT%% -e %%ECF_JOBOUT%% " % (name)
    sub = " qsub -N %s -o %%ECF_JOBOUT%% -j oe " % (name)
    job = " %s%%ECF_NAME%%.job%%ECF_TRYNO%% " % (home[4:])
    s1 = "ssh %HOST% 'mkdir -p %ECF_OUT%/%SUITE%/%FAMILY%; "
    s3 = " > %ECF_JOBOUT% 2>&1 &'"
    cmd = s1 + sub + job + s3
    return Task(name,
                HOST="cca",
                ECF_OUT = "%s" % (home[4:]),
                ECF_LOGHOST='%HOST%',
                ECF_LOGPORT='51949',
                ECF_JOB_CMD=cmd)



def add_suite(suite,cfg):
    
    ymd = "%Y%m%d"
    rep = RepeatDate("DATE",int(cfg["date"].strftime(ymd)),int(cfg["enddate"].strftime(ymd)))
    home = cfg["home"]    
    parent_exp = cfg["parent"]
    fams = {"Fetch":
             {"Trigger": Trigger("InitRun == complete"),
              "Repeat": rep,
              "tasks": 
                {"ecp":
                    {"Task": cca_task("ecp",home),
                    "prog": "ecp_fetch.py",
                    "args": "%s $DATE" % parent_exp
                      }
#                 "check":
#                    {"Task": cca_task("check",home) + Trigger("ecp == complete"),
#                     "prog": "check_fetched.py",
#                     "args": "$DATE"
#                     }
                 }
              },
            "Process":
              {"tasks":
                {"g12g2":
                   {"Task": cca_task("g12g2",home),
                     "prog": "grib1togrib2.sh",
                     "args": "$DATE %s $BINDIR" % parent_exp.upper()
                    },
                 "push2mars":
                    {"Task": cca_task("push2mars",home) + Trigger("g12g2 == complete"),
                     "prog": "archive_save.sh",
                     "args": "$DATE %s $BINDIR" % parent_exp.upper()}
                 },
               "Trigger": Trigger("(Fetch == complete or Fetch:DATE > Process:DATE) and InitRun == complete"),
               "Repeat": rep
               }
           }
    
    initrun = {"Task": Task("InitRun"),
                    "prog": "InitRun",
                    "args": "%s %s " % (cfg["expdir"], suite)
                      }

    with Defs() as defs:
        with defs.add_suite(suite) as s:
            s += Edit(ECF_HOME=cfg["home"])
            s.add_task(initrun["Task"])
            create_task_script(initrun,{"home":cfg["home"],"scratch":cfg["scratch"],"bindir":cfg["expdir"]})
            for fam in fams:
                with s.add_family(fam) as f:
                    f += fams[fam]["Trigger"]
                    f.add_repeat(fams[fam]["Repeat"])
                    for task in fams[fam]["tasks"]:
                        t = fams[fam]["tasks"][task]
                        f.add_task(t["Task"])
                        create_task_script(t,cfg)
                    
        #print("Checking job creation: .ecf -> .job0")
        #print(defs.check_job_creation())
        return defs


def assume(arg,guess,comment="var"):
    if arg is not None:
        var = arg
    else:
        var = guess # 1500 + os.getuid()
        print("Assume %s is %s" % (comment,str(var)))
    return var


def main(args):

    dt = datetime.datetime.strptime(args["date"], "%Y%m%d")
    enddate = assume(args["enddate"],args["date"], "ENDDATE")
    dtend = datetime.datetime.strptime(enddate, "%Y%m%d")

    if not args["replace"]:
        action = "add"
    else:
        action = "replace"

    suite = args["suite"]
    parent_exp = args["parent"]

    port = assume(args["port"], 1500 + os.getuid(), "ECF_PORT")
    host = assume(args["host"], "ecgate", "ECF_HOST")   
    hpc = assume(args["compute_server"], "cca", "compute server (where jobs are submitted)")

    scratch = os.path.join(os.getenv("SCRATCH"),"backlog_now/%s/" % suite)
    print("jobs run under %s:%s" % (hpc,scratch))
    bindir = scratch+"/src/"
    
    expdir = os.path.join(os.getenv("PWD"),"src")
    
    home = "/hpc/%s/BACKLOG/" % os.getenv("PERM")
    print("ECF_HOME is at %s" % home)
    
    cfg = {"home": home,
           "scratch":scratch,
           "bindir":bindir,
           "expdir":expdir,
           "date":dt,
           "enddate":dtend,
           "parent":parent_exp}
    
    
    defs = add_suite(suite,cfg)
    
    ci = ecflow.Client(host,str(port))
    try:
        if suite in ci.suites() and action == "replace":
            ci.replace(suite,defs)
        elif suite not in ci.suites() and action == "add":
            ci.load(defs)
        else:
            print("")
            print("EXIT! Not able to %s %s in [%s]" % (action,suite,", ".join(ci.suites())))
            exit(1)

        ci.begin_suite(suite)
    except RuntimeError as e:
       print("RuntimeError: Is the server running?")
       #exit(1)
       #raise e

    print("%s %s in [%s]" % (action, suite,", ".join(ci.suites())))
 
 


if __name__ == "__main__":
    
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='set up backlog archiving suite')
    parser.add_argument("--date", required=True, type=str, help="first date of archiving [yyyymmdd]")
    parser.add_argument("--enddate", type=str, default=None, help="last date of archiving [yyyymmdd]")
    parser.add_argument("--suite", required=True, type=str, default=None, help="name of suite")
    parser.add_argument("--parent", required=True, type=str, default=None, help="parent experiement")
    parser.add_argument("-r", "--replace", action='store_true', help="replace suite")
    parser.add_argument("--port", type=int, default=None, help="port of ecflow_server")
    parser.add_argument("--host", type=str, default=None, help="host of ecflow_server")
    parser.add_argument("--compute_server", type=str, default=None, help="which system to run jobsin")
    
    args = vars(parser.parse_args())
 
    main(args)
