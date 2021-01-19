#!/bin/bash


module switch eccodes/2.16.0
#module load python3/3.6.8-01
module load python3

dtg=$1
parent_exp=$2
src=$3

date=$dtg

expver="prod"
version=prod


database=marsscratch #mars
MARS_DATABASE=$database
DOMAIN=$(echo $parent_exp | cut -c1-8)  #   CARRA_NE



if [[ "$DOMAIN" == "CARRA_NE" ]]; then
   origin="NO-AR-CE"
   suiteName="no-ar-ce"
elif [[ "$DOMAIN" == "CARRA_SW" || "$DOMAIN" == "IGB" ]];then
   origin="NO-AR-CW"
   suiteName="no-ar-cw"
fi

rm -f archive.batch

for hh in 00 03 06 09 12 15 18 21 ; do
  for typ in an fc ; do
  
    gribfile_in=grib_tmp/$typ.save.$dtg.${hh}00.not_yet.grib1
    gribfile_out=$typ.$dtg.${hh}00.sfc.grib2
    ### convert units ###
    # call python script which replace field
    echo "Convert..."
    python3 $src/converters.py  $gribfile_in
    
    
    ### gribfilter ###
    # grib1-> grib2
    echo "grib_filter..."
    sed -e "s/@type@/$typ/g" $src/rule_save_now.batch > rule.batch
    grib_filter rule.batch $gribfile_in
    echo "grib_set..."
    grib_set "-scentre=enmi,tablesVersion=23,productionStatusOfProcessedData=10,grib2LocalSectionPresent=1,suiteName=$suiteName" $gribfile_out  ${gribfile_out}_final
    rm -f $gribfile_out
    echo "tigge_check..."
    echo NOT REAlly DOING: tigge_check -u -c  ${gribfile_out}_final || exit 1
    echo "make_archive_recuest..."
    python3 $src/make_archive_request.py ${gribfile_out}_final '--database' $database >> archive.batch
    
  done
done

### finish ###
