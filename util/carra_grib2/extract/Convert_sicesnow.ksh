#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################

set -x





dtg=$iy$im$id$ih

#+++++++++++++++++++++++++++++++++++++++++++
# change only this part of script

# setup

for i in $out1/*$dtg*.grib1sicesnow
do
  echo $i 
  ls -l $i
  python $carrabin/convert_sicesnow.py $i ${i}depth

done

export GRIB_DEFINITION_PATH=$GRIB_DEFINITION_PATH_TMP
exit

