# =============================================================================
## @file   RunObjectives.py
#  @author Derek Anderson
#  @date   10.31.2025
# -----------------------------------------------------------------------------
## @brief Python script to run objectives
#    and write out output. Called by the
#    run-mobo-en-brut.py script. 
# =============================================================================

import argparse
import os
import subprocess

import EICMOBOTestTools as emt

def RunObjectives(params, tag):
    """RunObjectives

    Runs trial (simulation, reconstruction,
    and all analyses) for provided set of
    updated parameters.

    Args:
      params: dictionary of parameters and values 
      tag:    tag for trial
    """

    # extract path to script being run currently
    main_path, main_file = emt.SplitPathAndFile(
        os.path.realpath(__file__)
    )

    # determine paths to config files
    #   -- FIXME this is brittle!
    run_path = main_path + "/configuration/run.config"
    par_path = main_path + "/configuration/parameters.config"
    obj_path = main_path + "/configuration/objectives.config"

    # parse run config to extract path to eic-shell
    cfg_run   = emt.ReadJsonFile(run_path)
    eic_shell = cfg_run["eic_shell"]

    # create trial manager
    trial = emt.TrialManager(run_path,
                             par_path,
                             obj_path)

    # create and run script
    script, ofiles = trial.MakeTrialScript(tag, params)
    subprocess.run([eic_shell, "--", script])

    # write out values of parameters to
    # output file(s) for analysis later
    ofResEle = ofiles["ElectronEnergyResolution"].replace(".root", ".txt")
    with open(ofResEle, 'a') as out:
        for param, value in params.items():
            out.write("\n")
            out.write(f"{value}")

    # extract electron resolution
    eResEle = None
    with open(ofResEle, 'r') as out:
        outData = out.readlines()
        eResEle = float(outData[0])

    # return dictionary of objectives
    return {
        "ElectronEnergyResolution" : eResEle
    }

if __name__ == "__main__":

    # parse keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", "--tag", help = "Trial tag", type = str)
    parser.add_argument("--enable_staves_2", "--enable_staves_2", help = "Stave 2 value", type = int)
    parser.add_argument("--enable_staves_3", "--enable_staves_3", help = "Stave 3 value", type = int)
    parser.add_argument("--enable_staves_4", "--enable_staves_4", help = "Stave 4 value", type = int)
    parser.add_argument("--enable_staves_5", "--enable_staves_5", help = "Stave 5 value", type = int)
    parser.add_argument("--enable_staves_6", "--enable_staves_6", help = "Stave 6 value", type = int)

    # grab arguments & create dictionary
    # of parameters
    args   = parser.parse_args()
    params = {
        "enable_staves_2" : args.enable_staves_2,
        "enable_staves_3" : args.enable_staves_3,
        "enable_staves_4" : args.enable_staves_4,
        "enable_staves_5" : args.enable_staves_5,
        "enable_staves_6" : args.enable_staves_6
    }

    # run objective
    RunObjectives(params, args.tag)

# end ===========================================================================
