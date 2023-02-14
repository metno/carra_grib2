#!/bin/bash


#module unload eccodes
#module load eccodes/2.25.0
#module load python3/3.6.8-01
#module load python3

module load ecmwf-toolbox/2022.03.0.1
module load python3/3.8.8-01

set -x

dtg=$1
parent_exp=$2
src=$3


date=$dtg

expver="prod"
version=prod


database=marsscratch #mars
MARS_DATABASE=$database
#DOMAIN=$(echo $parent_exp | cut -c1-8)

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

# mars call
mars archive.batch


### verify ###
# count fields
# comapre tree

max_tries=3
k=0
while [ "$k" -lt "$max_tries" ];do
  all_good=0
  rm -rf tree.out cost.out

  if [ "$MARS_DATABASE" == "marsscratch" ]; then
   mars -n -t << EOF
list,
      class      = RR,
      origin     = $origin,
      stream     = oper,
      type       = all,
      DATE       = $date,
      levtype    = all,
      expver     = $version,
      database   = $database,
      target     = tree.out,
      hide       = file/length/offset/id/missing/cost/branch/date/hdate/month/year/time,
      output     = tree

list,
      class      = RR,
      hide       = file/length/offset/id/missing/cost/branch/param/levtype/levelist/expver/type/class/stream/origin/date/time/step/number/hdate/month/year/time,
      target     = cost.out,
      output     = table
EOF

  elif [ "$MARS_DATABASE" == "mars" ];then
    mars -n -t  << EOF
list,
      class      = RR,
      origin     = $origin,
      stream     = oper,
      type       = all,
      DATE       = $date,
      levtype    = all,
      expver     = $version,
      target     = tree.out,
      hide       = file/length/offset/id/missing/cost/branch/date/hdate/month/year/time,
      output     = tree

list,
      class      = RR,
      hide       = file/length/offset/id/missing/cost/branch/param/levtype/levelist/expver/type/class/stream/origin/date/time/step/number/hdate/month/year/time,
      target     = cost.out,
      output     = table
EOF
fi

# ES Skip this step since MFB/ODB files are not constant
#  archived_expected="42008" #1254
#  archived=$(cat cost.out| grep ^Entries|sed s/,//g| sed 's/.*: //')
#  if [[ "$archived" != "$archived_expected" ]] ; then
#    echo "$date: Different number of fields archived than expected: $archived ($archived_expected)! try $k"
#  else
    all_good=$((all_good + 1))
#  fi


#ES: Skip this step since we re-archive
#  tree_ref=$src/carra-${suiteName}-save.tree.reference.out #$bin/carra-${suiteName}-${fclen}.tree.reference.out
#  if [[ $(diff tree.out ${tree_ref}) ]] ; then
#    echo "$date: Different fields archived than expected. Check the reference and current MARS list outputs! try $k"
#  else
    all_good=$((all_good + 1))
#  fi


  if [[ "$all_good" -eq "2" ]]; then
    break
  else
    echo "try #$k"
    sleep 5
  fi

  k=$((k+1))

done

if [[ "$all_good" -eq "2" ]]; then
  echo "Archiving successful"
#  echo "Cleaning.."
#  rm -f an*grib2*
#  rm -f fc*grib2* 
#  rm -f grib_tmp/*
else
  echo "Archive check failed!"
  exit 1
fi


### finish ###
