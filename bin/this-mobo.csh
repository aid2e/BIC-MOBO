#!/bin/csh
# ===============================================
# @file    this-mobo.csh
# @authors Derek Anderson
# @date    01.07.2025
# -----------------------------------------------
# Sets enviroment variable with path to
# this installation of the BIC-MOBO
# problem.
# ===============================================

set invoked = ($_)
if ("$invoked" != "") then
    set path_to_this = `readlink -f "$invoked[2]:q"`
else
    set path_to_this = `readlink -f "$0:q"`
endif
setenv BIC_MOBO "${path_to_this:h:h}"
setenv OBJ_CFG "$BIC_MOBO/configuration/objectives.config"
setenv PAR_CFG "$BIC_MOBO/configuration/parameters.config"
setenv EXP_CFG "$BIC_MOBO/configuration/problem.config"
setenv RUN_CFG "$BIC_MOBO/configuration/run.config"
setenv SLM_TMP "$BIC_MOBO/configuration/template.slurm"
setenv ENV_SCR "$BIC_MOBO/bin/this-mobo.csh"

# end ===========================================
