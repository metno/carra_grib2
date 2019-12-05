#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################

module swap grib_api/1.16.0 # use default version

set -x

#export PATH=/tmp/emos/uerra/grib_api/bin:$PATH 
#export PYTHONPATH=/tmp/emos/uerra/grib_api/lib/python2.7/site\-packages/

#iy=2014
#im=03
#id=02
#ih=03
#inpdir=/scratch/ms/no/fab0/carra_grib
#out1=/scratch/ms/no/fab0/carra_grib
#bin=.


dtg=$iy$im$id$ih

#+++++++++++++++++++++++++++++++++++++++++++
# change only this part of script

if (( $ih == 0 || $ih == 12 )) ; then
  steps="000 001 002 003 004 005 006 009 012 015 018 021 024 027 030"
else
  steps="000 001 002 003"
fi
#+++++++++++++++++++++++++++++++++++++++++++


select=1
tableVer=16

for step in $steps ; do

  levels="sfc pl ml"
  for level in $levels ; do

    if [[ "$level" == "pl" ]] ; then
      ftype="fp"
      ltype=3
    elif [[ "$level" == "sfc" ]] ; then
      ftype="fp"
      ltype=0
    elif [[ "$level" == "ml" ]] ; then
      ltype=2
      if [[ "$step" == "000" ]] ; then
        ftype="ba"
      else
        ftype="full"
        if [[ "$step" -gt "002" ]] ; then
          continue
        fi
      fi
    fi

    if [[ "$level" == "sfc" ]] ; then
       frules=rulesc.hirlam.convert.sl.batch
    elif [[ "$level" == "pl" ]] ; then
       frules=rulesc.hirlam.convert.pl.batch
    elif [[ "$level" == "ml" ]] ; then
       frules=rulesc.hirlam.convert.ml.batch
    fi

    if [[ "$ftype" == "ba" ]] ; then
      infile=$inpdir"/ba"$dtg"+000grib"
    elif [[ "$ftype" == "full" ]] ; then
      infile=$inpdir"/fc"$dtg"+"$step"grib"
    elif [[ "$ftype" == "fp" ]] ; then
      infile=$inpdir"/fc"$dtg"+"$step"grib_fp"
    elif [[ "$ftype" == "sfx" ]] ; then
      infile=$inpdir"/fc"$dtg"+"$step"grib_sfx"
    fi

    echo $infile  
 
    sed "s|@select@|$select|g ; s|@convert@|$convert|g ; s|@out1@|$out1|g ; s|@out2@|$out2|g ;\
         s|@fileType@|$ftype|g ; s|@out@|$out|g ; s|@tableVer@|$tableVer|g ;\
         s|@step@|$step|g ; s|@dtg@|$dtg|g ; s|@ltype@|$ltype|g "  $carrabin/$frules > rules.batch
 
#    cat rules.batch

    echo "bef grib fil" $ftype $ltype $dtg $step
    grib_filter rules.batch $infile

  done

done

#rm -f *

exit
