#!/usr/bin/python

import numpy as np
import numpy.ma as ma
import eccodes as ecc
import matplotlib.pyplot as plt
import sys
import argparse


def get_field(fnam):
    f = ecc.GribFile(fnam)
    nfound = 0
    msghit = None
    for i in range(len(f)):
        msg = ecc.GribMessage(f)
        msghit = msg
        nx = msghit['Nx']
        ny = msghit['Ny']
        units = msghit['units']
        name = msghit['parameterName']
        val = ma.masked_values(np.flipud(msghit['values'].reshape((ny,nx))),msghit['missingValue'])
        field = {'vals':val,'name':name,'units':units}
        pngfile = "%s_l%s_s%s.png" % (msghit["shortName"],msghit["level"],msghit["step"])
        plot_field(field,save=pngfile)


def str2dict(string):
    keys = {}
    opts = string.split(',')
    for opt in opts:
        s = opt.split('=')
        keys[s[0]] = s[1]
    return keys


def plot_field(field,save=None):
    plt.imshow(field['vals'],cmap="jet")
    plt.title(field['name']+"["+field['units']+"]")
    plt.colorbar()
    if save is not None:
        if ".png" == save[-4:]:
            pngfile = save
        else:
            pngfile = save + ".png"
        plt.savefig(pngfile)
        plt.close()
    else:
        plt.show()



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='take a quicklook on parameter from gribfile')
    parser.add_argument('filename',type=str,help='grib file name file')

    args = vars(parser.parse_args())

    get_field(args["filename"])

