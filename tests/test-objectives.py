# =============================================================================
## @file   test-objectives.py
#  @author Derek Anderson
#  @date   08.29.2025
# -----------------------------------------------------------------------------
## @Driver script to test run objective
#    methods
#
#  TODO convert to use pytest
# =============================================================================

import sys
sys.path.append('../')

import objectives.BICEnergyResolution as eres

# test 0: run objectives ------------------------------------------------------

# output file names for convenience
ofResEle = "test_reso.ele.root"
ofResPi0 = "test_reso.pi0.root"

# test resolution calculation on electrons
ele_reso = eres.CalculateReso(
    ifile = "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/25.07.0/epic_craterlake/SINGLE/e-/5GeV/45to135deg/e-_5GeV_45to135deg.0099.eicrecon.edm4eic.root",
    ofile = ofResEle,
    pdg   = 11
)

# test resolution calculation on pi0
pi0_reso = eres.CalculateReso(
    ifile = "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/25.07.0/epic_craterlake/SINGLE/pi0/5GeV/45to135deg/pi0_5GeV_45to135deg.0099.eicrecon.edm4eic.root",
    ofile = ofResPi0,
    pdg   = 111
)

print(f"[0] Ran objectives:")
print(f"  -- e- resolution = {ele_reso}")
print(f"  -- pi0 resolution = {pi0_reso}")

# test 1: extract objectives --------------------------------------------------

# extract electron resolution
ele_reso_txt = None
with open(ofResEle.replace(".root", ".txt")) as oele:
    ele_reso_txt = float(oele.read().splitlines()[0])

# extract pi0 resolution
pi0_reso_txt = None
with open(ofResPi0.replace(".root", ".txt")) as opi0:
    pi0_reso_txt = float(opi0.read().splitlines()[0])

print(f"[1] Extracted objectives:")
print(f"  -- e- resolution = {ele_reso_txt}, type = {type(ele_reso_txt)}")
print(f"  -- pi0 resolution = {pi0_reso_txt}, type = {type(pi0_reso_txt)}")

# end =========================================================================
