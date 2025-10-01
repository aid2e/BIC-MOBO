# =============================================================================
## @file   test-aid2e-tools.py
#  @author Derek Anderson
#  @date   09.29.2025
# -----------------------------------------------------------------------------
## @brief A small script to test various features
#    of the AID2ETestTools module.
#
#  TODO convert to use pytest
# =============================================================================

import pprint
import sys
sys.path.append('../')

import AID2ETestTools as att
import EICMOBOTestTools as emt



# (0) Test config converters -------------------------------------------------- 

# load config files
cfg_run = emt.ReadJsonFile("../configuration/run.config")
cfg_exp = emt.ReadJsonFile("../configuration/problem.config")
cfg_par = emt.ReadJsonFile("../configuration/parameters.config")
cfg_obj = emt.ReadJsonFile("../configuration/objectives.config")

# convert parameter config
ax_pars = att.ConvertParamConfig(cfg_par)
print(f"[0][Test A] Converted parameter configuration")
pprint.pprint(ax_pars)

# convert objective config
ax_objs = att.ConvertObjectConfig(cfg_obj)
print(f"[0][Test B] Converted objective configuration")
print(f"  objectives = {ax_objs}")

# end =========================================================================
