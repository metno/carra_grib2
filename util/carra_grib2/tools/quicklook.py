import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import argparse
import xarray as xr
import copy
import datetime
import eccodes as ecc
import metview as mv


def get_field(fnam, req):
    with open(fnam) as f:
        nfound = 0
        msghit = None
        tmp = []
        while True:
            msg = ecc.codes_grib_new_from_file(f)
            if msg is None:
                break
            matchlist = []
            for key in req:
                mval = ecc.codes_get(msg, key)
                tmp += [mval]
                if str(mval) == str(req[key]):
                    matchlist.append(1)
                    continue
                else:
                    break
            if len(matchlist) == len(req):
                if msghit:
                    print('Ambigous spesification! found more than one match')
                    print(req)
                    exit(1)
                msghit = ecc.codes_clone(msg)
                nfound += 1
                break
        if nfound == 0:
            print('No match!')
            print(req)
            print(tmp)
        nx = ecc.codes_get(msghit, 'Nx')
        ny = ecc.codes_get(msghit, 'Ny')
        name = ecc.codes_get(msghit, 'parameterName')
        val = ma.masked_values(ecc.codes_get_values(msghit).reshape((ny,nx)), ecc.codes_get(msghit, 'missingValue'))
        return {'vals':val,'name':name}


def request_vars(params, dt, type_='an', step=0, origin='no-ar-ce', database=None):
    ds = {}
    vars = copy.deepcopy(params)
    paramlist = [vars[param] for param in vars]
    ret = mv.retrieve(type=type_,
                      levtype='sfc',
                      param=paramlist,
                      date=dt.strftime('%Y-%m-%d'),
                      expver='prod',
                      origin=origin,
                      class_='rr',
                      time=dt.strftime('%H'),
                      database=database,
                      stream='oper',
                      step=step)
    
    x = ret.to_dataset()
    param = list(x.data_vars)[0]
    attrs = x.variables[param].attrs
    lons = x.longitude.values
    lats = x.latitude.values
        
    ds['misc'] = {'date':dt,
                  #'lons':lons2,
                  #'lats':lats,
                  #'proj':proj,
                  'attrs':attrs,
                  'fcstep':step}
    
    missVal = x.variables[param].attrs['GRIB_missingValue']
    val = ma.masked_values(x.variables[param].values,missVal)
    ds['params'] = {param: {'field': val}}
    return {'vals':val,'name':param}
    

def str2dict(string):
    keys = {}
    opts = string.split(',')
    for opt in opts:
        s = opt.split('=')
        keys[s[0]] = s[1]
    return keys


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='take a quicklook on parameter from gribfile')
    parser.add_argument('filename', type=str, help='grib file name file')
    parser.add_argument('-w','--where', type=str, required=True, help='comma separated list of key specifier')
    parser.add_argument('-fd','--filediff', type=str, default=None, help='name of file to compare')
    parser.add_argument('-wd','--wherediff', type=str, default=None, help='specifier to compare')

    args = parser.parse_args()
    fnam = args.filename
    keys = {}
    opts = args.where.split(',')
    keys = str2dict(args.where)


    if fnam in [f'no-ar-{id}' for id in ['cw', 'ce', 'pa']]:
        try:
            dt = datetime.datetime.strptime(keys['dtg'], '%Y%m%d%H')
            type_ = 'an'
            step = 0
            if 'type' in keys:
                type_ = keys['type']
            if 'step' in keys:
                step = keys['step']
            field = request_vars({'param': keys['param']}, dt, type_=type_, step=step, origin=fnam)
        except Exception as e:
            raise e
    else:
        field = get_field(fnam, keys)
    
    if args.filediff or args.wherediff:
        # TODO mars source
        diffile = fnam
        wkeys = keys
        if args.filediff:
            diffile = args.filediff
        if args.wherediff:
            wkeys = str2dict(args.wherediff)
        field2 = get_field(diffile,wkeys)

        x = field['vals'] - field2['vals']
        lim = np.max(np.abs(x))
        plt.imshow(x, cmap='seismic',vmin=-lim,vmax=lim, origin='lower')
        plt.title(field['name'])
        plt.colorbar()
        plt.ylim((0,field['vals'].shape[0]))
        plt.show()
    else:
        plt.imshow(field['vals'],cmap='jet', origin='lower')
        plt.title(field['name'])
        plt.colorbar()
        plt.ylim((0,field['vals'].shape[0]))
        plt.show()

