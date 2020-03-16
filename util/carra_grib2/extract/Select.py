import yaml
import copy
import datetime
import subprocess
import os
import sys
import time


def fill_pattern(pattern, dt, step):
    out = pattern.replace("@YYYY@", dt.strftime("%Y"))
    out = out.replace("@MM@", dt.strftime("%m"))
    out = out.replace("@DD@", dt.strftime("%d"))
    out = out.replace("@HH@", dt.strftime("%H"))
    out = out.replace("@LLL@", "%03d" % step)
    return out.strip()


def fstep(step):
    if step == 0:
        fstep = 0
    elif step <= 6:
        fstep = step - 1
    else:
        fstep = step - 3
    return fstep


def fill_rule(task, ruledir, taskRule='rules.batch'):
    orule = open(taskRule, 'w')
    with open(ruledir+'/'+task['rulefile'], 'r') as irule:
        for iline in irule:
            oline = iline
            for key in task['conf']:
                old_str = '@'+key+'@'
                if old_str in oline:
                    oline = oline.replace(old_str, str(task['conf'][key]))
            orule.write(oline)
    orule.close()
    return taskRule


def prep_selection_config(dt, configYML='Selection.yml'):
    HH = dt.strftime('%H')
    if HH in ['00', '12']:
        cycle = 'long'
    else:
        cycle = 'short'
    with open(configYML, 'r') as conf:
        conf_dict = yaml.safe_load(conf)
    task_specs = {}
    for ttype in ['an', 'fc']:
        for level in conf_dict['level']:
            l = conf_dict['level'][level]
            d = l['default']
            steps = conf_dict['cycles'][cycle]
            for spec in l:
                config = copy.deepcopy(d)
                config.update(l[spec])
                if ttype in config:
                    config.update(config[ttype])
                if 'steps' not in config:
                    config['steps'] = list(steps)
                if ttype == 'an':
                    config['steps'] = [0]
                elif ttype == 'fc':
                    if len(config['steps']) > 1 and 0 in config['steps']:
                        config['steps'].remove(0)
                suffix = "" if spec == "default" else spec
                result = "%s_%s_@YYYY@@MM@@DD@@HH@_@LLL@.grib1%s " % (ttype, level, suffix)
                task_specs[result] = config
    return task_specs


def prep_tasks(dt, task_specs, outdir, archive):
    ptasks = []
    for task in task_specs:
        for step in task_specs[task]['steps']:
            outfile = fill_pattern(task, dt, step)
            infile = fill_pattern(task_specs[task]['filepattern'], dt, step)
            ffstep = fstep(step)
            ptask = {'outfile': outfile,
                     'infile': archive+'/'+infile,
                     'rulefile': task_specs[task]['rules'],
                     'conf': {
                             'ltype': task_specs[task]['ltype'],
                             'dtg': dt.strftime("%Y%m%d%H"),
                             'step': "%03d" % step,
                             'select': 1,
                             'tableVer': 16,
                             'convert': 1,
                             'out1': outdir,
                             'fstep': ffstep,
                             'date': dt.strftime("%Y%m%d"),
                             'time': dt.strftime("%H")}
                     }
            ptasks.append(ptask)
    return ptasks


def dump_inputfiles(ptasks):
    infiles = []
    for ptask in ptasks:
        f = ptask['infile']
        if f not in infiles:
            infiles.append(f)
            print(f)


def process_tasks(ptasks,ruledir):
    pids = {}
    logs = {}
    for i in range(len(ptasks)):
        #print(ptasks[i],file=sys.stderr)
        rule = fill_rule(ptasks[i], ruledir, ptasks[i]['outfile']+'.rule')
        args = ['grib_filter', rule, ptasks[i]['infile']]
        #print(args,file=sys.stderr)
        p = subprocess.Popen(args)
        pids[p.pid] = p
        affinity = max([len(os.sched_getaffinity(0))-1,1])
        print("affinity=",affinity,file=sys.stderr)
        while len(pids) >= affinity:
            print("wait for resources",file=sys.stderr)
            time.sleep(1)
            for pid in pids:
                if pids[pid].poll() is not None:
                    pids.pop(pid)
                    print(pid, 'done',file=sys.stderr)
                    break
    for pid in pids:
        pids[pid].wait()
        print(pid, 'done',file=sys.stderr)
        


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='prepare and process grib_filter rules')
    parser.add_argument('dtg', type=str, help='date time group')
    parser.add_argument('--archive', type=str, required=True, help='path to input files')
    parser.add_argument('--carrabin', type=str, required=True, help='path to installation, util/carra_grib2/extract')
    parser.add_argument('-d','--dump',default=False, action='store_true',help='dump a list of inputfiles')
    args = parser.parse_args()

    dt = datetime.datetime.strptime(args.dtg, '%Y%m%d%H')
    carrabin = args.carrabin
    archive = args.archive
    outdir = '.'

    task_specs = prep_selection_config(dt, carrabin+'/Selection.yml')
    ptasks = prep_tasks(dt, task_specs, outdir, archive)
    if args.dump:
        dump_inputfiles(ptasks)
    else:
        process_tasks(ptasks,carrabin)

