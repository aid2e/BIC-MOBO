#!/bin/tcsh
# ===============================================
# @file    this-mobo.tcsh
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

# end ===========================================
