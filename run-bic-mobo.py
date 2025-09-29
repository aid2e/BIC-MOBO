# =============================================================================
## @file   run-bic-mobo.py
#  @author Derek Anderson
#  @date   09.25.2025
# -----------------------------------------------------------------------------
#  Main executable and wrapper script for
#  running the BIC-MOBO problem.
# =============================================================================

from ax.service.ax_client import AxClient, ObjectiveProperties
from scheduler import AxScheduler, JobLibRunner

import AID2ETestTools as att
import EICMOBOTestTools as emt

def counter(function):
    """counter

    Decorator to count how many times
    a function's been called
    """
    def wrapped(parameterization):
        wrapped.calls += 1
        return function(parameterization)
    wrapped.calls = 0
    return wrapped

#@counter
def RunObjectives(*args, **kwargs):
    # TODO
    #   - translate call # into tag
    #   - create trial manager and script
    #     to run
    #   - run script
    #   - extract objectives from output
    #   - create and return dictionary
    #     of objectives

    # dummy objective
    objective = 0
    for parVal in kwargs.values():
        objective -= parVal
    return {"ElectronEnergyResolution" : objective}

def main():
    # TODO
    #   - save everything for analysis

    # load config files
    cfg_run = emt.ReadJsonFile("run_config.json")
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
    best = scheduler.run_optimization(max_trials = 10)
    print("Optimization complete! Best parameters:\n", best)

if __name__ == "__main__":
   main()

# end =========================================================================
