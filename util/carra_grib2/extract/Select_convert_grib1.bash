#!/bin/bash

set -ax 

iy=$1
im=$2
id=$3
ih=$4


echo carrabin=$carrabin
echo archvive=$ARCHIVE


time python3 $carrabin/Select.py $iy$im$id$ih --carrabin $carrabin --archive $ARCHIVE || exit 1 
#rm *.rule
mv *grib1* $out1/


time python3 $carrabin/Convert.py --gribdir "$WRK/carra_grib" --cfg "$carrabin/Converters.yml" || exit 1

time $carrabin/Convert_sicesnow.ksh || exit 1
time $carrabin/Convert_rad2alb.ksh || exit 1
time $carrabin/Cat_uerra.ksh || exit 1

exit


