# =============================================================================
## @file   run-bic-mobo.py
#  @author Derek Anderson
#  @date   09.25.2025
# -----------------------------------------------------------------------------
## @brief Main executable and wrapper script for
#    running the BIC-MOBO problem.
# =============================================================================

import os
import subprocess

from ax.service.ax_client import AxClient, ObjectiveProperties
from scheduler import AxScheduler, JobLibRunner

import AID2ETestTools as att
import EICMOBOTestTools as emt

def RunObjectives(*args, **kwargs):
    # TODO
    #   - extract objectives from output
    #   - create and return dictionary
    #     of objectives

    # create tag for trial
    tag = "AxTrial" + str(RunObjectives.counter)
    RunObjectives.counter += 1

    # extract path to script being run currently
    main_path, main_file = emt.SplitPathAndFile(
        os.path.realpath(__file__)
    )

    # determine paths to config files
    #   -- FIXME this is brittle!
    run_path  = main_path + "/run_config.json"
    par_path  = main_path + "/parameters_config.json"
    obj_path  = main_path + "/objectives_config.json"

    # parse run config to extract path to eic-shell 
    cfg_run   = emt.ReadJsonFile(run_path)
    eic_shell = cfg_run["eic_shell"]

    # create trial manager
    trial = emt.TrialManager(run_path,
                             par_path,
                             obj_path)

    # create and run script
    script, ofiles = trial.MakeTrialScript(tag, kwargs)
    subprocess.run([eic_shell, "--", script])

    # dummy objective
    objective = 0
    for parVal in kwargs.values():
        objective = objective - parVal
    return {"ElectronEnergyResolution" : objective}

# make sure trial counter starts at 0
RunObjectives.counter = 0

def main():
    # TODO
    #   - save everything for analysis

    # load relevant config files
    cfg_exp = emt.ReadJsonFile("problem_config.json")
    cfg_par = emt.ReadJsonFile("parameters_config.json")
    cfg_obj = emt.ReadJsonFile("objectives_config.json")

    # translate parameter, objective options
    # into ax-compliant ones
    ax_pars = att.ConvertParamConfig(cfg_par)
    ax_objs = att.ConvertObjectConfig(cfg_obj)

    # create ax client
    ax_client = AxClient()
    ax_client.create_experiment(
        name = cfg_exp["problem_name"],
        parameters = ax_pars,
        objectives = ax_objs
    )

    # set up scheduler
    #   - TODO add switch to toggle slurm running
    runner    = JobLibRunner(n_jobs = -1)
    scheduler = AxScheduler(ax_client, runner)
    scheduler.set_objective_function(RunObjectives)

    # run and report best parameters
    best = scheduler.run_optimization(max_trials = 2)
    print("Optimization complete! Best parameters:\n", best)

if __name__ == "__main__":
   main()

# end =========================================================================
