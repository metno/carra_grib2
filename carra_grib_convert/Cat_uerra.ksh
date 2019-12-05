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

cd $out1 || exit

if (( $ih == 0 || $ih == 12 )) ; then
  steps="001 002 003 004 005 006 009 012 015 018 021 024 027 030"
else
  steps="001 002 003"
fi
#+++++++++++++++++++++++++++++++++++++++++++

module swap grib_api/1.16.0 # use default version

select=1
tableVer=16

pwd

types="an fc"
levelout="sfc"

for type in $types ; do

  if [[ "$type" == "an" ]] ; then
    levels="sfc soil ml pl hl"
  else
    levels="sfc soil ml pl hl"
  fi  

  for level in $levels ; do
  echo "now in " $type $level

  if [[ "$type" == "an" ]] ; then

    [[ -f $out2/${type}_${level}_${dtg}.grib1 ]] && rm $out2/${type}_${level}_${dtg}.grib1 

    step=000

    if [[ "$level" == "ml" ]] ; then

     cat ${type}_${level}_${dtg}_${step}.grib1     >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1con  >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1clon >>$out2/${type}_${level}_${dtg}.grib1

    elif [[ "$level" == "sfc" ]] ; then

     cat ${type}_${level}_${dtg}_${step}.grib1      >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1full  >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1oroon >>$out2/${type}_${level}_${dtg}.grib1 
     cat ${type}_${level}_${dtg}_${step}.grib1lsm   >>$out2/${type}_${level}_${dtg}.grib1 
     cat ${type}_${level}_${dtg}_${step}.grib1con   >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1ron   >>$out2/${type}_${level}_${dtg}.grib1
     

    elif [[ "$level" == "soil" ]] ; then

     cat ${type}_${level}_${dtg}_${step}.grib1      >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1sn    >>$out2/${type}_${levelout}_${dtg}.grib1 
     cat ${type}_${level}_${dtg}_${step}.grib1albon >>$out2/${type}_${levelout}_${dtg}.grib1 
    
    elif [[ "$level" == "pl" || "$level" == "hl" ]] ; then

     cat ${type}_${level}_${dtg}_${step}.grib1    >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1ron >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1con >>$out2/${type}_${level}_${dtg}.grib1
     cat ${type}_${level}_${dtg}_${step}.grib1clon >>$out2/${type}_${level}_${dtg}.grib1

    fi

  else

    [[ -f $out2/${type}_${level}_${dtg}.grib1 ]] && rm $out2/${type}_${level}_${dtg}.grib1 

    for step in $steps ; do
     

     if [[ "$level" == "sfc" ]] ; then

      cat ${type}_${level}_${dtg}_${step}.grib1       >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1full  >>$out2/${type}_${level}_${dtg}.grib1
#      cat ${type}_${level}_${dtg}_${step}.grib1evapon >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1con    >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1ron    >>$out2/${type}_${level}_${dtg}.grib1 

     elif [[ "$level" == "pl" ]] ; then

      cat ${type}_${level}_${dtg}_${step}.grib1     >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1con  >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1ron  >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1clon >>$out2/${type}_${level}_${dtg}.grib1 

     elif [[ "$level" == "soil" ]] ; then

      cat ${type}_${level}_${dtg}_${step}.grib1      >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib121on  >>$out2/${type}_${levelout}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1sn    >>$out2/${type}_${levelout}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1albon >>$out2/${type}_${levelout}_${dtg}.grib1 

     elif [[ "$level" == "hl" ]] ; then

      cat ${type}_${level}_${dtg}_${step}.grib1     >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1ron  >>$out2/${type}_${level}_${dtg}.grib1 
      cat ${type}_${level}_${dtg}_${step}.grib1clon >>$out2/${type}_${level}_${dtg}.grib1 

     elif [[ "$level" == "ml" ]] ; then
      cat ${type}_${level}_${dtg}_${step}.grib1 >>$out2/${type}_${level}_${dtg}.grib1
      cat ${type}_${level}_${dtg}_${step}.grib1clon >>$out2/${type}_${level}_${dtg}.grib1
      cat ${type}_${level}_${dtg}_${step}.grib1con  >>$out2/${type}_${level}_${dtg}.grib1

     fi

    done

  fi



  done

done

#rm -f *

exit 0
