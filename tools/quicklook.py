#!/usr/bin/python

import numpy as np
import numpy.ma as ma
import eccodes as ecc
import matplotlib.pyplot as plt
import sys
import argparse


def get_field(fnam,req):
    f = ecc.GribFile(fnam)
    nfound = 0
    msghit = None
    for i in range(len(f)):
        msg = ecc.GribMessage(f)
        matchlist = []
        for key in req:
            if str(msg[key]) == str(req[key]):
                matchlist.append(1)
                continue
            else:
                break
        if len(matchlist) == len(req):
            if msghit:
                print("Ambigous spesification! found more than one match")
                print(req)
                exit(1)
            msghit = msg
            nfound += 1
    if nfound == 0:
        print("No match!")
        print(req)
    nx = msghit['Nx']
    ny = msghit['Ny']
    name = msghit['parameterName']
    val = ma.masked_values(np.flipud(msghit['values'].reshape((ny,nx))),msghit['missingValue'])
    return {'vals':val,'name':name}


def str2dict(string):
    keys = {}
    opts = string.split(',')
    for opt in opts:
        s = opt.split('=')
        keys[s[0]] = s[1]
    return keys


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='take a quicklook on parameter from gribfile')
    parser.add_argument('filename',type=str,help='grib file name file')
    parser.add_argument('-w','--where',type=str,required=True,help='comma separated list of key specifier')
    parser.add_argument('-fd','--filediff',type=str,default=None,help='name of file to compare')
    parser.add_argument('-wd','--wherediff',type=str,default=None,help='specifier to compare')

    args = parser.parse_args()
    fnam = args.filename
    keys = {}
    opts = args.where.split(',')
    keys = str2dict(args.where)

    
    field = get_field(fnam,keys)
    
    if args.filediff or args.wherediff:
        diffile = fnam
        wkeys = keys
        if args.filediff:
            diffile = args.filediff
        if args.wherediff:
            wkeys = str2dict(args.wherediff)
        field2 = get_field(diffile,wkeys)

        x = field['vals'] - field2['vals']
        lim = np.max(np.abs(x))
        plt.imshow(x,cmap="seismic",vmin=-lim,vmax=lim)
        plt.title(field['name'])
        plt.colorbar()
        plt.show()
    else:
        plt.imshow(field['vals'],cmap="jet")
        plt.title(field['name'])
        plt.colorbar()
        plt.show()



