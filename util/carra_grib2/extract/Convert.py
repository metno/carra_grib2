import eccodes as ecc
import numpy as np
import numpy.ma as ma
import yaml
import glob
import time
import multiprocessing as mp
import matplotlib.pyplot as plt


def run_pool_jobs(conf_dict,grib_dir,nproc=None):
    if nproc is None:
        nproc = mp.cpu_count() - 1
    pool = mp.Pool(nproc)
    print("converting with Ntasks=",nproc)
    tasks = []
    for key in config:
        infiles = glob.glob(grib_dir+'/'+conf_dict[key]['filepattern'])
        for ifile in infiles:
            #print(key,ifile,conf_dict[key]['name'])
            tasks.append(pool.apply_async(process_gf,args=(ifile,eval(conf_dict[key]['name']),)))
    pool.close()
    pool.join()
    return pool, tasks


def run_serial_jobs(conf_dict,grib_dir):
    for key in config:
        infiles = glob.glob(grib_dir+'/'+conf_dict[key]['filepattern'])
        for ifile in infiles:
            iret = process_gf(ifile,eval(conf_dict[key]['name']))
            if iret != 0:
                exit(1)


def parse_config(configYML):
    with open(configYML, 'r') as conf:
        conf_dict = yaml.safe_load(conf)
    return conf_dict



def write_gf(fnam,messages):
    with open(fnam,'wb') as fout:
        for msg in messages:
            msg.write(fout)
    return 0


def read_gf(fnam):
    gfin = ecc.GribFile(fnam)
    msgs = []
    for i in range(len(gfin)):
        msg = ecc.GribMessage(gfin)
        msgs.append(ecc.GribMessage(clone=msg))
    gfin.close()
    del gfin
    return msgs


def process_gf(fnam,func):
    msgs_in = read_gf(fnam)
    msgs_out = []
    for msg in msgs_in:
        missval = msg['missingValue']
        msg2 = msg
        msg2['values'] = np.where(msg2['values'] != missval, func(msg['values']),missval)
        msgs_out.append(msg2)
    write_gf(fnam+'on',msgs_out)
    del msgs_in
    del msgs_out
    return 0


def change_sign(x):
    return -x


def frac_2_percent(x):
    x0 = np.where(x>0.9999,100,x*100)
    x1 = np.where(x0<0.01,0,x0)
    del x0
    return x1


def remove_negatives(x):
    return np.where(x<0,0,x)


def phi2z(x):
    return x*0.10194


if __name__ == "__main__":
  
    import argparse


    parser = argparse.ArgumentParser(description='convert fields')
    parser.add_argument('--gribdir', type=str, required=True, help='path to grib files (I/O)')
    parser.add_argument('--cfg', type=str, required=True, help='yaml file containing conversion rules')
    parser.add_argument('--npool',default=1, type=int, help='number of tasks in pool')
    
    args = parser.parse_args()

    
    ymlfile = args.cfg
    carra_grib = args.gribdir
    nproc = args.npool

    config = parse_config(ymlfile)
    tic = time.time()
    if nproc == 1:
        run_serial_jobs(config,carra_grib)
    else:
        p, tasks = run_pool_jobs(config,carra_grib,nproc=nproc)
        for t in tasks:
            tg = t.get()
            if tg != 0:
               print(tg)
    print(time.time() - tic)
