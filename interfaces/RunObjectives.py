# =============================================================================
## @file   RunObjectives.py
#  @author Derek Anderson
#  @date   11.24.2025
# -----------------------------------------------------------------------------
## @brief Simple wrapper for deploying the
#    trial manager.
# =============================================================================

import argparse
import datetime
import os
import re
import subprocess

import EICMOBOTestTools as emt 

def RunObjectives(tag = None, **kwargs):
    """RunObjectives

    Runs trial (simulation, reconstruction,
    and all analyses) for provided set of
    updated parameters.

    Args:
      tag:    tag associated with trial
      kwargs: any keyword arguments (e.g. parameterization)
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
                             obj_path,
                             tag)

    # create and run script
    oFiles = trial.DoTrial(kwargs)

    # extract relevant objectives
    #   --> (should be 1st line in associated
    #       text files)
    objectives = dict()
    for obj, file in oFiles.items():
        oTxt = file.replace(".root", ".txt")
        oVal = None
        with open(oTxt, 'r') as out:
            oDat = out.readlines()
            oVal = float(oDat[0])
        objectives[obj] = oVal

    # return dictionary of objectives
    return objectives

# main ========================================================================

if __name__ == "__main__":

    # parse keyword arguments
    #   -- TODO automate adding parameters to parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", "--tag", help = "Trial tag", type = str, default = None)
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
    RunObjectives(args.tag, **params)

# end ===========================================================================
