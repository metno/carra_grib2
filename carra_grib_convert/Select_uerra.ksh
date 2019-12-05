#!/bin/ksh

#######################################################
# script for selection of hirlam fields for uerra
# use grib-api 1.15.0 or higher!
#######################################################

module swap grib_api/1.16.0 # use default version


set -x

#export PATH=/tmp/emos/uerra/grib_api/bin:$PATH 
#export PYTHONPATH=/tmp/emos/uerra/grib_api/lib/python2.7/site\-packages/


dtg=$iy$im$id$ih


#+++++++++++++++++++++++++++++++++++++++++++
# change only this part of script

# setup

if (( $ih == 0 || $ih == 12 )) ; then
  steps="000 001 002 003 004 005 006 009 012 015 018 021 024 027 030"
else
  steps="000 001 002 003"
fi
#+++++++++++++++++++++++++++++++++++++++++++

select=1
tableVer=16

typeset -i estep
typeset -i fstep

for step in $steps ; do

  if [[ "$step" == "000" ]] ; then
    levels="sfc soil ml pl hl"
    fstep=0
    estep=0
  else
    if (( $step <= 2 )); then
      levels="sfc soil ml pl hl"
    else
      levels="sfc soil pl hl"
    fi
    if (( $step <= 6 )) ; then
      estep=estep+1
      (( fstep=estep-1 ))
    else
      estep=estep+3
      (( fstep=estep-3 ))
    fi
  fi  

  echo $fstep $estep

  for level in $levels ; do

    if [[ "$level" == "ml" ]] ; then
      if [[ "$step" == "000" ]]; then
        ftype="ba"
      else
        ftype="full"
      fi
      ltype=2
    elif [[ "$level" == "hl" ]] ; then
      ftype="fp"
      ltype=4
    elif [[ "$level" == "pl" ]] ; then
      ftype="fp"
      ltype=3
    elif [[ "$level" == "sfc" ]] ; then
      ftype="fp"
      ltype=0
    elif [[ "$level" == "soil" ]] ; then
      ftype="sfx"
      ltype=4
    fi

    if [[ "$level" == "sfc" ]] ; then
       frules=rulez.hirlam.convert.sl.batch
    elif [[ "$level" == "hl" ]] ; then
       if [[ "$step" == "000" ]] ; then
          frules=rulez.hirlam.convert.hlana.batch
       else 
          frules=rulez.hirlam.convert.hl.batch
       fi
    elif [[ "$level" == "pl" ]] ; then
       frules=rulez.hirlam.convert.pl.batch
    elif [[ "$level" == "ml" ]] ; then
       frules=rulez.hirlam.convert.ml.batch
    elif [[ "$level" == "soil" ]] ; then
       frules=rulez.hirlam.convert.soil.batch
    fi

    if [[ "$ftype" == "ba" ]] ; then
      infile=$inpdir"/ba"$dtg"+000grib"
    elif [[ "$ftype" == "full" ]]; then
      infile=$inpdir"/fc"$dtg"+"$step"grib"
      ftype="fc"
    elif [[ "$ftype" == "fp" ]] ; then
      infile=$inpdir"/fc"$dtg"+"$step"grib_fp"
    elif [[ "$ftype" == "sfx" ]] ; then
      infile=$inpdir"/fc"$dtg"+"$step"grib_sfx"
    fi

    echo $infile  
 
    sed "s|@select@|$select|g ; s|@convert@|$convert|g ; s|@out1@|$out1|g ; s|@out2@|$out2|g ;\
         s|@fileType@|$ftype|g ; s|@out@|$out|g ; s|@tableVer@|$tableVer|g ;\
         s|@fstep@|$fstep|g ;s|@step@|$step|g ; s|@dtg@|$dtg|g ;\
         s|@ltype@|$ltype|g "  $carrabin/$frules > rules.batch

#    cat rules.batch

    grib_filter rules.batch $infile || exit 1

  done

done

#rm -f *

exit
