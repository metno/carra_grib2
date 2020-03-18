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

with ecc.GribFile(infile_raw_snow) as gfin_raw_snow:
  num_messages = len(gfin_raw_snow)
  for _ in range(num_messages):
    grib_message = ecc.GribMessage(gfin_raw_snow)

    parameter  = grib_message['indicatorOfParameter']
    level_type = grib_message['indicatorOfTypeOfLevel']
    level      = grib_message['level']
    print(parameter,level_type,level)
    if parameter == 13 and level_type == 'sfc' and level == 721:
      out_message = ecc.GribMessage(clone=grib_message)

    if parameter == 13 and level_type == 'sfc' and level in [721, 722, 723]:
      print('Found SWE, layer {}'.format(level))
      raw_data = grib_message['values']
      masked_data = ma.masked_where(raw_data == grib_message['missingValue'], raw_data)

      swe_per_level.append(masked_data)

    if parameter == 191 and level_type == 'sfc' and level in [721, 722, 723]:
      print('Found SR, layer {}'.format(level))
      raw_data = grib_message['values']
      masked_data = ma.masked_where(raw_data == grib_message['missingValue'], raw_data)

      sr_per_level.append(masked_data)

print('Snow depth calculation...')

swe_all_levels = ma.stack(swe_per_level)
sr_all_levels  = ma.stack(sr_per_level)

snow_depth = ma.sum(swe_all_levels/sr_all_levels, axis=0)

print('Generating output GRIB')

if out_message is not None:
  missing_value = out_message['missingValue']
  out_message['values'] = snow_depth.filled(fill_value=missing_value)
  out_message['level']  = 721 # FIXME: correct level?
  out_message['indicatorOfParameter']  = 141 # FIXME: correct parameter id?

  with open(outfile_snow_depth, 'wb') as out_file:
    out_message.write(out_file)

