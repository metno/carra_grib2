import json
import argparse

def asci2list(asciiFileName):
    parents = []
    with open(asciiFileName,'r') as f:
        for l in f:
            if len(l) < 3:
                continue
            try:
                l0 = l.rstrip()
                l1 = l0.split(" ")
                l2 = l1[-1].split("-")
                parents.append({l1[0]: {"startDate":l2[0],"endDate":l2[-1]}})
            except Exception as e:
                pass
    return parents

#    with open("parent_exps.json","w") as f:
#       json.dump(parents,f,indent=4)




def getParent(parent_list,dtg,dtgend=None,domain=None):
    # return dict {exp:{startDate:1,edndate:2}, exp2}
    plan = []
    dtg = int(dtg)
    dtgend = int(dtgend)
    dtgend0 = dtg if dtgend is None else dtgend
    if dtg > dtgend0:
        print("startDate > endDate: abort!!!")
        return None
    for i in range(len(parent_list)):
        exp = list(parent_list[i].keys())[0]
        if domain is not None:
            if domain not in exp:
                continue
        pd = parent_list[i][exp]
        t0 = int(pd["startDate"])
        t1 = int(pd["endDate"])
        if dtg <= t1 and dtgend0 >= t0:
            p = {exp:{}}
            p[exp]["startDate"] = dtg if t0 <= dtg else t0
            p[exp]["endDate"] = dtgend0 if t1 >= dtgend0 else t1
            plan.append(p)
    return plan

def get_plan(args):
    if "ascii" not in args:
        args["ascii"] = None
    if "json" not in args:
        args["json"] = None
    if args["ascii"] is not None:
        par_list = ascii2list(args["ascii"])
    elif args["json"] is not None:
        with open(args["json"],"r") as f:
            par_list = json.load(f)
    else:
        print("Please provide a file with stream overview: --json/ascii")
        exit(1)
    	 
    plan = getParent(par_list,args["date"], dtgend=args["enddate"],domain=args["domain"])
    return plan
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Plan streams, find parent exps')
    parser.add_argument("--date", required=True, type=int, help="first date of archiving [yyyymmdd]")
    parser.add_argument("--enddate", type=int, default=None, help="last date of archiving [yyyymmdd]")
    parser.add_argument("--domain", required=False, type=str, default=None, help="NE/IGB")
    parser.add_argument("--json", required=False, type=str, default=None, help="json file")
    parser.add_argument("--ascii", required=False, type=str, default=None, help="ascii file")
    parser.add_argument("-o","--output", required=False, type=str, default="plan.json", help="output")

    args = vars(parser.parse_args())

    plan = get_plan(args)
    with open(args["output"],'w') as f:
        json.dump(plan,f,indent=4)


