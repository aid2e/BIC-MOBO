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
ele_reso = eres.CalculateReso(
    ifile = "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/25.07.0/epic_craterlake/SINGLE/e-/5GeV/45to135deg/e-_5GeV_45to135deg.0099.eicrecon.edm4eic.root",
    ofile = "test_reso.ele.root",
    pdg   = 11
)

# test resolution calculation on pi0
pi0_reso = eres.CalculateReso(
    ifile = "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/25.07.0/epic_craterlake/SINGLE/pi0/5GeV/45to135deg/pi0_5GeV_45to135deg.0099.eicrecon.edm4eic.root",
    ofile = "test_reso.pi0.root",
    pdg   = 111
)

print(f"Ran objectives:")
print(f"  -- e- resolution = {ele_reso}")
print(f"  -- pi0 resolution = {pi0_reso}")

# end =========================================================================
