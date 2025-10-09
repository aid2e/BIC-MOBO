# =============================================================================
## @file   RunObjectives.py
#  @author Derek Anderson
#  @date   10.09.2025
# -----------------------------------------------------------------------------
## @brief Script to run objectives.
#    Called by run-bic-mobo.py. 
# =============================================================================

import datetime
import os
import re
import subprocess

import EICMOBOTestTools as emt

# FIXME remove this when ready
def DoTestScript(*args, **kwargs):

    print(f"[0] CHECK CHECK starting trial")

    eResEle = 6.0
    for key, val in kwargs.items():
        print(f"  --> key = {key}, val = {val}, res = {eResEle}")
        eResEle = eResEle - val
    print(f"[1] CHECK CHECK finished trial")
    print(f"    objective is {eResEle}")

    return {
        "ElectronEnergyResolution" : eResEle
    }

def RunObjectives(*args, **kwargs):
    """RunObjectives

    Runs trial (simulation, reconstruction,
    and all analyses) for provided set of
    updated parameters.

    Args:
      args:   any positional arguments
      kwargs: any keyword arguments
    Returns:
      dictionary of objectives and their values
    """
    print("[0] CHECK CHECK starting trial")

    # create tag for trial
    time = str(datetime.datetime.now())
    time = re.sub(r'[.\-:\ ]', '', time)
    tag = f"AxTrial{time}"
    print(f"[1] CHECK CHECK tag is {tag}")

    # extract path to script being run currently
    main_path, main_file = emt.SplitPathAndFile(
        os.path.realpath(__file__)
    )
    print(f"[2] CHECK CHECK main path is")
    print(f"    {main_path}")

    # determine paths to config files
    #   -- FIXME this is brittle!
    run_path  = main_path + "/configuration/run.config"
    par_path  = main_path + "/configuration/parameters.config"
    obj_path  = main_path + "/configuration/objectives.config"
    print(f"[3] CHECK CHECK run config is")
    print(f"    {run_path}")

    # parse run config to extract path to eic-shell 
    cfg_run   = emt.ReadJsonFile(run_path)
    eic_shell = cfg_run["eic_shell"]
    print(f"[4] CHECK CHECK path to eic-shell is")
    print(f"    {eic_shell}")

    # create trial manager
    trial = emt.TrialManager(run_path,
                             par_path,
                             obj_path)

    # create and run script
    script, ofiles = trial.MakeTrialScript(tag, kwargs)
    subprocess.run([eic_shell, "--", script])

    # extract electron resolution 
    ofResEle = ofiles["ElectronEnergyResolution"].replace(".root", ".txt")
    eResEle  = None
    with open(ofResEle) as out:
        eResEle = float(out.read().splitlines()[0])

    # return dictionary of objectives
    return {
        "ElectronEnergyResolution" : eResEle
    }

if __name__ == "__main__":
#    RunObjectives()
    DoTestScript()

# end =========================================================================
