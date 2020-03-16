import eccodes as ecc
import numpy as np
import numpy.ma as ma
import yaml
import glob
import time
import multiprocessing as mp
import matplotlib.pyplot as plt


def compare_file(gf_their,gf_my):

    with ecc.GribFile(gf_their) as tf, ecc.GribFile(gf_my) as mf:
        if len(tf) != len(mf):
            print("different length!")
            raise Exception
        for i in range(len(tf)):
            tmsg = ecc.GribMessage(tf)
            mmsg = ecc.GribMessage(mf)
            nx = tmsg['Nx']
            ny = tmsg['Ny']
            tv = tmsg['values'].reshape((ny,nx))
            mv = mmsg['values'].reshape((ny,nx))
            if 0 in mv:
                denom = 1
            else:
                denom = mv
            plt.imshow((mv - tv)/denom)
            plt.colorbar()
            plt.title("%f - %f" % ((mv-tv).min(),(mv-tv).max()))
            plt.savefig(gf_my+'.png')
            plt.close()


if __name__ == "__main__":
    files = glob.glob('*grib1*on')
    for f in files:
        print(f)
        compare_file('target/'+f,f)