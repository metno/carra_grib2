#!/bin/ksh
set -ex

set -ax 

. header.sh

cd $WRK
WDIR=`hostname`$$
Workdir $WDIR


trap "Trapbody $WDIR ; exit 1" 0



############################################################
# script for HARMONIE PRECISE data processing:
#  - conversion to PRECISE-GRIB2
#  - archiving in MARS
#  - checking what was archived

############################################################
#vvvvvvvv change only this part vvvvvvvvvvvvvvvvvvvvvvvvvvvv

# set up

dtg=$DTG
#dtg=$1
date=$(echo $dtg | cut -c1-8)
hh=$(echo $dtg | cut -c9-10)

# Convert precise fields for given $date, $type and $levtype and write them to $outdir
convert=1
levtypes="sfc pl ml hl soil"
types="an fc"

#levtypes="sfc"
#types="fc"

## Archive all grib2 data in $outdir in one go
## setting archive=0 for testing that things are set up properly
## when running first time, for testing that all is ok...use test env.
## set archive = 1 when all is ok for using it for real...
# for testing purpuse only use next line, as well as version=test, a few lines down...
archive=0
## when done with testing, comment above and use next line (uncomment first)
#archive=1
##        then when all is ok set version=prod also do not forget to 
##  N.B.  comment out use of tigge_check further down in the archiving part, line 101, 102
version=test # MARS expver of PRECISE data for testing
#version=prod # MARS expver of PRECISE data for production

# directory set up
#home=$HM_LIB/carra_grib_convert/archive #/home/ms/no/fab0/carra_grib/grib/archive
bin=$HM_LIB/util/carra_grib_convert/archive # location of script and grib_filter rule files
inpdir=$WRK/carra_grib1 # input hirlam grib1 dir
outdir=$WRK/carra_grib2 # output grib2 dir

# The latest (temporary) version of tigge_check on ecgate with all tunings based on available data
# Once it is tuned properly for all centres it will become part of an official grib-api release
#tigge_check=/tmp/marm/uerra/bin/tigge_check # ecgate!
#tigge_check=~marm/uerra/bin/tigge_check
#tigge_check=tigge_check # default grib-api version

#cd $bin

#^^^^^^^^ change only this part ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
############################################################
#module unload grib_api eccodes
#module load grib_api/1.17.0 # must be used for UERRA!
module load eccodes/new
#grib_info

if [[ "$version" == "prod" ]] ; then
  expver=8
elif [[ "$version" == "test" ]] ; then
  expver=9
fi

rm -f $outdir/*$date*.grib2
if [[ "$convert" == "1" ]] ; then

  for type in $types ; do
    if [[ "$type" == "fc" ]] ; then
      #xlevtypes="$(echo $levtypes|sed 's/ml//g')" # uerra do not have fc/ml data
      xlevtypes=$levtypes
    else
      xlevtypes=$levtypes
    fi
    for levtype in $xlevtypes ; do

      if [[ "$levtype" == "sfc" || "$levtype" == "soil" ]] ; then
        frules=rules.hirlam.convert.sl.batch
      else
        frules=rules.hirlam.convert.vl.batch
      fi

      ls $inpdir/${type}_${levtype}_${date}*.grib1 > flist
 
      cat flist
      sed "s|@outdir@|$outdir|g;s|@version@|$expver|g;s|@type@|$type|g " $bin/$frules > rules.batch

      for f in $(cat flist) ; do
#        grib_info
        grib_filter  rules.batch $f
      done

      if [[ "$levtype" == "soil" ]] ; then
        clevtype="sol"
      else  
        clevtype=$levtype
      fi

      # concatenate all times into one file per day
#      fout=$outdir/$type.${date}.$clevtype.grib2
#      cat $outdir/${type}.${date}.*.${clevtype}.grib2 > $fout
#      rm -rf $outdir/${type}.${date}.*.${clevtype}.grib2

## this can be commented out - for testing, you can optionally activate it...
## E.O. used it for a run or so in the beginning but as it takes extra time, he opted to
## not use it later on.
#      $tigge_check -z -u -w -v $fout > $outdir/tigge_check.$(basename $fout .grib2).out 2>&1
#      echo "error return from tigge_check is " $?

    done
  done

fi

echo stop for now 
exit 0

if [[ "$archive" == "1" ]] ; then

  ###########
  # archive

  ls $outdir/*.${date}.*.grib2 > flist
  for f in $(cat flist) ; do
    ln -fs $f .
  done

  # parse actual date and mars database
  sed "s|\$date|$date|g;s|@version@|$version|g " $bin/archive-hirlam.batch > archive.batch



  # archive it all
#  mars -n archive.batch

  [[ $? != 0 ]] && exit -1

  #########
  # check 

  # Verify that the expected number of fields ($archived_expected) were archived and the MARS field list 
  #   for actual day is the same as the reference one ($tree_ref)

  rm -rf tree.out cost.out

mars -n << EOF
list,
      class      = RR,
      stream     = oper,
      type       = all,
      date       = $date,
      time       = all,
      levtype    = all,
      origin     = enmi,
      expver     = $version,
      target     = tree.out,
      hide       = file/length/offset/id/missing/cost/branch/date/hdate/month/year,
      output     = tree

list,
      class      = RR,
      hide       = file/length/offset/id/missing/cost/branch/param/levtype/levelist/expver/type/class/stream/origin/date/time/step/number/hdate/month/year,
      target     = cost.out,
      output     = table
EOF

  archived_expected=13804
  archived=$(cat cost.out| grep ^Entries|sed s/,//g| sed 's/.*: //')
  if [[ "$archived != "$archived_expected"" ]] ; then
    exit -1
    echo "$date: Different number of fields archived than expected: $archived ($archived_expected)!"
  fi

  tree_ref=$bin/uerra-eswi.tree.reference.out
  if [[ $(diff $tree.out $tree_ref) ]] ; then
    echo "$date: Different fields archived than expected. Check the reference and current MARS list outputs!"
    exit -1
  fi

fi

rm -f flist glist rules.batch mars.batch ifile
rm -f *.grib2

#rm -f $outdir/*
