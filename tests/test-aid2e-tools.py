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

from BICLowQ2 import AID2ETools as at
from BICLowQ2 import EICTools as et



# (0) Test config converters -------------------------------------------------- 

# load config files
cfg_run = et.ReadJsonFile("../configuration/run.config")
cfg_exp = et.ReadJsonFile("../configuration/problem.config")
cfg_par = et.ReadJsonFile("../configuration/parameters.config")
cfg_obj = et.ReadJsonFile("../configuration/objectives.config")

# convert parameter config
ax_pars = at.ConvertParamConfig(cfg_par)
print(f"[0][Test A] Converted parameter configuration")
pprint.pprint(ax_pars)

# convert objective config
ax_objs = at.ConvertObjectConfig(cfg_obj)
print(f"[0][Test B] Converted objective configuration")
print(f"  objectives = {ax_objs}")

# end =========================================================================
