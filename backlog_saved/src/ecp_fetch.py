#!/usr/local/apps/python3/3.6.10-01/bin/python3

import subprocess
import os
import datetime
import time
import sys


def find_on_ecfs(filenames,ecfsdir):
    tic = time.time()
    files = {}
    dt = datetime.datetime.strptime(filenames[0][0:14],"%Y/%m/%d/%H/")
    args = ['els',ecfsdir+dt.strftime("/%Y/%m/%d")+'/*']
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    els = p.communicate()[0].splitlines()
    stringlist=[x.decode('utf-8') for x in els]
    for f in filenames:
        basename = os.path.basename(f)
        files[basename] = {'ecfs': None}
        if basename in stringlist:
            files[basename] = {'ecfs': ecfsdir+'/'+f}
    toc = time.time()
    print('ecfs:',toc-tic)
    return files


def fetch_files(ecfsdir,dts):
    # system
    grib_tmp_dir = "grib_tmp"
    ecfs_sources = "ecfs_sources"
    if not os.path.isdir(grib_tmp_dir):
        os.mkdir(grib_tmp_dir)
    # format list of files for ecp
    with open(ecfs_sources,'w') as srcf:
        for dt in dts:
            dpath = dt.strftime("%Y/%m/%d/%H/")
            date = dt.strftime("%Y%m%d")
            h = dt.strftime("%H")
            srcf.writelines("ec:%s/*.save.%s.%s00.not_yet.grib1\n" % (dpath,date,h))
            srcf.writelines("ec:%s/fc%s%s+000grib_sfx\n" % (dpath,date,h))
    # command line to execute
    args = ['module load ecfs;','ecd', ecfsdir,';',
            'ecp', '-F', ecfs_sources,'--order=tape', grib_tmp_dir+'/']
    # execution
    print(args)
    print("Fetch from ECFS...")
    print(" ".join(args))
    tic = time.time()
#    p = subprocess.Popen(" ".join(args),shell=True,stdout=subprocess.STDOUT,stderr=subprocess.STDOUT)
    p = subprocess.Popen(" ".join(args),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err = p.communicate()
    print(out)
    print(err)
#    time.sleep(5)
    toc = time.time()
    print("Time spent in ecp[s]: ",toc-tic)

#if __name__ == "__main__":

# args: dtg parent_exp

if len(sys.argv) != 3:
    print("takes exactly 2 arguments: PARENT_EXP DATE")
    exit()

yyyy = int(sys.argv[2][0:4])
mm = int(sys.argv[2][4:6])
dd = int(sys.argv[2][6:8])

print(yyyy,mm,dd)

dt = [datetime.datetime(yyyy,mm,dd,i*3) for i in range(8)]
ecfpath = "/nhx/harmonie/%s/" % sys.argv[1]

grib_tmp_dir = "grib_tmp"
if not os.path.isdir(grib_tmp_dir):
    os.mkdir(grib_tmp_dir)
if "grib_tmp" in os.listdir():
    content_0 = os.listdir("grib_tmp")

fetch_files(ecfpath,dt)

content_1 = os.listdir("grib_tmp")

if len(content_1) <= len(content_0):
    print(content_0)
    print("No files fetched!! CAUTION!!")
    print(content_1)
    #exit(1)
