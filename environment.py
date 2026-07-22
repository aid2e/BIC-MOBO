#!/usr/bin/env python
# =============================================================================
## @file    environment.py
#  @authors Derek Anderson,
#           Amit Bashyal
#  @date    07.22.2026
# -----------------------------------------------------------------------------
## @brief Small python script to manage environments.
#
#  @usage
#    ./environment.py --create (to create environment)
#    ./environment.py --remove (to remove environment)
#    ./environment.py --create --panda (to create environment w/ PanDA)
# =============================================================================

import argparse as ap
import subprocess
import os

def CreateEnvironment(config: str, name: str) -> None:
    """Creates mobo conda/mamba environment
    on the provided yaml file.

    Usage:
      ./environment.py --create

    Args:
      config: yaml configuration file
      name:   name of environment
    """
    # create environment
    print(f"Creating environment based on {config}...")
    subprocess.run(f"conda env create -f {config}")

    # announce completion
    print("\nEnvironment created successfully!")
    print(f"To activate: conda activate {name}")

def RemoveEnvironment(name: str) -> None:
    """RemoveEnvironment

    Removes a conda/mamba environment with
    the provided name.

    Usage:
      ./environment.py --remove

    Args:
      name: name of environment to remove
    """
    subprocess.run(f"conda remove -n {name} --all")

if __name__ == "__main__":

    parser = ap.ArgumentParser()
    parser.add_argument("--create", action = 'store_true')
    parser.add_argument("--remove", action = 'store_true')
    parser.add_argument("--panda", action = 'store_true')
    args = parser.parse_args()

    if args.create:

        # 1st set up environment
        if args.panda:
            CreateEnvironment("bic-mobo-panda.yml", "bic-mobo")
        else:
            CreateEnvironment("bic-mobo.yml", "bic-mobo")
            print("\nNote: To add PanDA/iDDS support later, run:")
            print("  conda activate bic-mobo")
            print("  pip install -e .[panda]")
            print("  pip install 'git+https://github.com/aid2e/scheduler_epic.git[panda]'")

        # then generaate relevant scripts to set
        # environment variables
        from BICLowQ2.AID2ETools import MakeThisMoboScripts
        MakeThisMoboScripts(os.cwd())

    if args.remove:
        RemoveEnvironment("bic-mobo")

# end =========================================================================
