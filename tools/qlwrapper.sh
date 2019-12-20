#!/bin/bash


module unload eccodes
module load eccodes/2.15.0
module load python3/3.6.8-01

python3 /home/ms/no/fab0/hm_home/carra_grib_convert2_SW/util/carra_grib2/tools/quicklook.py "$@"
