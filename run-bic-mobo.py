# =============================================================================
## @file   run-bic-mobo.py
#  @author Derek Anderson
#  @date   09.25.2025
# -----------------------------------------------------------------------------
## @brief Main executable and wrapper script for
#    running the BIC-MOBO problem.
# =============================================================================

import argparse as ap
import pickle
import os
import subprocess

from ax.generation_strategy.generation_node import GenerationStep
from ax.generation_strategy.generation_strategy import GenerationStrategy
from ax.modelbridge.registry import Generators
from ax.service.ax_client import AxClient
from ax.service.utils.report_utils import exp_to_df
from scheduler import AxScheduler, JobLibRunner, SlurmRunner

import AID2ETestTools as att
import EICMOBOTestTools as emt
import interfaces as itf

def main(*args, **kwargs):
    """main

    Wrapper to run BIC-MOBO. The model
    and generation strategy are saved
    to both JSON and CSV files (model)
    and pickle files (generation) for
    downstream analysis.

    User can specify which runner to use
    with the -r option:

      joblib -- use joblib runner (default)
      slurm  -- use slurm runner
      panda  -- use panda runner (TODO)

    And can provide a JSON file to load
    an experiment from with the -x option

    Args:
      -r: specify runner (optional)
      -x: specify experiment to load (optional)
    """

    # set up arguments
    parser = ap.ArgumentParser()
    parser.add_argument("-r", "--runner", help = "Runner type", nargs = '?', const = 1, type = str, default = "joblib")
    parser.add_argument("-x", "--experiment", help = "JSON-serialized Ax experiment to load", nargs = '?', const = 1, type = str, default = None)
    parser.add_argument("-u", "--runconfig", help = "JSON config file for runtime options to use", nargs = '?', const = 1, type = str, default = None)
    parser.add_argument("-e", "--expconfig", help = "JSON config file for Ax options to use", nargs = '?', const = 1, type = str, default = None)
    parser.add_argument("-p", "--parconfig", help = "JSON config file for parameters to use", nargs = '?', const = 1, type = str, default = None)
    parser.add_argument("-o", "--objconfig", help = "JSON config file for objectives to use", nargs = '?', const = 1, type = str, default = None)
    parser.add_argument("-s", "--envscript", help = "Script to call to set environment variables", nargs= '?', const = 1, type = str, default = None)

    # grab arguments
    args = parser.parse_args()

    # if any config overrides provided,
    # update environment variables
    if args.runconfig is not None:
        os.environ['RUN_CFG'] = args.runconfig
    if args.expconfig is not None:
        os.environ['EXP_CFG'] = args.expconfig
    if args.parconfig is not None:
        os.environ['PAR_CFG'] = args.parconfig
    if args.objconfig is not None:
        os.environ['OBJ_CFG'] = args.objconfig

    # if an alternate environment script was provided,
    # grab path and run it
    mobo_path = os.getenv('BIC_MOBO')
    mobo_this = f"{mobo_path}/bin/this-mobo.tcsh"
    if args.envscript is not None:
        mobo_this = args.envscript
        subprocess.run(f"source {mobo_this}", shell = True)

    # grab paths to config files
    run_path = os.getenv('RUN_CFG')
    exp_path = os.getenv('EXP_CFG')
    par_path = os.getenv('PAR_CFG')
    obj_path = os.getenv('OBJ_CFG')

    # load relevant config files
    cfg_run = emt.ReadJsonFile(run_path)
    cfg_exp = emt.ReadJsonFile(exp_path)
    cfg_par = emt.ReadJsonFile(par_path)
    cfg_obj = emt.ReadJsonFile(obj_path)

    # translate parameter, objective options
    # into ax-compliant ones
    ax_pars, ax_par_cons = att.ConvertParamConfig(cfg_par)
    ax_objs, ax_obj_cons = att.ConvertObjectConfig(cfg_obj)

    # define generation strategy to use
    #   - TODO try bandit optimization
    gstrat = GenerationStrategy(
        steps = [
            GenerationStep(
                model = Generators.SOBOL,
                num_trials = cfg_exp["n_sobol"],
                min_trials_observed = cfg_exp["min_sobol"],
                max_parallelism = cfg_exp["n_sobol"]
            ),
            GenerationStep(
                model = Generators.BOTORCH_MODULAR,
                num_trials = -1,
                max_parallelism = cfg_exp["max_parallel_gen"]
            )
        ]
    )

    # either create or load ax experiment as needed
    ax_client = None
    if args.experiment == None:
        ax_client = AxClient(
            generation_strategy = gstrat,
            enforce_sequential_optimization = False
        )
        ax_client.create_experiment(
            name = cfg_exp["problem_name"],
            parameters = ax_pars,
            objectives = ax_objs,
            parameter_constraints = ax_par_cons
        )
    else:
        if os.path.isfile(args.experiment):
            ax_client = AxClient().load_from_json_file(args.experiment)
        else:
            raise FileNotFoundError(f"File {args.experiment} not found!")

    # set up runners
    runner = None
    match args.runner:
        case "joblib":
            runner = JobLibRunner(
                n_jobs = cfg_run["sched_n_jobs"],
                config = {
                    'tmp_dir' : cfg_run["run_path"]
                }
            )
        case "slurm":
            runner = SlurmRunner(
                slurm_template = f"{mobo_path}/configuration/template.slurm",
                init_env = [
                    f"source {mobo_this}",
                    f"source {cfg_run['conda']}",
                    f"conda activate {cfg_run['environment']}",
                    "conda list"
                ]
            )
        case _:
            raise ValueError("Unknown runner specified!")

    # set up scheduler
    scheduler = AxScheduler(
        ax_client,
        runner,
        config = {
            'job_output_dir' : cfg_exp["OUTPUT_DIR"],
        }
    )
    scheduler.set_objective_function(itf.RunObjectives)

    # run and report best parameters
    #best = scheduler.run_optimization(max_trials = cfg_exp["n_max_trials"])
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
