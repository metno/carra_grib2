import yaml
import copy
import datetime
import subprocess
import os


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
                    else:
                        continue
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

def process_tasks(ptasks,ruledir):
    pids = {}
    logs = {}
    for i in range(len(ptasks)):
        rule = fill_rule(ptasks[i], ruledir, ptasks[i]['outfile']+'.rule')
        args = ['grib_filter', rule, ptasks[i]['infile']]
#        args = ['./process.sh']
        logfile = open('log'+str(i),'w')
        p = subprocess.Popen(args, stdout=logfile,stderr=logfile)
        pids[p.pid] = p
        logs[p.pid] = logfile
        affinity = len(os.sched_getaffinity(0))
        while len(pids) >= affinity - 1:
            for pid in pids:
                if pids[pid].poll() is not None:
                    pids.pop(pid)
                    logs[pid].close()
                    print(pid, 'done')
                    break




if __name__ == '__main__':
    import sys

    dt = datetime.datetime.strptime(sys.argv[1], '%Y%m%d%H')
    carrabin = sys.argv[2]
    archive = sys.argv[3]
    outdir = '.'

    task_specs = prep_selection_config(dt, carrabin+'/Selection.yml')
    ptasks = prep_tasks(dt, task_specs, outdir, archive)
    process_tasks(ptasks,carrabin)
