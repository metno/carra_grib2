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

for i in $out1/*$dtg*.grib1r 
do
  echo $i 
  ls -l $i

mars<<EOF
  read, source="$i", fieldset=r
  compute,fieldset=r1,formula="(r>0.9999)*100+(r<=0.9999)*r*100"
  compute,fieldset=r2,formula="(r1<0.01)*0+(r1>=0.01)*r1"
  write, fieldset=r2, target="${i}on"
EOF

done
exit

