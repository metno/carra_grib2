#!/bin/bash




export MKDIR='mkdir -p'

export DOMAIN=carra_NE
export DTG=2017010906
export WRK=$SCRATCH/testWRK2/
export ARCHIVE=/scratch/ms/no/fab0/hm_home/carra_grib_convert2/archive/2017/01/09/06/
export HM_LIB=/scratch/ms/no/fab0/hm_home/carra_grib_convert2_SW/lib/
export PATH=$PATH:$HM_LIB/scr/


cd $WRK


$HM_LIB/util/carra_grib2/carra_grib_convert/Carra_grib_convert
