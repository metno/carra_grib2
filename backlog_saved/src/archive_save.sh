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
DOMAIN=$(echo $parent_exp | cut -c1-8)

if [[ "$DOMAIN" == "CARRA_NE" ]]; then
   origin="NO-AR-CE"
   suiteName="no-ar-ce"
elif [[ "$DOMAIN" == "CARRA_SW" || "$DOMAIN" == "IGB" ]];then
   origin="NO-AR-CW"
   suiteName="no-ar-cw"
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
          echo mars  << EOF
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

  archived=$(cat cost.out| grep ^Entries|sed s/,//g| sed 's/.*: //')
  if [[ "$archived" != "$archived_expected" ]] ; then
    echo "$date: Different number of fields archived than expected: $archived ($archived_expected)! try $k"
  else
    all_good=$((all_good + 1))
  fi


  tree_ref=carra-${suiteName}-save.tree.reference.out #$bin/carra-${suiteName}-${fclen}.tree.reference.out
  if [[ $(diff tree.out ${tree_ref}) ]] ; then
    echo "$date: Different fields archived than expected. Check the reference and current MARS list outputs! try $k"
  else
    all_good=$((all_good + 1))
  fi


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
else
  echo "Archive check failed!"
  exit 1
fi


### finish ###
