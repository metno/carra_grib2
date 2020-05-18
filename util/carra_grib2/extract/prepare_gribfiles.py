import subprocess
import os
import datetime
import time


def find_on_scratch(filenames,scratchdir):
    tic = time.time()
    files = {}
    for f in filenames:
        basename = os.path.basename(f)
        files[basename] = {'scratch': None}
        if os.path.isfile(scratchdir+'/'+f):
            files[basename] = {'scratch': scratchdir+'/'+f}
    toc = time.time()
    print('scratch:',toc-tic)
    return files


def find_local(filenames):
    tic = time.time()
    files = {}
    locdir = os.environ['ARCHIVE_ROOT']
    for f in filenames:
        basename = os.path.basename(f)
        files[basename] = {'local': None}
        if os.path.isfile(locdir+'/'+f):
            files[basename] = {'local': locdir+'/'+f}
    toc = time.time()
    print('local:',toc-tic)
    return files


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

    

def parse_file(ffile):
    with open(ffile,'r') as f:
        filenames = f.read().splitlines()
    return filenames


def dump_file_list(fileDict):
    for f in fileDict:
            print(f,fileDict[f])


def prep_files(fileDict):
    dump_file_list(fileDict)
    grib_tmp_dir = os.environ['WRK']+'/grib_tmp'
    ecfs_sources = 'ecfs_sources'
    if not os.path.isdir(grib_tmp_dir):
        os.mkdir(grib_tmp_dir)
    ecfs_files = []
    for f in fileDict:
        basename = os.path.basename(f)
        if fileDict[f]['local'] is not None:
            print("already have file",basename)
        elif fileDict[f]['scratch'] is not None:
            dest = '%s/%s' % (grib_tmp_dir,basename)
            if not os.path.isfile(dest):
                os.symlink(fileDict[f]['scratch'], dest)
        elif fileDict[f]['ecfs'] is not None:
            ecfs_files.append(fileDict[f]['ecfs']+'\n')
    if len(ecfs_files) > 0:
        hours = []
        for f in fileDict:
            ecfs_path = os.path.dirname(fileDict[f]['ecfs'])
            hour = ecfs_path.split('/')[-1]
            if hour not in hours:
                hours.append(hour)
        datepath = "/".join(ecfs_path.split('/')[0:-1])
        print(datepath)
            
        with open(ecfs_sources,'w') as srcf:
            for hour in hours:
                srcf.writelines("ec:%s/%s\n" % (hour,"fc*grib"))
                srcf.writelines("ec:%s/%s\n" % (hour,"fc*grib_fp"))
                srcf.writelines("ec:%s/%s\n" % (hour,"fc*grib_sfx"))
                srcf.writelines("ec:%s/%s\n" % (hour,"[s,b]a*grib"))
        args = ['/bin/bash','-c','module load ecfs;','ecd', datepath,';', 'ecp', '-F', ecfs_sources,'--order=tape', grib_tmp_dir+'/']
        print("Fetch from ECFS...")
        print(" ".join(args))
        tic = time.time()
        p = subprocess.Popen(" ".join(args),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = p.communicate()
        print(out)
        print(err)
        toc = time.time()
        print("Time spent in ecp[s]: ",toc-tic)
    
        


if __name__ == '__main__':
    
    import argparse
    
    
    parser = argparse.ArgumentParser(description='prepare and process grib_filter rules')
    parser.add_argument('infiles', type=str, help='file with list of filenames relative to archive_root')
    parser.add_argument('--scratch_archive_root', type=str, required=True, help='path to archive_root of parent')
    parser.add_argument('--ecfs_archive_root', type=str, required=True, help='path to ecfs archive root')
    parser.add_argument('-n','--dry',default=False,action='store_true',help='check inputfiles and dump status otherwise also copy/link')
    args = parser.parse_args()

    filelist = parse_file(args.infiles)
    files_on_scratch = find_on_scratch(filelist,args.scratch_archive_root)
    files_on_ecfs = find_on_ecfs(filelist,args.ecfs_archive_root)
    files_local = find_local(filelist)
    filelocs = files_on_ecfs
    for f in filelocs:
        filelocs[f].update(files_on_scratch[f])
        filelocs[f].update(files_local[f])


    if args.dry:
        dump_file_list(filelocs)
    else:
        abort = False
        for f in filelocs:
            if filelocs[f] is None:
                print("Some files are not found")
                abort = True
                break
        if abort:
            dump_file_list(filelocs)
        else:
            prep_files(filelocs)



    
