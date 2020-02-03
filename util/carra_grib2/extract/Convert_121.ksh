#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################

set -x

#export PATH=/tmp/emos/uerra/grib_api/bin:$PATH
#export PYTHONPATH=/tmp/emos/uerra/grib_api/lib/python2.7/site\-packages/

dtg=$iy$im$id$ih

#+++++++++++++++++++++++++++++++++++++++++++
# change only this part of script

# setup

for i in $out1/*$dtg*.grib121
do
  echo $i 
  ls  $i

mars<<EOF
  read, source="$i", fieldset=flux
  compute,fieldset=flux1,formula="-1.*flux"
  write, fieldset=flux1, target="${i}on"
EOF

done
exit

