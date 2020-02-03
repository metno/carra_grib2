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

for i in $out1/*$dtg*.grib1c 
do
  echo $i 
  ls -l $i

mars<<EOF
  read, source="$i", fieldset=tcc
  compute,fieldset=tcc1,formula="(tcc>0.9999)*100+(tcc<=0.9999)*tcc*100"
  compute,fieldset=tcc2,formula="(tcc1<0.01)*0+(tcc1>=0.01)*tcc1"
  write, fieldset=tcc2, target="${i}on"
EOF

done
exit

