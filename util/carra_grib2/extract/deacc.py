import eccodes as ecc
import numpy as np
import sys

#infile_rad='/scratch/ms/no/fab0/carra_grib/fc_sfc_2014030203_001.grib1'
#infile_alb='/scratch/ms/no/fab0/carra_grib/fc_soil_2014030203_001.grib1alb'
#outfile='/scratch/ms/no/fab0/carra_grib/test.grib1alb'


infile_alb = sys.argv[2]
infile_rad = sys.argv[1]
outfile = sys.argv[3]


print("albedo file:",infile_alb)
print("radiation file:",infile_rad)
print("output file:",outfile)

gfin_alb = ecc.GribFile(infile_alb)
gfin_rad = ecc.GribFile(infile_rad)

ikey = 'indicatorOfParameter'

for i in range(len(gfin_alb)):
    msg = ecc.GribMessage(gfin_alb)
    if (msg[ikey] == 84):
        msg2 = ecc.GribMessage(clone=msg)
        break

for i in range(len(gfin_rad)):
    msg = ecc.GribMessage(gfin_rad)
    if (msg[ikey] == 111):
        ssr = msg['values']
    elif (msg[ikey] == 117):
        ssrd = msg['values'] 

undef = msg2['missingValue']

with np.errstate(divide='ignore', invalid='ignore'):
    al = 1 - np.where(ssrd < 1e-4,np.nan,ssr/ssrd)
    
al *= 100
albedo = np.where(np.isnan(al),undef,al)
albedo = np.where(albedo<0,undef,albedo)


with open(outfile,'w') as test:
    msg2['values'] = albedo
    msg2.write(test)


