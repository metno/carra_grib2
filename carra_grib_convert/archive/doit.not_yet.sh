#!/bin/ksh
set -ex


. header.sh

cd $WRK
WDIR=`hostname`$$
Workdir $WDIR


trap "Trapbody $WDIR ; exit 1" 0



dtg=$DTG
date=$(echo $dtg | cut -c1-8)
hh=$(echo $dtg | cut -c9-10)

# Convert precise fields for given $date, $type and $levtype and write them to $outdir
convert=1
#ES
levtypes="sfc soil"
#levtypes="sfc pl ml hl soil"
types="an fc"

# directory set up
#home=$HM_LIB/carra_grib_convert/archive #/home/ms/no/fab0/carra_grib/grib/archive
bin=$HM_LIB/util/carra_grib2/carra_grib_convert/archive # location of script and grib_filter rule files
inpdir=$WRK/carra_grib1 # input hirlam grib1 dir
outdir=$ARCHIVE # output grib2 dir



#^^^^^^^^ change only this part ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
############################################################
#module unload grib_api eccodes
#module load grib_api/1.17.0 # must be used for UERRA!
#module load eccodes
#grib_info

#ES
echo $ECCODES_DEFINITION_PATH
export ECCODES_DEFINITION_PATH=/usr/local/apps/eccodes/2.12.5/GNU/63/share/eccodes/definitions
GRIB_DEFINITION_PATH_TMP=$GRIB_DEFINITION_PATH
export GRIB_DEFINITION_PATH=""
module swap gcc/6.3.0
module unload grib_api
module load eccodes/new
# End ES


if [[ "$convert" == "1" ]] ; then

  for type in $types ; do
    if [[ "$type" == "fc" ]] ; then
      xlevtypes=$levtypes
    else
      xlevtypes=$levtypes
    fi
    for levtype in $xlevtypes ; do

      if [[ "$levtype" == "sfc" || "$levtype" == "soil" ]] ; then
        frules=rules.notInEccodes.sl.batch
      else
        frules=rules.notInEccodes.vl.batch
      fi

      ls $inpdir/${type}_${levtype}_${date}*.grib1 > flist2
 
      cat flist2
      sed "s|@outdir@|$outdir|g;s|@version@|$expver|g;s|@type@|$type|g " $bin/$frules > rules.batch

      for f in $(cat flist2) ; do
#        grib_info
        grib_filter  rules.batch $f
      done

      if [[ "$levtype" == "soil" ]] ; then
        clevtype="sol"
      else  
        clevtype=$levtype
      fi

    done
  done

fi

trap - 0
#ES
export GRIB_DEFINITION_PATH=$GRIB_DEFINITION_PATH_TMP
exit
