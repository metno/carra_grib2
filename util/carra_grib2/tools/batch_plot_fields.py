#!/usr/bin/env python3

import numpy as np
import numpy.ma as ma
import xarray as xr
import matplotlib
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import argparse
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime
import copy
import glob
import pyproj
#import eccodes as ecc
import metview as mv


def str2dict(string):
    keys = {}
    opts = string.split(',')
    for opt in opts:
        s = opt.split('=')
        keys[s[0]] = s[1]
    return keys


def read_vars(gribfile,params,step=0):
    raise NotImplementedError
    ds = {}
    vars = copy.deepcopy(params)
    f = ecc.GribFile(gribfile)
    for i in range(len(f)):
        msg = ecc.GribMessage(f)
        for param in vars:
            if vars[param]['param']== msg['param'] and msg['step'] == step:
                print('found',vars[param])
                vars[param]['msg'] = msg
    for param in vars:
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
        ds['misc'] = {'date':dt,
                      'lons':lons2,
                      'lats':lats,
                      'proj':proj,
                      'fcstep':fcstep}
        ds['params'] = vars

    return ds


def request_vars(params, dt, type_='an', step=0, origin='no-ar-ce', database=None):
    ds = {}
    vars = copy.deepcopy(params)
    paramlist = [vars[param]['param'] for param in vars]
    ret = mv.retrieve(type=type_,
                      levtype='sfc',
                      param=paramlist,
                      date=dt.strftime("%Y-%m-%d"),
                      expver='prod',
                      origin=origin,
                      class_='rr',
                      time=dt.strftime("%H"),
                      database=database,
                      stream='oper',
                      step=step)
    
    x = xr.merge([ret[i].to_dataset() for i in range(len(ret))], compat="override")
    attrs = x.variables[list(vars.keys())[0]].attrs
    
    lons = x.longitude.values
    lats = x.latitude.values
    
    if attrs['GRIB_gridType'] == 'polar_stereographic':
        proj = ccrs.Stereographic(
            central_longitude=-30,
            central_latitude =90.0,
            true_scale_latitude=90.0)
        lons2 = lons
    else:
        lon0 = attrs['GRIB_LoVInDegrees']
        lat0 = attrs['GRIB_LaDInDegrees']
        lat1 = attrs['GRIB_Latin1InDegrees']
        lat2 = attrs['GRIB_Latin2InDegrees']
        
        lons2 = np.where(lons>180,lons-360,lons)
        lon0 = np.where(lon0>180,lon0-360,lon0)
        proj = ccrs.LambertConformal(central_latitude=lat0,
                                 central_longitude=lon0,
                                 standard_parallels=(lat1, lat2))
        
    ds['misc'] = {'date':dt,
                  'lons':lons2,
                  'lats':lats,
                  'proj':proj,
                  'fcstep':step}
    
    for param in vars:
        missVal = x.variables[param].attrs['GRIB_missingValue']
        val = ma.masked_values(x.variables[param].values,missVal)
        vars[param]['field'] = val
    ds['params'] = vars
    return ds


def mslp_precip(ds):
    params = {'msl':{'param':151},
              'tp':{'param':228228}
              }
    lons = ds['misc']['lons']
    lats = ds['misc']['lats']
    proj = ds['misc']['proj']
    dt = ds['misc']['date']
    fcstep = ds['misc']['fcstep']
    PRJ = pyproj.Proj(proj.proj4_init)

    # Plotting parameters
    pcontours = np.arange(960,1060,5)
    precip_levels = [0.5,2,4,10,25,50,100,250]
    precip_colors = ['aqua','dodgerblue','blue','m','magenta','darkorange','red']

    # Fields to plot
    mslp = ds['params']['msl']['field']/100
    precip = ma.masked_values(ds['params']['tp']['field'], 0)
    x, y = PRJ(lons, lats)

    fig, ax = plt.subplots(figsize=[12,9],edgecolor='k',subplot_kw=dict(projection=proj))
    CS = ax.contour(x, y, mslp,
                    transform=proj,
                    levels=pcontours,
                    colors='k',
                    zorder=3,
                    linewidths=[2,1])
    ax.clabel(CS,inline=1,fmt='%d')

    CS2 = ax.contourf(x, y, precip,
                      transform=proj,
                      levels=precip_levels,
                      colors=precip_colors,
                      zorder=2,
                      alpha=0.9)
    plt.colorbar(CS2,shrink=0.5,orientation='vertical')
    land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                            edgecolor='face',
                                            facecolor=cfeature.COLORS['land'])
    ax.add_feature(land_50m)
    ax.coastlines('50m')
    ax.gridlines()
    plt.title("acc precip and MSLP \n%s UTC + %dh" % (dt.strftime('%Y-%m-%d %H:00'), fcstep))       


def t2m_rh2m(ds):
    lons = ds['misc']['lons']
    lats = ds['misc']['lats']
    proj = ds['misc']['proj']
    dt = ds['misc']['date']
    fcstep = ds['misc']['fcstep']

    # Plotting parameters
    t_colors = ['#ffffff','#e6e6e6','#cccccc','#b3b3b3','#ae99ae','#7a667a','#330066','#590080','#8000ff',
                '#0080ff','#00ccff','#00ffff','#26e699','#66bf26','#bfe626','#ffff80','#ffff00','#ffda00',
                '#ffb000','#ff7300','#ff0000','#cc0000','#80002c','#cc3d6e','#ff00ff','#ff80ff','#ffbfff',
                '#e6cce6','#e6e6e6']
    t_levels = np.array([-80,-70,-60,-52,-48,-44,-40,-36,-32,-28,-24,-20,-16,-12,-8,-4,0,
                4,8,12,16,20,24,28,32,36,40,44,48,52,56])

    # Fields to plot
    t2m = ds['params']['t2m']['field'] - 273.15
    PRJ = pyproj.Proj(proj.proj4_init)
    x, y = PRJ(lons, lats)
    fig = plt.figure(figsize=[12,9])
    ax = plt.axes(projection=proj)

    CS = ax.contourf(x, y, t2m, transform=proj, colors=t_colors, levels=t_levels)
    plt.colorbar(CS,shrink=0.5,orientation='vertical')
    ax.coastlines('50m')
    ax.gridlines()
    plt.title("Analysed T2M \n%s UTC + %dh" % (dt.strftime('%Y-%m-%d %H:00'), fcstep))


def wind_vel(ds):
    u = ds['params']['u10']['field']
    v = ds['params']['v10']['field']
    lons = ds['misc']['lons']
    lats = ds['misc']['lats']
    proj = ds['misc']['proj']
    dt = ds['misc']['date']
    fcstep = ds['misc']['fcstep']#
    PRJ = pyproj.Proj(proj.proj4_init)
    x, y = PRJ(lons, lats)
    wind_speed = np.sqrt(u**2 + v**2)
    ws_levels = [5,10,15,20,25,30,40,50]
    jet = matplotlib.colormaps["jet"]
    newcolors = jet(np.linspace(0, 1, 256))
    white = np.array([1,1,1,1])
    lightgrey = np.array([200/256,200/256,200/256,1])
    darkgrey = np.array([100/256,100/256,100/256,1])
    newcolors[0:5, :] = white
    newcolors[5:19, :] = lightgrey
    newcolors[19:38, :] = darkgrey
    newcmp = ListedColormap(newcolors)
    ny,nx = lons.shape
    step = 75
    sx = slice(0, nx, step)
    sy = slice(0, ny, step)
    fig = plt.figure(figsize=[12,9],edgecolor='k')
    ax = plt.axes(projection=proj)
    CS = ax.quiver(x[sy,sx], y[sy,sx],
                   u[sy,sx], v[sy,sx],
                   scale=300,
                   transform=proj,
                   zorder=3)
    CS2 = ax.pcolormesh(x,y,wind_speed,
                      transform=proj,
                      cmap=newcmp,
                      vmin=0,
                      vmax=40,
                      zorder=1,
                      alpha=0.9)
    plt.colorbar(CS2,shrink=0.5,orientation='vertical')
    ax.coastlines('50m',zorder=2)
    ax.gridlines()
    plt.title("Wind velocity \n%s UTC + %dh" % (dt.strftime('%Y-%m-%d %H:00'), fcstep))


def swe(ds):
    lons = ds['misc']['lons']
    lats = ds['misc']['lats']
    proj = ds['misc']['proj']
    dt = ds['misc']['date']
    fcstep = ds['misc']['fcstep']
    # Fields to plot
    swe = ds['params']['sd']['field']
    PRJ = pyproj.Proj(proj.proj4_init)
    x, y = PRJ(lons, lats)
    fig = plt.figure(figsize=[12,9])
    ax = plt.axes(projection=proj)
    ax.set_facecolor('lightgrey')
    CS = ax.pcolormesh(x, y, swe,
                      transform=proj,
                      cmap='bone',
                      vmin=0,
                      vmax=300,
                      zorder=1,
                      alpha=0.9)
    plt.colorbar(CS, shrink=0.5, orientation='vertical')
    ax.coastlines('50m')
    ax.gridlines()
    plt.title("Analysed SWE \n%s UTC + %dh" % (dt.strftime('%Y-%m-%d %H:00'), fcstep))



def from_path(path):
    params = {'msl':{'param':151},
              'tp':{'param':228228}
              }
    f1 = glob.glob(path+"/fc.*.sfc.grib2")
    print(f1)
    for f in f1:
        ds = read_vars(f,params,step=3)
        mslp_precip(ds)
        plt.show()
        #plt.savefig('mslp_precipitation')
    f2 = glob.glob(path+"an.*.sfc.grib2")
    params = {'t2':{'param':167 }}
    for f in f2:
        ds = read_vars(f,params,step=3)
        t2m_rh2m(ds)
        plt.show()


def from_mars(dt, origin, database=None, figures=None):
    if figures is None:
        figures = ['mslp', 't2m', 'wind', 'swe']

    if 'mslp' in figures:
        # mslp + precip
        params = {'msl':{'param':151},
                  'tp':{'param':228228}
                  }
        ds = request_vars(params, dt, type_='fc', origin=origin, step=3, database=database)
        mslp_precip(ds)
        plt.savefig('mslp_precip_%s_%s_%d.png' % (origin, dt.strftime("%Y%m%d%H"),3))
        plt.close()
    
    if 't2m' in figures:
        # t2m analysis
        params = {'t2m':{'param':167 }} 
        ds = request_vars(params, dt, type_='an', origin=origin, step=0, database=database)
        t2m_rh2m(ds)
        plt.savefig('t2m_analysis_%s_%s.png' % (origin, dt.strftime("%Y%m%d%H")))
        plt.close()
    
    if 'wind' in figures:
        # wind
        params = {'u10': {'param':165},
                  'v10': {'param':166}}
        ds = request_vars(params, dt, type_='fc', origin=origin, step=3, database=database)
        wind_vel(ds)
        plt.savefig('wind_%s_%s.png' % (origin, dt.strftime("%Y%m%d%H")))
        plt.close()
    
    if 'swe' in figures:
        # Snow
        params = {'sd': {'param':228141}}
        ds = request_vars(params, dt, type_='an', origin=origin, step=0, database=database)
        swe(ds)
        plt.savefig('SWE_%s_%s.png' % (origin, dt.strftime("%Y%m%d%H")))
        plt.close()


if __name__=='__main__':


    use_example = '''
Examples:

  ./batch_plot_fields.py --dtg 2020121706

'''
    parser = argparse.ArgumentParser(description='make wheather maps',
                                     epilog=use_example,
                                     formatter_class=argparse.RawDescriptionHelpFormatter
                                     )
    parser.add_argument('--dtg', type=str, required=True, help='yyyymmddhh')
    parser.add_argument('--source', type=str, default='mars', help='mars or path/to/grib2files/')
    parser.add_argument('--origin', type=str, default='no-ar-pa', help="DOMAIN: no-ar-ce, no-ar-cw, no-ar-pa")
    parser.add_argument('--database', type=str, default=None, help="database")
    parser.add_argument('--figures', type=str, default=None, help='mslp,t2m,wind,swe')
    
    args = parser.parse_args()    
    dt = datetime.datetime.strptime(args.dtg,"%Y%m%d%H")
    figs = None

    if args.figures is not None:
        figs = args.figures.split(',')

    if args.source == 'mars':
        from_mars(dt, args.origin, database=args.database, figures=figs)

