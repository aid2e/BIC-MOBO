#!/bin/zsh
# ===============================================
# @file    this-mobo.zsh
# @authors Derek Anderson
# @date    01.07.2025
# -----------------------------------------------
# Sets enviroment variable with path to
# this installation of the BIC-MOBO
# problem.
# ===============================================

set -f
path_to_this="${(%):-%N}"
export BIC_MOBO="${path_to_this:A:h:h}"
export OBJ_CFG=$BIC_MOBO/configurations/objectives.config
export PAR_CFG=$BIC_MOBO/configuration/parameters.config
export EXP_CFG=$BIC_MOBO/configuration/problem.config
export RUN_CFG=$BIC_MOBO/configuration/run.config

# end ===========================================
