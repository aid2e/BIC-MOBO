# =============================================================================
## @file   launch-mobo.py
#  @author Derek Anderson
#  @date   04.23.2026
# -----------------------------------------------------------------------------
## @brief Launches a sequence of slurm pilot jobs and
#    generates relevant problem.config, environment
#    scripts.
# =============================================================================

import json
import math
import os
import pathlib
import shutil
import subprocess

import interfaces as itf

def GetWaveExpName(iwave, wavedir):
    """GetWaveExpName

    Helper method to construct name of
    experiment config file for a wave.

    Args:
      iwave: wave index
    Returns:
      Created config file name (with path!)
    """
    cfg_path = pathlib.Path(itf.GetConfigPath('exp'))
    cfg_name = cfg_path.name.replace('.config', f'_{iwave}.config')
    cfg_wave = f"{wavedir}/{cfg_name}"
    return cfg_wave

def MakeWaveExpConfig(iwave, nparallel, ntotal, wavedir):
    """MakeWaveExpConfig

    Helper method to generate an experiment
    config file for a wave.

    Args:
      iwave:     wave index
      nparallel: no. of trials to run in parallel
      ntotal:    total no. of trials to run
      wavedir:   directory to store wave files
    Returns:
      Path to created config file
    """
    # load base config file, calculate max no. of
    # trials for wave
    cfg_data = itf.LoadConfig('exp')
    exp_name = cfg_data['problem_name']
    nfront   = min((iwave + 1) * nparallel, ntotal)

    # update wave, n_max_trials
    cfg_data['problem_name'] = f"{exp_name}_{iwave}"
    cfg_data['n_max_trials'] = nfront

    # dump updated config to wave directory
    cfg_wave = GetWaveExpName(iwave, wavedir)
    with open(cfg_wave, "w") as cfg:
        json.dump(cfg_data, cfg, indent = 4)

    # return path to created wave config
    return cfg_wave

def main(*args, **kwargs):
    """main

    Wrapper to run BIC-MOBO via slurm. Runs
    the problem in waves determined by
    n_max_trials and max_parallel_gen to
    avoid time limits on slurm jobs.
    """
    # parse argsuments
    args = itf.ParseArguments()

    # load relevant config and extract no. of parallel
    # and total trials to run
    run_cfg   = itf.LoadConfig('run')
    exp_cfg   = itf.LoadConfig('exp')
    nparallel = exp_cfg['max_parallel_gen']
    ntotal    = exp_cfg['n_max_trials']
    nwave     = math.floor(ntotal / nparallel)

    # create and submit a pilot job for each wave
    for iwave in range(0, nwave):

        # create a directory to hold wave files
        wavedir = run_cfg['run_path'] + f"/wave_{iwave}"
        if os.path.isdir(wavedir):
            shutil.rmtree(wavedir)
            os.mkdir(wavedir)
        else:
            os.mkdir(wavedir)

        # create a config file and experiment output to use for wave
        wave_cfg = MakeWaveExpConfig(iwave, nparallel, ntotal, wavedir)
        prev_exp = None
        if iwave > 0:
            prev_exp = f"{exp_cfg['OUTPUT_DIR']}/{exp_cfg['problem_name']}_exp_out_{iwave - 1}.json"

        # set output & error logs
        out = f"--output={run_cfg['log_path']}/pilot_{iwave}.out"
        err = f"--error={run_cfg['log_path']}/pilot_{iwave}.err"

        # copy slurm template to wave directory
        slpath = wavedir + f"/wave_{iwave}.sh"
        shutil.copyfile(itf.GetSlurmTemplate(), slpath)

        # append additional commands to slurm script
        with open(slpath, 'a') as script:

            # add output/error options
            script.write(f"#SBATCH {out}\n")
            script.write(f"#SBATCH {err}\n")

            # write command
            if iwave == 0:
                script.write(f"\npython {itf.GetMoboPath()}/run-bic-mobo.py -r slurm -e {wave_cfg}")
            else:
                script.write(f"\npython {itf.GetMoboPath()}/run-bic-mobo.py -r slurm -e {wave_cfg} -x {prev_exp}")

        # make script executable
        os.chmod(slpath, 0o777)

        # TODO submit with dependency here

if __name__ == "__main__":
   main()

# end =========================================================================
