#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################

#export PATH=/tmp/emos/uerra/grib_api/bin:$PATH
#export PYTHONPATH=/tmp/emos/uerra/grib_api/lib/python2.7/site\-packages/
#source /usr/local/apps/module/init/bash

GRIB_DEFINITION_PATH_TMP=$GRIB_DEFINITION_PATH
export GRIB_DEFINITION_PATH=""


#ES test
export ECCODES_DEFINITION_PATH=/usr/local/apps/eccodes/2.12.5/GNU/63/share/eccodes/definitions
module swap gcc/6.3.0
module unload grib_api
module load eccodes
module swap python/2.7.15-01 

#module load python/2.7.15-01
#module load eccodes/2.12.5

dtg=$iy$im$id$ih

#+++++++++++++++++++++++++++++++++++++++++++
# change only this part of script

# setup

for i in $out1/fc_sfc_$dtg*.grib1
do
  echo $i 
  ls -l $i
  j0=$(echo $i | sed s#_sfc_#_soil_#)
  j=${j0}alb
#i="/scratch/ms/no/fab0/carra_grib/fc_sfc_2014030203_001.grib1"
  python $carrabin/convert_rad2alb.py $i $j ${j}on


done

export GRIB_DEFINITION_PATH=$GRIB_DEFINITION_PATH_TMP

exit

