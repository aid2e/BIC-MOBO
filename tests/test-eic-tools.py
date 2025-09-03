# =============================================================================
## @file   test-eic-tools.py
#  @author Derek Anderson
#  @date   09.02.2025
# -----------------------------------------------------------------------------
## @brief A small script to test various features
#    of the EICMoboTools module.
#
#  TODO convert to use pytest
# =============================================================================

import EICMoboTools as emt


# (0) Test ConfigParser -------------------------------------------------------

# these should work
enable1 = emt.GetParameter("enable_staves_1", "parameters_config.json")
enable2 = emt.GetParameter("enable_staves_2", "parameters_config.json")

# grab variables
path1, type1, units1 = emt.GetPathElementAndUnits(enable1)
path2, type2, units2 = emt.GetPathElementAndUnits(enable2)

print(f"[0][enable_staves_1] path = {path1}, type = {type1}, units = {units1}")
print(f"[0][enable_staves_2] path = {path2}, type = {type2}, units = {units2}")

try:
    enable3 = emt.GetParameter("eanble_satvse_3", "parameters_config.json")
except:
    print(f"[0][enable_staves_3] exception raised!")
finally:
    print(f"[0][enable_staves_3] typo generated error as expected!")

# (1) Test GeometryEditor -----------------------------------------------------

# create a geometry editor
geditor = emt.GeometryEditor("environment_config.json", "parameters_config.json")

# edit a couple parameters in one compact file
geditor.EditCompact(enable1, 0, "test1A")
geditor.EditCompact(enable2, 1, "test1A")
print(f"[1][test A] set values of staves 1, 2 to 0, 1 respectively")

# now create config files associated with
# compact; the 2nd line should leave
# config file unmodified
geditor.EditConfig(enable1, "test1A")
geditor.EditConfig(enable2, "test1A")
print("[1][Test A] config file created")

# create a 2nd compact file with multiple
# subsystems modified
enable5 = emt.GetParameter("enable_staves_5", "parameters_config.json")
dsnout  = emt.GetParameter("snout_length", "parameters_config.json")
geditor.EditCompact(enable5, 1, "test1B")
geditor.EditCompact(dsnout, 23., "test1B")
print(f"[1][test B] set value of stave 5 to 1, and the dRICH snout length to 23 cm")

# this one should create a new config file,
# and the 2nd line should add the modified
# dRICH file
geditor.EditConfig(enable5, "test1B")
geditor.EditConfig(dsnout, "test1B")
print(f"[1][test B] config file created")

# end =========================================================================
