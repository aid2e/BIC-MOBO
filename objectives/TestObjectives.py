# =============================================================================
## @file   TestObjectives.py
#  @author Derek Anderson
#  @date   08.29.2025
# -----------------------------------------------------------------------------
#  Driver script to test run objective
#  methods
# =============================================================================

import BICEnergyResolution as eres

# test resolution calculation on electrons
reso = eres.CalculateReso(
    ifile = "../../input/forToyObjectiveTesting.epic25080evt1Ke5th33ele.podio.root",
    ofile = "test.root",
    pdg   = 11
)

print(f"Ran objectives:")
print(f"  -- e resolution = {reso}")

# end =========================================================================
