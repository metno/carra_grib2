#!/usr/bin/perl

# Get the required environment variables
# -----------------------------------------
foreach $var ( qw/HM_LIB HM_WD DTGBEG DTG FCINT PP/ ) {
   if ( exists $ENV{$var} ) {
      $$var=$ENV{$var};
   } else {
      push @lackenv, $var;
   }
}

# Some required environment variables missing?
# ------------------------------------------------
if ( @lackenv ) {
   print STDERR "The following environment variables are needed but missing:\n\t";
   print STDERR join("\n\t", @lackenv);
   die "\n$0 failed\n";
}

## Needed for the &Env function
require "$HM_LIB/msms/harmonie.pm";

## For consistency with the harmonie.tdf hour loop step:
my $fcint = 24; #&Env('FCINT','min');

## Compute new DTG
my $dtgnew ;
if ( $ENV{SIMULATION_TYPE} eq 'climate' ) {
 $dtgnew = $DTG;
} else {
 $dtgnew = qx(mandtg $DTG + 24 );
 chomp $dtgnew;
}

print $DTG 
print $dtgnew 
## Write to file
my $proglog = "$HM_WD/progress$PP.log";
open(PL,">$proglog") || die "Could not write '$proglog'\n";
print PL "DTG$PP=$dtgnew export DTG$PP\n";
unless ( $PP ) {
   print PL "DTGBEG=$DTGBEG\n";
}
close(PL);
