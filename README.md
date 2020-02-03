# carra_grib2

*This repository contains scripts for converting grib1 to grib2 files,
archiving to mars for the CARRA project and some additional tools for visualisation.*

+ Structure is similar to harmonie and can copied into an experiment. (rsync -av carra_grib2/ ~/hm_home/experiment_dir/)
+ Following files has to be updated:
    - config-sh/submit.[machine]
    - sms/config_exp.h
    - msms/harmonie.tdf

+ New variables in config_exp.h are:
    - CARRA_GRIB2_CONVERT=yes                 # Convert grib to grib2 (yes|no)
    - CARRA_GRIB2_ARCHIVE=yes                 # Push grib2 to MARS    (yes|no)
    - MARS_DATABASE=marsscratch               # (marsscratch|???)



## Content:

1. **Carra_grib_extract**: 
> Extracts relevant fields from harmonie grib output files,
> and save them into carra_grib1 directory in DTGDIR.

2. **Carra_grib_archive**:
> Converts file s in carra_grib1 directory and save them in carra_grib2 directory.
> if archive=1 it will also push the data to mars.

3. **Carra_grib_save4later**:
> packs fields not yet ready for grib2/mars into a grib1 file in $ARCHIVE

4. **Carra_grib_gallery**:
> make png plots based on recently archived mars data for quick inspection.

  



