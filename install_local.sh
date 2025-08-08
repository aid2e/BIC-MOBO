#!/bin/bash
# =============================================================================
# @file   install_local.sh
# @author Derek Anderson (building on work by Wen Guan)
# @date   08.08.2025
# -----------------------------------------------------------------------------
# Script to set up conda environment for BIC MOBO on
# your local machine.
#
# Usage:
#  source install_local.sh <environment name>
# =============================================================================

# check to make sure no. of arguments is correct
if [ "$#" -ne 1 ]; then
  echo "Wrong number of parameters!"
  echo "Usage:"
  echo "  source install_local.sh <environment name>"
  return 2
fi

# now activate conda
#   - this assumes conda (or mamba) is already installed,
#     e.g. via miniforge
#
#       https://github.com/conda-forge/miniforge
#
conda activate

# check if environment is already created
if { conda env list | grep "$1"; } >/dev/null 2>&1; then
  echo "WARNING: environment already created!"
  echo "Activating environment \"$1\""
  conda activate $1
  return 0
fi

# if not created, create environment
conda create --name $1
conda activate $1

# framework requires python 3.11.5
conda install python=3.11.5

# install relevant packages
pip install -r pip_requirements.txt
pip install gmpy2
conda install --file conda_requirements.txt # FIXME this probably isn't needed

# additional installations will go here

# end =========================================================================
