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

for i in $out1/*$dtg*.grib1cl
do
  echo $i 
  ls -l $i

mars<<EOF
  read, source="$i", fieldset=cw
  compute,fieldset=cw1,formula="max(cw,0.)"
  write, fieldset=cw1, target="${i}on"
EOF

done
exit

