# =============================================================================
## @file   RunObjectives.py
#  @author Derek Anderson
#  @date   10.31.2025
# -----------------------------------------------------------------------------
## @brief Python script to run objectives
#    and return values.
# =============================================================================

import argparse
import datetime
import os
import re
import subprocess

import EICMOBOTestTools as emt

#def RunObjectives(params, tag):
def RunObjectives(**kwargs):
    """RunObjectives

    Runs trial (simulation, reconstruction,
    and all analyses) for provided set of
    updated parameters.

    Args:
      kwargs: any keyword arguments
    Returns:
      dictionary of objectives and their values
    """

    # extract path to script being run currently
    main_path, main_file = emt.SplitPathAndFile(
        os.path.realpath(__file__)
    )

    # determine paths to config files
    #   -- FIXME this is brittle!
    run_path = main_path + "/../configuration/run.config"
    par_path = main_path + "/../configuration/parameters.config"
    obj_path = main_path + "/../configuration/objectives.config"

    # create trial manager
    trial = emt.TrialManager(run_path,
                             par_path,
                             obj_path)

    # create and run script
    oFiles = trial.DoTrial(kwargs)

    # extract electron resolution
    #   -- TODO automate this
    oResEle = oFiles["ElectronEnergyResolution"].replace(".root", ".txt")
    eResEle = None
    with open(oResEle, 'r') as out:
        outData = out.readlines()
        eResEle = float(outData[0])

    # return dictionary of objectives
    #   -- TODO and automate this
    return {
        "ElectronEnergyResolution" : eResEle
    }

if __name__ == "__main__":

    # parse keyword arguments
    #   -- TODO automate adding parameters to parser
    parser = argparse.ArgumentParser()
    #parser.add_argument("--tag", "--tag", help = "Trial tag", type = str)
    parser.add_argument("--enable_staves_2", "--enable_staves_2", help = "Stave 2 value", type = int)
    parser.add_argument("--enable_staves_3", "--enable_staves_3", help = "Stave 3 value", type = int)
    parser.add_argument("--enable_staves_4", "--enable_staves_4", help = "Stave 4 value", type = int)
    parser.add_argument("--enable_staves_5", "--enable_staves_5", help = "Stave 5 value", type = int)
    parser.add_argument("--enable_staves_6", "--enable_staves_6", help = "Stave 6 value", type = int)

    # grab arguments & create dictionary
    # of parameters
    #   -- TODO this can also be automated
    args   = parser.parse_args()
    params = {
        "enable_staves_2" : args.enable_staves_2,
        "enable_staves_3" : args.enable_staves_3,
        "enable_staves_4" : args.enable_staves_4,
        "enable_staves_5" : args.enable_staves_5,
        "enable_staves_6" : args.enable_staves_6
    }

    # run objective
    #RunObjectives(params, args.tag)
    RunObjectives(**vars(params))

# end ===========================================================================
