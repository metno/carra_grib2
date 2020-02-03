#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################

module swap grib_api/1.16.0 # use default version

set -x
#+++++++++++++++++++++++++++++++++++++++++++

#export PATH=/tmp/emos/uerra/grib_api/bin:$PATH 
#export PYTHONPATH=/tmp/emos/uerra/grib_api/lib/python2.7/site\-packages/

dtg=$iy$im$id$ih

#+++++++++++++++++++++++++++++++++++++++++++
# change only this part of script

steps="001" "002" "003"

select=1
tableVer=16

for step in $steps ; do

  levels="sfc"
  ftype="full"
  ltype=4
  frules=rulez.hirlam.convert.rad.batch

  infile=$inpdir"/fc"$dtg"+"$step"grib_fp"

  echo $infile  
 
  sed "s|@select@|$select|g ; s|@convert@|$convert|g ; s|@out1@|$out1|g ; s|@out2@|$out2|g ;\
       s|@fileType@|$ftype|g ; s|@out@|$out|g ; s|@tableVer@|$tableVer|g ;\
       s|@step@|$step|g ; s|@dtg@|$dtg|g ; s|@ltype@|$ltype|g "  $carrabin/$frules > rules.batch

#    cat rules.batch

  grib_filter rules.batch $infile

done

#rm -f *

exit
