#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################

module swap grib_api/1.16.0 # use default version

set -x

dtg=$iy$im$id$ih

#export PATH=/tmp/emos/uerra/grib_api/bin:$PATH 
#export PYTHONPATH=/tmp/emos/uerra/grib_api/lib/python2.7/site\-packages/

#+++++++++++++++++++++++++++++++++++++++++++
# change only this part of script

select=1
tableVer=16
step=000
level=sfc

(( dataDate=$dtg/100 ))
(( dataTime=$dtg-$dataDate*100 ))
(( dataTime=$dataTime*100 ))

echo $dataDate


ftype="ba"
ltype=2
frules=rulez.hirlam.convert.lsm.batch
infile=$inpdir/ba$dtg+${step}grib

    echo $infile  
 
    sed "s|@select@|$select|g ; s|@convert@|$convert|g ; s|@out1@|$out1|g ;\
         s|@date@|$dataDate|g ;\
         s|@fileType@|$ftype|g ; s|@time@|$dataTime|g ; s|@tableVer@|$tableVer|g ;\
         s|@step@|$step|g ; s|@dtg@|$dtg|g ; s|@ltype@|$ltype|g "  $carrabin/$frules > rules.batch

#    cat rules.batch

    grib_filter rules.batch $infile

#rm -f *

exit
