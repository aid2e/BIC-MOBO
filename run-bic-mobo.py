# =============================================================================
## @file   run-bic-mobo.py
#  @author Derek Anderson
#  @date   09.25.2025
# -----------------------------------------------------------------------------
## @brief Main executable and wrapper script for
#    running the BIC-MOBO problem.
# =============================================================================

import os
import pickle
import subprocess

from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.service.utils.report_utils import exp_to_df
from scheduler import AxScheduler, JobLibRunner

import AID2ETestTools as att
import EICMOBOTestTools as emt

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

    # create tag for trial
    tag = "AxTrial" + str(RunObjectives.counter)
    RunObjectives.counter += 1

    # extract path to script being run currently
    main_path, main_file = emt.SplitPathAndFile(
        os.path.realpath(__file__)
    )

    # determine paths to config files
    #   -- FIXME this is brittle!
    run_path  = main_path + "/configuration/run.config"
    par_path  = main_path + "/configuration/parameters.config"
    obj_path  = main_path + "/configuration/objectives.config"

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

    # extract electron resolution 
    ofResEle = ofiles["ElectronEnergyResolution"].replace(".root", ".txt")
    eResEle  = None
    with open(ofResEle) as out:
        eResEle = float(out.read().splitlines()[0])

    # return dictionary of objectives
    return {
        "ElectronEnergyResolution" : eResEle
    }

# make sure trial counter starts at 0
RunObjectives.counter = 0

def main():
    """main

    Wrapper to run BIC-MOBO. The model
    and generation strategy are saved
    to both JSON and CSV files (model)
    and pickle files (generation) for
    downstream analysis.

    User can
    specify which runner to use with
    the -r option:

      joblib -- use joblib runner (default)
      slurm  -- use slurm runner (TODO)
      panda  -- use panda runner (TODO)

    Args:
      -r: specify runner (optional)
    """
    # extract path to script being run currently
    #   - FIXME this should get automated!
    main_path, main_file = emt.SplitPathAndFile(
        os.path.realpath(__file__)
    )
    exp_path  = main_path + "/configuration/problem.config"
    par_path  = main_path + "/configuration/parameters.config"
    obj_path  = main_path + "/configuration/objectives.config"

    # load relevant config files
    cfg_exp = emt.ReadJsonFile(exp_path)
    cfg_par = emt.ReadJsonFile(par_path)
    cfg_obj = emt.ReadJsonFile(obj_path)

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
    best = scheduler.run_optimization(max_trials = 720)
    print("Optimization complete! Best parameters:\n", best)

    # create paths to output files
    oPathBase = cfg_exp["OUTPUT_DIR"] + "/" + cfg_exp["problem_name"]
    oPathCSV  = oPathBase + "_exp_out.csv"
    oPathJson = oPathBase + "_exp_out.json"
    oPathPikl = oPathBase + "_gen_out.pkl"

    # grab experiment and generation strategy
    # for output
    exp   = ax_client._experiment
    gen   = ax_client._generation_strategy
    dfExp = exp_to_df(exp)

    # save outcomes and experiment
    # for downstream analysis
    dfExp.to_csv(oPathCSV)
    ax_client.save_to_json_file(oPathJson)
    with open(oPathPikl, 'wb') as file:
        pickle.dump(gen.model, file)

if __name__ == "__main__":
   main()

# end =========================================================================
