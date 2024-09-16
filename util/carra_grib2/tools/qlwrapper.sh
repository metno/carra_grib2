#!/bin/bash

module load ecmwf-toolbox
module load python3

python3 quicklook.py "$@"
