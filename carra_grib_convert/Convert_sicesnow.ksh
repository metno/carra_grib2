#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################

set -x


GRIB_DEFINITION_PATH_TMP=$GRIB_DEFINITION_PATH
export GRIB_DEFINITION_PATH=""

#export PATH=/tmp/emos/uerra/grib_api/bin:$PATH
#export PYTHONPATH=/tmp/emos/uerra/grib_api/lib/python2.7/site\-packages/
export ECCODES_DEFINITION_PATH=/usr/local/apps/eccodes/2.12.5/GNU/63/share/eccodes/definitions

module swap gcc/6.3.0
#module load gcc/6.3.0
module unload grib_api
module load eccodes
module swap python/2.7.15-01
#module load python/2.7.15-01



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

