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


gfin_alb = ecc.GribFile(infile_alb)
gfin_rad = ecc.GribFile(infile_rad)

print(len(gfin_rad))

stepattern = re.compile('_(\d+).grib1')
m = re.search(stepattern,infile_rad)

#print(m.group(1))

if int(m.group(1)) <= 1:
  deacc = False
else:
  deacc = True
  if int(m.group(1)) <= 6: 
    prev = "_%03d.grib1" % (int(m.group(1)) - 1)
  else:
    prev = "_%03d.grib1" % (int(m.group(1)) - 3)
  infile_rad_prev = stepattern.sub(prev,infile_rad)
  gfin_rad_prev = ecc.GribFile(infile_rad_prev)



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

if deacc:
   for i in range(len(gfin_rad_prev)):
        msg = ecc.GribMessage(gfin_rad_prev)
        if (msg[ikey] == 111):
            ssr_prev = msg['values']
        elif (msg[ikey] == 117):
            ssrd_prev = msg['values']
   ssrd = ssrd - ssrd_prev
   ssr = ssr - ssr_prev


undef = msg2['missingValue']

with np.errstate(divide='ignore', invalid='ignore'):
    al = 1 - np.where(ssrd < 10,np.nan,ssr/ssrd)
    
al *= 100
albedo = np.where(np.isnan(al),undef,al)
albedo = np.where(albedo<0,undef,albedo)


with open(outfile,'w') as test:
    msg2['values'] = albedo
    msg2.write(test)


