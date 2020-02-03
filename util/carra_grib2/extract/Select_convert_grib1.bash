#!/bin/bash

set -ax 

iy=$1
im=$2
id=$3
ih=$4


echo carrabin= $carrabin


$carrabin/Select_uerra.ksh || exit 1

$carrabin/Select_uerra_canari.ksh || exit 1

$carrabin/Select_uerra_full.ksh || exit 1

$carrabin/Select_uerra_oro.ksh || exit 1 
$carrabin/Convert_oro.ksh || exit 1 


$carrabin/Select_uerra_lsm.ksh || exit 1
#########################./Convert_lsm.ksh  || exit 1

##########################./Select_uerra_evap.ksh
###########################./Convert_evap.ksh

$carrabin/Select_uerra_121.ksh || exit 1
$carrabin/Convert_121.ksh || exit 1

$carrabin/Select_uerra_sn.ksh || exit 1

$carrabin/Select_uerra_sicesnow.ksh || exit 1
$carrabin/Convert_sicesnow.ksh || exit 1

$carrabin/Select_uerra_alb.ksh || exit 1
$carrabin/Convert_alb.ksh || exit 1

$carrabin/Select_uerra_rad.ksh || exit 1
$carrabin/Convert_rad2alb.ksh || exit 1

$carrabin/Select_uerra_clcv.ksh || exit 1
$carrabin/Convert_cc.ksh || exit 1

$carrabin/Select_uerra_cwci.ksh || exit 1
$carrabin/Convert_cwci.ksh || exit 1

$carrabin/Select_uerra_rh.ksh || exit 1
$carrabin/Convert_rh.ksh || exit 1

$carrabin/Cat_uerra.ksh || exit 1

exit


