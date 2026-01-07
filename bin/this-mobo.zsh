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

# end ===========================================
