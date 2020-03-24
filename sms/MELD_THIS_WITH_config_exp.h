# -*- shell-script -*-
# HARMONIE experiment configuration file
# 
# Please read the documentation on https://hirlam.org/trac/wiki/HarmonieSystemDocumentation first
#
# NB! All combinations may not be valid or well tested 
#
# **** Build and bin paths ****
# Definitions about Build, should fit with hm_rev
BUILD=${BUILD-no}                     # Turn on or off the compilation and binary build ( yes|no)
case $MAKEUP in
   no)
                                              # Definitions about gmkpack, should fit with hm_rev
      BUILD_ROOTPACK=${BUILD_ROOTPACK-no}     # Build your own ROOTPACK if it doesn't exists (yes|no)
                                              # This may take several hours!
                                              # Make sure you have write permissions in ROOTPACK directory defined in Env_system
      REVISION=40h1                           # Revision ( or cycle ) number, has to be set even for the trunk!
      BRANCH=trunk
      VERSION=01                              # Version of revision/branch to use
      OPTION=x                                # Which gmkpack/arch/SYSTEM.HOST.OPTION file to use

      # Other things to compile with gmkpack
      OTHER_PROGRAMS="pertcma mten convert_ecoclimap soda pgd blend \
                      odbtools bator ioassign odbsql \
                      blendsur addsurf surfex mandalay \
                      prep lfitools sfxtools pregpssol" 
   ;;
   yes)
   ;;
   *)
      echo "MAKEUP not valid or not set, Please set to yes/no in Env_system"
      exit
   ;;
esac

BINDIR=/perm/ms/dk/nhx/carrabin/production
##BINDIR=/perm/ms/dk/nhx/carrabin/20190710/bin19960701
#BINDIR=/perm/ms/dk/nhx/carrabin/20190809

# **** Misc, defined first because it's used later ****

CNMEXP=HARM                             # Four character experiment identifier
WRK=$HM_DATA/$CYCLEDIR                  # Work directory

# **** Paths to archive ****
# We need to define ARCHIVE early since it might be used further down

ARSTRATEGY="maximum"                     # Archive strategy
                                        # minimum: only logs and vfld file
                                        # medium: main results
                                        # maximum: everything

ARCHIVE_ROOT=$HM_DATA/archive           # Archive root directory
ECFSLOC=ec                              # Archiving site at ECMWF-ECFS: "ec" or ECFS-TMP "ectmp"
ECFSGROUP=hirald                        # Group in which to chgrp the ECMWF archive, "default" or "hirald"
EXTRARCH=$ARCHIVE_ROOT/extract          # Archive for fld/obs-extractions


# **** Running mode ****
RUNNING_MODE=research                   # Research or operational mode (research|operational)
                                        # operational implies that
                                        # - Not STAGE is done for MARS requests
                                        # - No assimilation is done if no obserations are found by Bator

SIMULATION_TYPE=nwp                     # Type of simulation (nwp|climate)


# **** Model geometry ****
DOMAIN=IGB                         # See definitions in scr/Harmonie_domains.pm
                                        # IGB/CARRA_SW, CARRA_NE, IGB
TOPO_SOURCE=gmted2010                   # Input source for orography. Available are (gtopo30|gmted2010)
                                        # For usage of gmted2010 check the documentation first
GRID_TYPE=QUADRATIC
VLEV=65                                 # Vertical level definition.
                                        # HIRLAM_60, MF_60,HIRLAM_40, or
                                        # BOUNDARIES = same number of levs as on boundary file.
                                        # See the other choices from scr/Vertical_levels.pl

# **** High level forecast options ****
NAMELIST_BASE="harmonie"                # Input for namelist generation (harmonie|alaro1)
                                        #   harmonie : The default HARMONIE namelist base nam/harmonie_namelists.pm
                                        #   alaro1   : For ALARO-1 baseline with only a few configurations available
                                        #              nam/alaro1_namelists.pm
DYNAMICS="nh"                           # Hydrostatic or non-hydrostatic dynamics (h|nh)
VERT_DISC=vfd                           # Discretization in the vertical (vfd,vfe)
                                        # Note that vfe does not yet work in non-hydrostatic mode
PHYSICS="arome"                         # Main model physics flag (arome|alaro)
SURFACE="surfex"                        # Surface flag (old_surface|surfex)
DFI="none"                              # Digital filter initialization (idfi|fdfi|none)
                                        # idfi : Incremental dfi
                                        # fdfi : Full dfi
                                        # none : No initialization (AROME default case)
LSPBDC=no                               # Spectral boundary contions option off(no) | on(yes)
LGRADSP=no                             # Apply Wedi/Hortal vorticity dealiasing
LUNBC=yes                               # Apply upper nested boundary condition

# Highlighted physics switches
CISBA="3-L"                             # Type of ISBA scheme in SURFEX. Options: "3-L" and "2-L"
CROUGH="NONE"                           # SSO scheme used in SURFEX "NONE"|"'Z01D'"|"'BE04'"
SURFEX_SEA_ICE="sice"                   # Treatment of sea ice in surfex (none|sice)
MODIFY_LAKES=F                          # Use Vanern/VAttern as Sea, requires new climate files
XZ0SN=0.003                             # Roughness length for snow. Deafult value is 0.001 m
XZ0HSN=0.0003                           # Roughness length for heat for snow. Default value is 0.0001 m
MASS_FLUX_SCHEME=edmfm                  # Version of EDMF scheme (edkf|edmfm)
                                        # Only applicable if PHYSICS=arome
                                        # edkf is the AROME-MF version
                                        # edmfm is the KNMI implementation of Eddy Diffusivity Mass Flux scheme for Meso-scale
HARATU="yes"                            # Switch for HARATU turbulence scheme (no|yes)
ALARO_VERSION=0                         # Alaro version (1|0)
NPATCH=1                                # Number of patches over land in SURFEX (see also LISBA_CANOPY)
LISBA_CANOPY=".FALSE."                  # Activates surface boundary multi layer scheme over land in SURFEX (must be .FALSE. for NPATCH>1)
# **** Assimilation ****
ANAATMO=3DVAR                           # Atmospheric analysis (3DVAR|4DVAR|blending|none)
ANASURF=CANARI_OI_MAIN                  # Surface analysis (CANARI|CANARI_OI_MAIN|CANARI_EKF_SURFEX|none)
                                        # CANARI            : Old style CANARI
                                        # CANARI_OI_MAIN    : CANARI + SURFEX OI
                                        # CANARI_EKF_SURFEX : CANARI + SURFEX EKF ( experimental )
                                        # none              : No surface assimilation
ANASURF_MODE="before"                   # When ANASURF should be done
                                        # before            : Before ANAATMO
                                        # after             : After ANAATMO
                                        # both              : Before and after ANAATMO (Only for ANAATMO=4DVAR) 
INCV="1,1,1,1"                          # Active EKF control variables. 1=WG2 2=WG1 3=TG2 4=TG1
INCO="1,1,0"                            # Active EKF observation types (Element 1=T2m, element 2=RH2m and element 3=Soil moisture) 
IAU=no                                  # IAU=yes if with incremental analysis update, no for default

MAKEODB2=no                             # Conversion of ODB-1 to ODB-2 using odb_migrator

SST_SOURCES="IFS OSISAF"                # List of external SST sources like IFS|HIROMB|NEMO|ROMS|OSISAF
                                        # See util/gl_grib_api/ala/merge_ocean.F90 for more details
lsnowalb=".TRUE."                       # Use MOD10A1 C6 glacier albedos if true

LSMIXBC=no                              # Spectral mixing of LBC0 file before assimilation
[ "$ANAATMO" = 3DVAR ] && LSMIXBC=yes
JB_INTERPOL=no                          # Interpolation of structure functions from a pre-defined domain to your domain

# **** Observations ****
OBDIR=$HM_DATA/observations             # Observation file directory
RADARDIR=$HM_DATA/radardata             # Radar observation file directory
SINGLEOBS=no                            # Run single obs experiment with observation created by scr/Create_single_obs (no|yes)

USE_MSG=no                              # Use MSG data for adjustment of inital profiles, EXPERIMENTAL! (no|yes)
MSG_PATH=$SCRATCH/CLOUDS/               # Location of input MSG FA file, expected name is MSGcloudYYYYMMDDHH

# **** 4DVAR ****
NOUTERLOOP=2                            # 4DVAR outer loops, need to be 1 at present
ILRES=2,2                               # Resolution (in parts of full) of outer loops
TSTEP4D=120,120                         # Timestep length (seconds) of outer loops TL+AD
TL_TEST=yes                             # Only active for playfile tlad_tests
AD_TEST=yes                             # Only active for playfile tlad_tests
CH_RES_SPEC=yes                         # yes => change of resolution of the increment spectrally; no => by FULLPOS

# **** DFI setting ****
TAUS=5400                               # cut-off frequency in second 
TSPAN=5400                              # 7200s or 5400s

# **** Nesting ****
HOST_MODEL="ifs"                        # Host model (ifs|hir|ald|ala|aro)
                                        # ifs : ecmwf data
                                        # hir : hirlam data
                                        # ald : Output from aladin physics
                                        # ala : Output from alaro physics
                                        # aro : Output from arome physics

HOST_SURFEX="no"                        # yes if the host model is run with SURFEX
SURFEX_INPUT_FORMAT=lfi                 # Input format for host model run with surfex (lfi|fa)

NBDMAX=12                               # Number of parallel interpolation tasks
MULTITASK=no                            # Submit jobs through the multi task script
export MULTITASK_OBSMON=yes
BDLIB=ECMWF                             # Boundary experiment, set:
                                        # ECMWF to use MARS data
                                        # RCRa  to use RCRa data from ECFS
                                        # Other HARMONIE/HIRLAM experiment

BDDIR=$HM_DATA/${BDLIB}/archive/@YYYY@/@MM@/@DD@/@HH@   # Boundary file directory,
                                                        # For more information, read in scr/Boundary_strategy.pl
INT_BDFILE=$WRK/ELSCF${CNMEXP}ALBC@NNN@                 # Interpolated boundary file name and location

BDSTRATEGY=era5 				# Which boundary strategy to follow 
                                # as defined in scr/Boundary_strategy.pl
                                # 
                                # available            : Search for available files in BDDIR, try to keep forecast consistency
                                #                        This is ment to be used operationally
                                # simulate_operational : Mimic the behaviour of the operational runs using ECMWF LBC,
                                #                        i.e. 6 hour old boundaries
                                # same_forecast        : Use all boundaries from the same forecast, start from analysis
                                # analysis_only        : Use only analysises as boundaries
                                # era5                 : As for analysis_only but using ERA5 data and hourly analysis from 4DVAR
                                # era                  : As for analysis_only but using ERA interim data
                                # e40                  : As for analysis_only but using ERA40 data
                                # latest               : Use the latest possible boundary with the shortest forecast length
                                # RCR_operational      : Mimic the behaviour of the RCR runs, ie
                                #                        12h old boundaries at 00 and 12 and
                                #                        06h old boundaries at 06 and 18
                                # enda                 : use ECMWF ENDA data for running ensemble data assimilation
                                #                        or generation of background statistic.
                                #                        Note that only LL up to 9h is supported
                                #                        with this you should set your ENSMSEL members
                                # eps_ec               : ECMWF EPS members from the GLAMEPS ECFS archive.
                                #                        Data available from 2013 and onwards
                                #                        Only meaningful with ENSMSEL non-empty, i.e., ENSSIZE > 0
BDINT=1                         # Boundary interval in hours
[ "$BDSTRATEGY" = analysis_only ] && BDINT=6 				# Which boundary strategy to follow 
PERTDIA_BDINT=6                 # Perturbation diagnostics interval

SURFEX_PREP="yes"               # Use offline surfex prep facility (Alt. gl + Fullpos + prep )

# *** Ensemble mode general settings. ***
# *** For member specific settings use msms/harmonie.pm ***
ENSMSEL=                                # Ensemble member selection, comma separated list, and/or range(s):
                                        # m1,m2,m3-m4,m5-m6:step    mb-me == mb-me:1 == mb,mb+1,mb+2,...,me
                                        # 0=control. ENSMFIRST, ENSMLAST, ENSSIZE derived automatically from ENSMSEL.
ENSINIPERT=                             # Ensemble perturbation method (bnd, randb). Not yet implemented: etkf, hmsv.
ENSCTL=                                 # Which member is my control member? Needed for ENSINIPERT=bnd. See harmonie.pm.
ENSBDMBR=                               # Which host member is used for my boundaries? Use harmonie.pm to set.
ENSMFAIL=0                              # Failure tolerance for all members.
ENSMDAFAIL=0                            # Failure tolerance for members doing own DA. Not implemented.
SLAFK=1.0                               # best set in harmonie.pm
SLAFLAG=0                               # --- " ---
SLAFDIFF=0                              # --- " ---

# *** This part is for EDA with observations perturbation
PERTATMO=none                           # ECMAIN  : In-line observation perturbation using the default IFS way.
                            			# CCMA    : Perturbation of the active observations only (CCMA content)
	                            		#           before the Minimization, using the PERTCMA executable.
                            			# none    : no perturbation of upper-air observations

PERTSURF=none                           # ECMA    : perturb also the surface observation before Canari (recommended
                            			#         : for EDA to have full perturbation of the initial state).
                                        # model   : perturb surface fields in grid-point space (recursive filter)
			                            # none    : no perturbation for surface observations.

FESTAT=no                               # Extract differences and do Jb calculations (no|yes)

# **** Climate files **** 
CREATE_CLIMATE=${CREATE_CLIMATE-yes}    # Run climate generation (yes|no)
CLIMDIR=$HM_DATA/climate                # Climate files directory 
BDCLIM=$HM_DATA/${BDLIB}/climate        # Boundary climate files (ald2ald,ald2aro)
                                        # This should point to intermediate aladin  
                                        # climate file in case of hir2aro,ifs2aro processes.

# Physiography input for SURFEX
ECOCLIMAP_VERSION=2.2                   # Version of ECOCLIMAP for surfex (1,2)
                                        # Available versions are 1.1-1.5,2.0-2.2
                                        # For beta.1, the ECOCLIMAP v 2.2 for CARRA west and east domains point to different files, to be united in beta.2
SOIL_TEXTURE_VERSION=HWSD_v2           # Soil texture input data FAO|HWSD_v2

# **** Archiving settings ****
TFLAG="h"                               # Time flag for model output. (h|min)
                                        # h   = hour based output
                                        # min = minute based output

[ "$TFLAG" = "min" ] && GRIB_TIME_UNIT=13  # GRIB_TIME_UNIT=0 1 min time unit
                                           # GRIB_TIME_UNIT=1 hourly time unit (default)
                                           # GRIB_TIME_UNIT=13 15 min time unit
                                           # GRIB_TIME_UNIT=14 30 min time unit
                                           # see scr/Makegrib

# **** Cycles to run, and their forecast length ****

# The content of HWRITUPTIMES, VERITIMES, SWRITUPTIMES, PWRITUPTIMES should be: 
#   - hours   if TFLAG="h"
#   - minutes if TFLAG="min"
 
# Writeup times of # history,surfex and fullpos files 
# Comma separated list, and/or range(s):
# t1,t2,t3-t4,t5-t6:step    tb-te == tb-te:1 == tb,tb+1,tb+2,...,te

if [ -z "$ENSMSEL" ] ; then
  # Standard deterministic run
  HH_LIST="00-21:3"                       # Which cycles to run, replaces FCINT
  LL_LIST="30,3,3,3,30,3,3,3"             # Forecast lengths for the cycles [h], replaces LL, LLMAIN
                                          # The LL_LIST list is wrapped around if necessary, to fit HH_LIST
  HWRITUPTIMES="00-06:1,09-30:3"          # History file output times
  FULLFAFTIMES=$HWRITUPTIMES              # History FA file IO server gather times
  PWRITUPTIMES=$HWRITUPTIMES              # Postprocessing times 
  PFFULLWFTIMES=$PWRITUPTIMES             # Postprocessing FA file IO server gathering times 
  VERITIMES=$HWRITUPTIMES                 # Verification output times, may change PWRITUPTIMES
  SWRITUPTIMES=$HWRITUPTIMES              # Surfex output times
  SFXWFTIMES=$SWRITUPTIMES                # SURFEX FA file IO server gathering times 
  SFXFULLTIMES="00-12:3"                  # Surfex model state output times
                                          # Only meaningful if SURFEX_LSELECT=yes
  SFXFWFTIMES=$SFXFULLTIMES               # SURFEX full FA file IO server gathering times 
else
  # EPS settings
  HH_LIST="00-21:3"                       # Which cycles to run, replaces FCINT
  LL_LIST="12,9,18,15,12,9,18,15"                            # Forecast lengths for the cycles [h], replaces LL, LLMAIN
  HWRITUPTIMES="00-12:1,15-18:3"                  # History file output times
  FULLFAFTIMES=$HWRITUPTIMES              # History FA file IO server gather times
  PWRITUPTIMES="00-18:1"                  # Postprocessing times 
  PFFULLWFTIMES=$PWRITUPTIMES              # Postprocessing FA file IO server gathering times 
  VERITIMES="00-24:3"                     # Verification output times, may change PWRITUPTIMES
  SWRITUPTIMES=$HWRITUPTIMES              # Surfex output times
  SFXWFTIMES=$SWRITUPTIMES                 # SURFEX FA file IO server gathering times 
  SFXFULLTIMES="00-12:1"                  # Surfex full model state output times
                                          # Only meaningful if SURFEX_LSELECT=yes
  SFXFWFTIMES=$SFXFULLTIMES               # SURFEX full FA file IO server gathering times 
fi

SURFEX_OUTPUT_FORMAT=fa                 # Output format for surfex (fa|lfi)
SURFEX_LSELECT="yes"                    # Only write selected fields in surfex outpute files. (yes|no)
                                        # Check nam/surfex_selected_output.pm for details. 
                                        # Not tested with lfi files.
INT_SINI_FILE=$WRK/SURFXINI.$SURFEX_OUTPUT_FORMAT       # Surfex initial file name and location
ARCHIVE_ECMWF=yes                       # Archive to $ECFSLOC at ECMWF (yes|no)

# **** Postprocessing/output ****
IO_SERVER=no                            # Use IO server (yes|no). Set the number of cores to be used
                                        # in your Env_submit
IO_SERVER_BD=no                         # Use IO server for reading of boundary data
POSTP="inline"                          # Postprocessing by Fullpos (inline|offline|none).
                                        # See Setup_postp.pl for selection of fields.
                                        # inline: this is run inside of the forecast
                                        # offline: this is run in parallel to the forecast in a separate task

FREQ_RESET_TEMP=6                       # Reset frequency of max/min temperature values in hours, controls NRAZTS
FREQ_RESET_GUST=1                       # Reset frequency of max/min gust values in hours, controls NXGSTPERIOD
                                        # Set to -1 to get the same frequency _AND_ reset behaviour as for min/max temperature
                                        # See yomxfu.F90 for further information.

# **** CARRA ARCHIVE ****
CARRA_PARENT_EXP="carra_NE_2" # stream to archive
CARRA_GRIB2_CONVERT=yes                # Convert grib to grib2 (yes|no)
CARRA_GRIB2_ARCHIVE=yes                # Push grib2 to MARS    (yes|no)
MARS_DATABASE="marsscratch"                   # (marsscratch|mars)


# **** GRIB ****
CONVERTFA=yes                           # Conversion of FA file to GRIB/nc (yes|no)
ARCHIVE_FORMAT=GRIB1                    # Format of archive files (GRIB1|GRIB2|nc). nc format yet only available in climate mode
MAKEGRIB_VERSION=gribex                 # Use gl with (gribex|grib_api), grib_api required for GRIB2 to work
NCNAMES=nwp                             # Nameing of NetCDF files follows (climate|nwp) convention.
RCR_POSTP=no                            # Produce a subset of fields from the history file for RCR monitoring
                                        # Only applicable if ARCHIVE_FORMAT=grib
MAKEGRIB_LISTENERS=1                    # Number of parallel listeners for Makegrib
                                        # Only applicable if ARCHIVE_FORMAT=grib


# **** Obs verification ****
VERIFY=no                               # Run verification in the experiment (yes|no)
OBSEXTR=bufr                            # Extract observations from BUFR (bufr|vobs|none)
                                        # bufr = create vobs file from BUFR files
                                        # vobs = copy pre-extracted vobs file from VOBSDIR
VOBSDIR=$EXTRARCH                       # Local directory of pre-extracted vobs files
FLDEXTR=yes                             # Extract model data for verification from model files (yes|no)
FLDEXTR_TASKS=1                         # Number of parallel tasks for field extraction
VFLDEXP=carra_IGB
VER_SDATE=$DTGBEG                       # Start verification date in format ($DTGBEG|YYYYMMDDHH)
                                        # applicable if VERIFY=yes


# *** Field verification ***
FLDVER=no                               # Main switch for field verification (yes|no)
FLDVER_HOURS="06 12 18 24 30 "  # Hours for field verification

# *** Observation monitoring ***
OBSMONITOR=obstat:                      # Create Observation statistics plots
                                        # Format: OBSMONITOR=Option1:Option2:...:OptionN
                                        # obstat: Daily usage maps and departures
                                        # plotlog: IFS log statistics
                                        #  - Grid point and spectral norms evolution
                                        #  - Cost function evolution, if applicable
                                        #  - Observation usage from the minimization, if applicable
                                        # no: Nothing at all
                                        #
                                        # The assimilation related monitoring is
                                        # only active if ANAATMO != none

#  *** Monitoring maps for hirlam.org. ***
#      Note that at ECMWF this is run on ecgb (grads is only there)
#      In  this version You must check out manually contrib/mapbin to the 
#      directory referred as MAPBIN 
FIELDMONITOR=no
MAPBIN=$HM_DATA/lib/util/mapbin

# Recipient(s) to send mail to when a task aborts
MAIL_ON_ABORT=                          # you@work,you@home

# Exporting variables for the system
export ARCHIVE_ROOT EXTRARCH BINDIR HH_LIST LL_LIST WRK CLIMDIR MODEL
export BDLIB BDDIR BDINT BDSTRATEGY NBDMAX MARS_EXPVER HOST_MODEL
export GRID_TYPE
export TFLAG POSTP RCR_POSTP CONVERTFA ARCHIVE_FORMAT MAKEGRIB_LISTENERS GRIB_TIME_UNIT MAKEGRIB_VERSION CARRA_GRIB2_CONVERT CARRA_GRIB2_ARCHIVE MARS_DATABASE
export ECFSLOC ECFSGROUP NLBC FCINT DOMAIN BDCLIM LSMIXBC CISBA INCV INCO CROUGH SURFEX_SEA_ICE TOPO_SOURCE
export VERITIMES OBSEXTR FLDEXTR FLDEXTR_TASKS VFLDEXP VOBSDIR 
export SURFEX_OUTPUT_FORMAT SURFEX_INPUT_FORMAT SURFEX_LSELECT
export BUILD CREATE_CLIMATE VERIFY REVISION BRANCH OPTION PROGRAM OTHER_PROGRAMS BUILD_ROOTPACK VERSION
export HWRITUPTIMES SWRITUPTIMES PWRITUPTIMES FLDVER_HOURS FLDVER SURFEX_PREP HOST_SURFEX 
export FULLFAFTIMES PFFULLWFTIMES
export SFXFULLTIMES SFXWFTIMES SFXFWFTIMES
export ANASURF_MODE EXT_BDDIR EXT_BDFILE EXT_ACCESS JB_INTERPOL SINGLEOBS
export NPATCH LISBA_CANOPY lsnowalb
export FIELDMONITOR MAPBIN
export BDFILE NCNAMES
export ANAATMO ANASURF VLEV VER_SDATE ARCHIVE_ECMWF FLDEXTR SST_SOURCES
export MAKEODB2
export NOUTERLOOP ILRES TSTEP4D
export OBDIR RADARDIR OBSMONITOR
export DYNAMICS PHYSICS SURFACE DFI TAUS TSPAN LGRADSP LSPBDC LUNBC
export CNMEXP RUNNING_MODE MASS_FLUX_SCHEME HARATU
export INT_BDFILE INT_SINI_FILE
export TL_TEST AD_TEST CH_RES_SPEC
export ECOCLIMAP_VERSION SOIL_TEXTURE_VERSION
export SIMULATION_TYPE
export ARSTRATEGY FREQ_RESET_TEMP FREQ_RESET_GUST
export IO_SERVER IO_SERVER_BD
export MAIL_ON_ABORT
export USE_MSG MSG_PATH
export VERT_DISC ALARO_VERSION NAMELIST_BASE

export PERTATMO PERTSURF SLAFLAG SLAFK SLAFDIFF
export MODIFY_LAKES
export ENSMSEL ENSBDMBR ENSINIPERT ENSCTL ENSMFAIL ENSMDAFAIL FESTAT
export PERTDIA_BDINT MULTITASK
export XZ0SN XZ0HSN
export H_TREE_FILE

# Define your testbed list here
# The definition of the different configurations can be found in scr/Harmonie_testbed.pl
export TESTBED_LIST="AROME_3DVAR AROME_1D AROME AROME_MUSC \
                     AROME_3DVAR_2P AROME_BD_ARO_2P \
                     ALARO_3DVAR ALARO_1D ALARO ALARO_MUSC \
                     AROME_BD_ARO AROME_BD_ALA \
                     AROME_EKF \
                     ALARO_3DVAR_OLD ALARO_OLD_MUSC \
                     ALARO1_3DVAR_OLD \
                     HarmonEPS \
                     AROME_EPS_COMP" 
#                    AROME_CLIMSIM \

# Let the testbed continue when a child fails
export CONT_ON_FAILURE=0

export IMOOBS HM_CLDATA PGD_DATA_PATH ECOCLIMAP_DATA_PATH GMTED2010_DATA_PATH E923_DATA_PATH
HM_CLDATA=/perm/ms/dk/nhz/PGD/40h1.carra.beta.2
PGD_DATA_PATH=$HM_CLDATA/PGD
ECOCLIMAP_DATA_PATH=$HM_CLDATA/ECOCLIMAP/40h1.1
GMTED2010_DATA_PATH=/perm/ms/dk/nhx/40h1/GMTED2010ARCDEM
E923_DATA_PATH=$HM_CLDATA/E923_DATA/38h1.1
if [ "$DOMAIN" = IGB -o "$DOMAIN" = CARRA_SW ]; then
   IMOOBS=yes
elif [ "$DOMAIN" = CARRA_NE ]; then
   IMOOBS=no
   H_TREE_FILE="tree_height_carra_east.dat" # Give name of external tree height data file to be find in the $HM_CLDAT
else
   IMOOBS=no
fi
