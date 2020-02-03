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

for i in $out1/*$dtg*.grib1alb
do
  echo $i 
  ls -l $i

mars<<EOF
  read, source="$i", fieldset=al
  compute,fieldset=al1,formula="(al>0.9999)*100+(al<=0.9999)*al*100"
  compute,fieldset=al2,formula="(al1<0.01)*0+(al1>=0.01)*al1"
  write, fieldset=al2, target="${i}on"
EOF

done
exit

