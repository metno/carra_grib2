import sys
import re
import eccodes as ecc
import numpy as np


"""
infile_rad='/scratch/ms/no/fab0/carra_grib/fc_sfc_2014030203_002.grib1'
infile_alb='/scratch/ms/no/fab0/carra_grib/fc_soil_2014030203_002.grib1alb'
outfile='test.grib1alb'

"""

infile_alb = sys.argv[2]
infile_rad = sys.argv[1]
outfile = sys.argv[3]

print("albedo file:",infile_alb)
print("radiation file:",infile_rad)
print("output file:",outfile)

gfin_alb = open(infile_alb)
gfin_rad = open(infile_rad)

stepattern = re.compile('_(\d+).grib1')
m = re.search(stepattern,infile_rad)

if int(m.group(1)) <= 1:
  deacc = False
else:
  deacc = True
  if int(m.group(1)) <= 6: 
    prev = "_%03d.grib1" % (int(m.group(1)) - 1)
  else:
    prev = "_%03d.grib1" % (int(m.group(1)) - 3)
  infile_rad_prev = stepattern.sub(prev,infile_rad)
  gfin_rad_prev = open(infile_rad_prev)


ikey = 'indicatorOfParameter'

while True:
    msg = ecc.codes_grib_new_from_file(gfin_alb)
    if msg is None:
        break
    key = ecc.codes_get_long(msg, ikey)
    if (key == 84):
        msg2 = ecc.codes_clone(msg)
        break

while True:
    msg = ecc.codes_grib_new_from_file(gfin_rad)
    if msg is None:
        break
    key = ecc.codes_get_long(msg, ikey)
    if (key == 111):
        ssr = ecc.codes_get_values(msg)
    elif (key == 117):
        ssrd = ecc.codes_get_values(msg) 

if deacc:
   while True:
        msg = ecc.codes_grib_new_from_file(gfin_rad_prev)
        if msg is None:
            break
        key = ecc.codes_get(msg, ikey)
        if (key == 111):
            ssr_prev = ecc.codes_get_values(msg)
        elif (ecc.codes_get(msg, ikey) == 117):
            ssrd_prev = ecc.codes_get_values(msg)
   ssrd = ssrd - ssrd_prev
   ssr = ssr - ssr_prev


undef = ecc.codes_get(msg2, 'missingValue')

with np.errstate(divide='ignore', invalid='ignore'):
    al = 1 - np.where(ssrd < 10,np.nan,ssr/ssrd)
    
al *= 100
albedo = np.where(np.isnan(al),undef,al)
albedo = np.where(albedo<0,undef,albedo)


with open(outfile,'wb') as test:
    ecc.codes_set_values(msg2, albedo)
    ecc.codes_write(msg2, test)

