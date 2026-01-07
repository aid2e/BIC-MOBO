#!/bin/bash
# ===============================================
# @file    this-mobo.sh
# @authors Derek Anderson
# @date    01.07.2025
# -----------------------------------------------
# Sets enviroment variable with path to
# this installation of the BIC-MOBO
# problem.
# ===============================================

path_to_this=$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
export BIC_MOBO=$(dirname -- "$path_to_this")

# end ===========================================
