# =============================================================================
## @file   run-mobo-en-brut.py
#  @author Derek Anderson
#  @date   10.31.2025
# -----------------------------------------------------------------------------
## @brief Alternative exectuable and wrapper script 
#    for running the BIC-MOBO problem. Eschews Ax
#    and insteads samples a set of specific
#    parameterizations.
# =============================================================================

import argparse as ap
import os
import shutil
import subprocess

import EICMOBOTestTools as emt
import interfaces as itf

def MakeParamArgs(parlist):
    """MakeParamArgs

    Helper method to convert a list of
    values into a list of keyword
    arguments.

    Args:
      parlist: ordered list of parameter values
    Returns:
      list of keyword arguments specifying parameters
      and values
    """
    parargs = list() 
    istave  = 2
    for par in parlist:
        parargs.append(f"--enable_staves_{istave} {par}")
        istave += 1
    return parargs

def main(*args, **kwargs):
    """main

    Alternative wrapper to run BIC-MOBO. Eschews
    Ax to instead manually sample a set of
    specific parameterizations.

    User can override which configuration files
    to use with the -u, -p, -o, -s, -t options
    as detailed below.

    Args:
      -u: specify a run config to use
      -p: specify a parameter config to use
      -o: specify an objective config to use
      -s: specify an environment script to source
      -t: specify a SLURM template to use
    """
    # parse argsuments
    args = itf.ParseArguments()

    # load and grab relevant configs/paths
    run_cfg = itf.LoadConfig('run')
    obj_run = itf.GetMoboPath() + "/interfaces/RunObjectives.py"

    # parameterizations
    params = []
    for stave2 in range(2):
        for stave3 in range(2):
            for stave4 in range(2):
                for stave5 in range(2):
                    for stave6 in range(2):
                        param = [stave2, stave3, stave4, stave5, stave6]
                        params.append(param)

    # create and run a Slurm job for each parameterization
    itrial = 0
    for param in params:

        # create trial tag and argument
        tag    = f"BrutTrial{itrial}"
        tagarg = f"--tag {tag}"

        # set ouput & error logs
        out = f"--output={run_cfg['log_path']}/{tag}.out"
        err = f"--error={run_cfg['log_path']}/{tag}.err"

        # generate parameter arguments 
        parargs = MakeParamArgs(param)

        # copy slurm template to run directory
        slpath = run_cfg["run_path"] + f"/Run{tag}.sh"
        shutil.copyfile(itf.GetSlurmTemplate(), slpath)

        # append additional commands to slurm script
        with open(slpath, 'a') as script:

          # add output/error options
          script.write(f"#SBATCH {out}\n")
          script.write(f"#SBATCH {err}\n")

          # construct arguments for objective runner
          kwargs = f"{tagarg}"
          for pararg in parargs:
              kwargs += f" {pararg}"

          # now add line to run objective runner
          # with arguments
          script.write(f"\npython {obj_run} {kwargs}")
        
        # make script executable and submit it
        os.chmod(slpath, 0o777)
        subprocess.run(["sbatch", slpath])
        itrial += 1

if __name__ == "__main__":
   main()

# end =========================================================================
