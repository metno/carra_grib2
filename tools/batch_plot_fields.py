#!/usr/bin/python

import numpy as np
import numpy.ma as ma
import eccodes as ecc
import matplotlib.pyplot as plt
import sys
import argparse
import os
import yaml
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime
import copy
import glob

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


def read_vars(gribfile,params,step=0):
    vars = copy.deepcopy(params)
    f = ecc.GribFile(gribfile)
    for i in range(len(f)):
            msg = ecc.GribMessage(f)
            for param in vars:
                if vars[param]['param']== msg['param'] and msg['step'] == step:
                    print('found',vars[param])
                    vars[param]['msg'] = msg
    for param in vars:
        print
        msghit = vars[param]['msg']
        nx = msghit['Nx']
        ny = msghit['Ny']
        date = msghit['date']
        hour = msghit['hour']
        fcstep = msghit['step']
        lons = msghit['longitudes'].reshape((ny,nx))
        lats = msghit['latitudes'].reshape((ny,nx))
        lat0 = msghit['LaDInDegrees']
        lon0 = msghit['LoVInDegrees']
        lat1 = msghit['Latin1InDegrees']
        lat2 = msghit['Latin2InDegrees']
        val = ma.masked_values(msghit['values'].reshape((ny,nx)),msghit['missingValue'])
        name = msghit['parameterName']
        vars[param]['field'] = val
        dt = datetime.datetime.strptime(str(date)+str(hour),"%Y%m%d%H")
        lons2 = np.where(lons>180,lons-360,lons)
        lon0 = np.where(lon0>180,lon0-360,lon0)
        proj = ccrs.LambertConformal(central_latitude=lat0,
                                 central_longitude=lon0,
                                 standard_parallels=(lat1, lat2))
        vars[param]['misc'] = {'date':dt,
                               'lons':lons2,
                               'lats':lats,
                               'proj':proj,
                               'name':name,
                               'fcstep':fcstep}

    return vars

def mslp_precip(gribfile):
    #parameters
    params = {'mslp':{'param':151},
              'total_precipitation':{'param':228228}
              }
    vars = read_vars(gribfile,params,step=3)
    lons = vars['mslp']['misc']['lons']
    lats = vars['mslp']['misc']['lats']
    proj = vars['mslp']['misc']['proj']
    dt = vars['mslp']['misc']['date']
    fcstep = vars['mslp']['misc']['fcstep']

    # Plotting parameters
    pcontours = np.arange(960,1060,2)
    precip_levels = [0.5,2,4,10,25,50,100,250]
    precip_colors = ['aqua','dodgerblue','blue','m','magenta','darkorange','red']

    # Fields to plot
    mslp = vars['mslp']['field']/100
    precip = vars['total_precipitation']['field']

    fig = plt.figure(figsize=[12,9])
    ax = plt.axes(projection=proj)
    CS = ax.contour(lons,lats,mslp,
                    transform=ccrs.PlateCarree(),
                    levels=pcontours,
                    colors='k',
                    linewidths=[2,1,1,1,1])
    ax.clabel(CS,inline=1,fmt='%d')

    CS2 = ax.contourf(lons,lats,precip,
                      transform=ccrs.PlateCarree(),
                      levels=precip_levels,
                      colors=precip_colors)
    plt.colorbar(CS2,shrink=0.5,orientation='vertical')
    land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                            edgecolor='face',
                                            facecolor=cfeature.COLORS['land'])
    ax.add_feature(land_50m)
    ax.coastlines('50m')
    ax.gridlines()

    plt.title("acc precip and MSLP \n%s UTC + %dh" % (dt.strftime('%Y-%m-%d %H:00'), fcstep))

def t2m_rh2m(gribfile):
    #parameters
    params = {'t2m':{'param':167 },
              'rh2m':{'param':260242}
              }
    gp = list(params.keys())[0]
    print(gp)
    vars = read_vars(gribfile,params,step=0)
    lons = vars[gp]['misc']['lons']
    lats = vars[gp]['misc']['lats']
    proj = vars[gp]['misc']['proj']
    dt = vars[gp]['misc']['date']
    fcstep = vars[gp]['misc']['fcstep']

    # Plotting parameters
    t_colors = ['#ffffff','#e6e6e6','#cccccc','#b3b3b3','#ae99ae','#7a667a','#330066','#590080','#8000ff',
                '#0080ff','#00ccff','#00ffff','#26e699','#66bf26','#bfe626','#ffff80','#ffff00','#ffda00',
                '#ffb000','#ff7300','#ff0000','#cc0000','#80002c','#cc3d6e','#ff00ff','#ff80ff','#ffbfff',
                '#e6cce6','#e6e6e6']
    t_levels = np.array([-80,-70,-60,-52,-48,-44,-40,-36,-32,-28,-24,-20,-16,-12,-8,-4,0,
                4,8,12,16,20,24,28,32,36,40,44,48,52,56])

    # Fields to plot
    t2m = vars['t2m']['field'] - 273.15
    rh2m = vars['rh2m']['field']

    fig = plt.figure(figsize=[12,9])
    ax = plt.axes(projection=proj)

    CS = ax.contourf(lons,lats,t2m,transform=ccrs.PlateCarree(),colors=t_colors,levels=t_levels)
    plt.colorbar(CS,shrink=0.5,orientation='vertical')

#    CS2 = ax.contour(lons,lats,rh2m,transform=ccrs.PlateCarree(),colors='k')

    ax.coastlines('50m')
    ax.gridlines()

    plt.title("Analysed T2M \n%s UTC + %dh" % (dt.strftime('%Y-%m-%d %H:00'), fcstep))


if __name__=='__main__':

  path = sys.argv[1]

  f1 = glob.glob(path+"fc.*.sfc.grib2")
  for f in f1:
      mslp_precip(f)
      plt.show()
      #plt.savefig('mslp_precipitation')

  f2 = glob.glob(path+"an.*.sfc.grib2")
  for f in f2:
      t2m_rh2m(f)
      plt.show()
