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

import json
import sys
sys.path.append('../')

import objectives.BICClustEneReso as bcer
import objectives.BICEPScan as beps
import objectives.BICHitAngReso as bhar

# test 0: run objectives ------------------------------------------------------

# output file names for convenience
ofResGam = "test_eneres.gam.root"
ofResEle = "test_etares.ele.root"
ofResPiM = "test_reject.pim.root"

# grab default options
gam_opts = bcer.DEFAULT_OPTS
ele_opts = bhar.DEFAULT_OPTS
pim_opts = beps.DEFAULT_OPTS
gam_opts.ofile = ofResGam
ele_opts.ofile = ofResEle
pim_opts.ofile = ofResPiM

# test energy resolution calculatio on gamma
gam_res = bcer.CalculateClustEneReso(gam_opts)

# test angular resolution calculation on e-
ele_res = bhar.CalculateHitAngReso(ele_opts)

# test resolution calculation on pi- (and e-)
pim_rej = beps.DoEPScan(pim_opts)

print(f"[0] Ran objectives:")
print(f"  -- gamma energy resolution = {gam_res}")
print(f"  -- e- eta resolution = {ele_res}")
print(f"  -- pi- rejection power = {pim_rej}")

# test 1: extract objectives --------------------------------------------------

# extract gamma resolution
gam_res_json = None
with open(ofResGam.replace(".root", ".json")) as ogam:
    gam_res_data = json.load(ogam)
    gam_res_json = gam_res_data["energy_resolution"]

# extract e- resolution
ele_res_json = None
with open(ofResEle.replace(".root", ".json")) as oele:
    ele_res_data = json.load(oele)
    ele_res_json = ele_res_data["eta_resolution"]

# extract pi- rejection power
pim_rej_json = None
with open(ofResPiM.replace(".root", ".json")) as opim:
    pim_rej_data = json.load(opim)
    pim_rej_json = pim_rej_data["rejection_power_-211"]

print(f"[1] Extracted objectives:")
print(f"  -- gamma energy resolution = {gam_res_json}, type = {type(gam_res_json)}")
print(f"  -- e- eta resolution = {ele_res_json}, type = {type(ele_res_json)}")
print(f"  -- pi- rejection = {pim_rej_json}, type = {type(pim_rej_json)}")

# end =========================================================================
