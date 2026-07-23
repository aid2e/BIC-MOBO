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
import os
import subprocess

def CreateEnvironment(config: str, name: str) -> None:
    """CreateEnvironment

    Creates mobo conda/mamba environment
    on the provided yaml file.

    Usage:
      ./environment.py --create

    Args:
      config: yaml configuration file
      name:   name of environment
    """
    # create environment
    print(f"Creating environment based on {config}...")
    os.system(f"conda env create -f {config}")

    # announce creation
    print("\nEnvironment created successfully!")
    print(f"To activate: conda activate {name}")

    # then generate relevant scripts to set
    # environment variables
    subprocess.run('conda run -n bic-fw-test python -c "import os;from BICLowQ2.AID2ETools import MakeThisMoboScripts;MakeThisMoboScripts(os.getcwd())"', shell=True)

def RemoveEnvironment(name: str) -> None:
    """RemoveEnvironment

    Removes a conda/mamba environment with
    the provided name.

    Usage:
      ./environment.py --remove

    Args:
      name: name of environment to remove
    """
    os.system(f"conda remove -n {name} --all")

if __name__ == "__main__":

    parser = ap.ArgumentParser()
    parser.add_argument("--create", action = 'store_true')
    parser.add_argument("--remove", action = 'store_true')
    parser.add_argument("--panda", action = 'store_true')
    args = parser.parse_args()

    if args.create:

        # 1st set up environment
        if args.panda:
            CreateEnvironment("bic-mobo-panda.yml", "bic-fw-test")
        else:
            CreateEnvironment("bic-mobo.yml", "bic-fw-test")
            print("\nNote: To add PanDA/iDDS support later, run:")
            print("  conda activate bic-fw-test")
            print("  pip install -e .[panda]")
            print("  pip install 'git+https://github.com/aid2e/scheduler_epic.git[panda]'")

    if args.remove:
        RemoveEnvironment("bic-fw-test")

# end =========================================================================
