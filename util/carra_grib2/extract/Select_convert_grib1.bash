#!/bin/bash

module load python3

set -ax 

iy=$1
im=$2
id=$3
ih=$4


echo carrabin=$carrabin
echo archvive=$ARCHIVE


python3 $carrabin/Select.py $iy$im$id$ih --carrabin $carrabin --archive $ARCHIVE
rm *.rule


$carrabin/Convert_oro.ksh || exit 1 
$carrabin/Convert_121.ksh || exit 1
$carrabin/Convert_sicesnow.ksh || exit 1
$carrabin/Convert_alb.ksh || exit 1
$carrabin/Convert_rad2alb.ksh || exit 1
$carrabin/Convert_cc.ksh || exit 1
$carrabin/Convert_cwci.ksh || exit 1
$carrabin/Convert_rh.ksh || exit 1
$carrabin/Cat_uerra.ksh || exit 1

exit


