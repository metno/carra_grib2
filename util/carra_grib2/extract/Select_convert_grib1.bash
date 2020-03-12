#!/bin/bash

module load python3

set -ax 

iy=$1
im=$2
id=$3
ih=$4


echo carrabin=$carrabin
echo archvive=$ARCHIVE


time python3 $carrabin/Select.py $iy$im$id$ih --carrabin $carrabin --archive $ARCHIVE
#rm *.rule
mv *grib1* $out1/

time $carrabin/Convert_oro.ksh || exit 1 
time $carrabin/Convert_121.ksh || exit 1
time $carrabin/Convert_sicesnow.ksh || exit 1
time $carrabin/Convert_alb.ksh || exit 1
time $carrabin/Convert_rad2alb.ksh || exit 1
time $carrabin/Convert_cc.ksh || exit 1
time $carrabin/Convert_cwci.ksh || exit 1
time $carrabin/Convert_rh.ksh || exit 1
time $carrabin/Cat_uerra.ksh || exit 1

exit


