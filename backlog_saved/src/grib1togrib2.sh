#!/bin/bash


module switch eccodes/2.21.0
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
#DOMAIN=$(echo $parent_exp | cut -c1-8)  #   CARRA_NE

if [[ $parent_exp == *"NE"* ]]; then
   origin="NO-AR-CE"
   suiteName="no-ar-ce"
elif [[ $parent_exp == *"IGB"* ]];then
   origin="NO-AR-CW"
   suiteName="no-ar-cw"
else
   echo "Unrecognized parent_exp: " $parent_exp
   exit 1 
fi

rm -f archive.batch

for hh in 00 03 06 09 12 15 18 21 ; do
#for hh in 03 ; do

  for typ in an fc ; do
  
    gribfile_in_sfx=grib_tmp/fc$dtg${hh}+000grib_sfx
    gribfile_in=grib_tmp/$typ.save.$dtg.${hh}00.not_yet.grib1
    gribfile_out=$typ.$dtg.${hh}00.sfc.grib2
    gribfile_out_sol=$typ.$dtg.${hh}00.sol.grib2

   
    ### convert units ###
    # call python script which replace field (unit e.g. ; not grib1-grib2 here)
    echo "Convert..."
    python3 $src/converters.py  $gribfile_in tmp.grib && mv tmp.grib $gribfile_in || exit 1
    python3 $src/converters.py  $gribfile_in_sfx tmp_sfx.grib && mv tmp_sfx.grib $gribfile_in_sfx || exit 1
    
    
    ### gribfilter ###
    # grib1-> grib2
    echo "grib_filter..."
    sed -e "s/@type@/$typ/g" $src/rule_save_now.batch > rule.batch
    sed -e "s/@type@/$typ/g" $src/rule_save_now_sfx.batch > rule_sfx.batch
    sed -e "s/@type@/$typ/g" $src/rule_save_now_sol.batch > rule_sol.batch


    grib_filter rule.batch $gribfile_in
    if [[ "$typ" == "an" ]]; then  #Backup analysis file, and add extra parameters from sfx file
      grib_filter rule_sfx.batch $gribfile_in_sfx  # Add extra parameters from sfx file

      #Backup analysis file
      if [[ "$suiteName" == "no-ar-cw" ]]; then 
        cp $gribfile_in /scratch/ms/no/fa0e/carra_backup/IGB/${dtg:0:4}/
      else 
        cp $gribfile_in /scratch/ms/no/fa0e/carra_backup/NE/${dtg:0:4}/
      fi

    fi
    grib_filter rule_sol.batch $gribfile_in


    echo "grib_set..." 
    for outfile in $gribfile_out $gribfile_out_sol; do
      grib_set "-scentre=enmi,tablesVersion=23,productionStatusOfProcessedData=10,grib2LocalSectionPresent=1,suiteName=$suiteName" $outfile ${outfile}_final
      #rm -f $outfile
      echo "tigge_check..."
      tigge_check -u -c  ${outfile}_final > ${outfile}_tigge_check_dump #|| exit 1
      echo "make_archive_request..."
      python3 $src/make_archive_request.py ${outfile}_final '--database' $database >> archive.batch
    done
  done
done

### finish ###
