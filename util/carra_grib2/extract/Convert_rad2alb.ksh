#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################


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

