import sys
import eccodes as ecc
import numpy as np
import numpy.ma as ma


"""
infile_raw_snow='/scratch/ms/no/fab0/carra_grib/fc_sfc_2014030203_002.grib1'
outfile_snow_depth='test.grib1alb'

"""

infile_raw_snow       = sys.argv[1]
outfile_snow_depth    = sys.argv[2]

print("SWE/SR input file:",   infile_raw_snow)
print("SD output file:",      outfile_snow_depth)

ikey = 'indicatorOfParameter' # 13, 191
ikey = 'indicatorOfTypeOfLevel' # sfc
ikey = 'level' # 721,722,723

swe_per_level = []
sr_per_level  = []
out_message   = None

with open(infile_raw_snow) as gfin_raw_snow:
    while True:
        grib_message = ecc.codes_grib_new_from_file(gfin_raw_snow)
        if  grib_message is None:
            break
        parameter  = ecc.codes_get(grib_message, 'indicatorOfParameter')
        level_type = ecc.codes_get(grib_message, 'indicatorOfTypeOfLevel')
        level      = ecc.codes_get(grib_message, 'level')
        print(parameter,level_type,level)
        if parameter == 13 and level_type == 'sfc' and level == 721:
            out_message = ecc.codes_clone(grib_message)
  
        if parameter == 13 and level_type == 'sfc' and level in [721, 722, 723]:
            print('Found SWE, layer {}'.format(level))
            raw_data = ecc.codes_get_values(grib_message)
            missval = ecc.codes_get(grib_message, 'missingValue')
            masked_data = ma.masked_where(raw_data == missval, raw_data)
   
            swe_per_level.append(masked_data)
        if parameter == 191 and level_type == 'sfc' and level in [721, 722, 723]:
            print('Found SR, layer {}'.format(level))
            raw_data = ecc.codes_get_values(grib_message)
            masked_data = ma.masked_where(raw_data == missval, raw_data)
  
            sr_per_level.append(masked_data)
  

print('Snow depth calculation...')

swe_all_levels = ma.stack(swe_per_level)
sr_all_levels  = ma.stack(sr_per_level)

snow_depth = ma.sum(swe_all_levels/sr_all_levels, axis=0)

print('Generating output GRIB')

if out_message is not None:
  missing_value = missval
  ecc.codes_set_values(out_message, snow_depth.filled(fill_value=missing_value))
  ecc.codes_set(out_message, "level", 721)
  ecc.codes_set(out_message, "indicatorOfParameter", 141)

  with open(outfile_snow_depth, 'wb') as out_file:
    ecc.codes_write(out_message, out_file)

