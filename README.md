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

  
## Tools:

* **quicklook.py**:
  Visualize a field from gribfile or mars. Possible to plot difference between fiels and fields. Requires metview and eccodes and python3 with matplotlib++
  ```
    $ ./quicklook.py -h

    usage: quicklook.py [-h] -w WHERE [-fd FILEDIFF] [-wd WHEREDIFF] filename
    
    take a quicklook on parameter from gribfile
    
    positional arguments:
      filename              grib filename (or mars origin)
    
    options:
      -h, --help            show this help message and exit
      -w WHERE, --where WHERE
                            comma separated list of key specifier
      -fd FILEDIFF, --filediff FILEDIFF
                            name of file to compare
      -wd WHEREDIFF, --wherediff WHEREDIFF
                            specifier to compare
    
    Examples:
        grib1 file
        ./quicklook.py fc2024073112+004grib_fp -w param=11.253 
    
        from mars (carra2) 
        ./quicklook.py no-ar-pa -w param=167,dtg=2020121706,step=2,type=fc
    
        diff mars and gribfile
        ./quicklook.py no-ar-ce -w param=167,dtg=2020121706,step=0 -fd fc2024073112+012grib_fp -wd param=11.253 
  ```

* **batch_plot_fields.py**:
  Saves predefined figures (weather maps) for a given time/source

```
  $ ./batch_plot_fields.py -h
usage: batch_plot_fields.py [-h] [--dtg DTG] [--source SOURCE] [--origin ORIGIN] [--database DATABASE]

make wheather maps

options:
  -h, --help           show this help message and exit
  --dtg DTG            yyyymmddhh
  --source SOURCE      mars or path/to/grib2files/
  --origin ORIGIN      DOMAIN: no-ar-ce, no-ar-cw, no-ar-pa
  --database DATABASE  database

    Examples:

    ./batch_plot_fields.py --dtg 2020121706

  ```

