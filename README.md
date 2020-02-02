# carra_grib2

This repository contains scripts for converting grib1 to grib2 files,
archiving to mars archive for the CARRA project and some additional tools for visualisation.


Content:

  Run_all_new: (Should be softlinked into scr/Carra_grib_convert)
    Extracts relevant fields from harmonie grib output files,
    and save them into carra_grib1 directory in DTGDIR.

  archive/doit.hirlam.org: (Should be softlinked into scr/Carra_grib_archive)
    Converts files in carra_grib1 directory and save them in carra_grib2 directory.
    if archive=1 it will also push the data to mars.

  



