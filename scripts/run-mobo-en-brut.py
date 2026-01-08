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

import os
import subprocess

import EICMOBOTestTools as emt

def MakeParamArgs(parlist):
    """MakeParamArgs

    Helper method to convert a
    list of values into a list
    of keyword arguments.

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

    Alternative wrapper to run BIC-MOBO.
    Eschews Ax to instead manually sample
    a set of specific parameterizations. 
    """
    # slurm options
    slopts = [
        "--account=eic",
        "--partition=ifarm",
        "--mail-user=dereka@jlab.org",
        "--mail-type=END,FAIL",
        "--time=24:00:00",
        "--mem=8G",
        "--cpus-per-task=4"
    ]

    # parameterizations
    params = []
    for stave2 in range(2):
        for stave3 in range(2):
            for stave4 in range(2):
                for stave5 in range(2):
                    for stave6 in range(2):
                        param = [stave2, stave3, stave4, stave5, stave6]
                        params.append(param)

    # extract path path to run config
    # and set runner paths
    mobo_path = os.getenv('BIC_MOBO')
    run_path  = mobo_path + "/configuration/run.config"
    obj_run   = mobo_path + "/interfaces/RunObjectives.py"

    # load relevant config files
    cfg_run = emt.ReadJsonFile(run_path)

    # create and run a Slurm job for each parameterization
    itrial = 0
    for param in params:

        # create trial tag and argument
        tag    = f"BrutTrial{itrial}"
        tagarg = f"--tag {tag}"

        # set ouput & error logs
        out = f"--output={cfg_run['log_path']}/{tag}.out"
        err = f"--error={cfg_run['log_path']}/{tag}.err"

        # generate parameter arguments 
        parargs = MakeParamArgs(param)

        # create slurm script
        slpath = cfg_run["run_path"] + f"/Run{tag}.sh"
        with open(slpath, 'w') as script:

          # add specified options
          script.write("#!/bin/bash\n")
          for opt in slopts:
              script.write(f"#SBATCH {opt}\n")

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
