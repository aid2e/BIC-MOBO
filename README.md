# BIC-MOBO [Under Construction]

An application of the AID2E framework to the ePIC Barrel Imaging Calorimeter (BIC).
As the BIC design is largely finalized and optimal, this exercise has three purposes:

  1. As a simple test of the AID2E framework to gain familiarity with the tool;
  2. As clarification of instructions on how to start, run, and utilize the tool.
  3. And as a demonstration of the framework, showing that it converges to a
     reasonable answer.

## Development strategy

Develoment will proceeding by building this new problem from the ground-up, using
the [dRICH-MOBO](https://github.com/aid2e/dRICH-MOBO) as reference and leveraging
the [AID2E scheduler](https://github.com/aid2e/scheduler_epic).

### Steps:

- [x] Create simplified environment creation/deletion scripts
- [x] Run optimization locally on BIC simulation using scheduler
      with one objective, energy resolution
- [x] Run workflow with one objective on hPC resources via
      SLURM using scheduler
- [x] Implement second objective, electron-pion separation
- [x] Run workflow with both objectives on HPC resources via
      PANDA using scheduler

### Design Goals:

- Integration with [AID2E scheduler](https://github.com/aid2e/scheduler_epic);
- Both small-scale, local tests and larger-scale, remote tests are able to
  be run easily
- Modified EIC software interface is:
    1. Able to handle arbitrary numbers of subsytems to modify,
    2. Able to be easily factorized and deployed in other problems,
    3. Able to handle modifying reconstruction parameters (stretch
       goal);
    4. And can be evolved to align with ongoing work in the [holistic optimization](https://github.com/aid2e/HolisticOptimization)
       example;

## Dependencies

- Python 3.11.5
- Matplotlib
- Numpy
- Conda or Mamba (eg. via [Miniforge](https://github.com/conda-forge/miniforge)) 
- [EIC Software](https://eic.github.io)
- [PanDA](https://pandawms.org) (optional)
- [BIC/LowQ2 framework](https://github.com/aid2e/BICLowQ2-framework)

## Code organization

This repository is structured like so:

  | File/Directory | Description |
  |----------------|-------------|
  | `bic-mobo.yml` | conda/mamba environment file |
  | `environment.py` | script to create/remove bic-mobo conda/mamba environment |
  | `run-bic-mobo.py` | wrapper script and point-of-entry to the problem |
  | `configurations` | collects various configuration files that define the problem |
  | `objectives` | collects analysis scripts to calculate objectives for optimize for |
  | `steering` | collects steering/macro files for running simulations |
  | `examples` | collects of example config files, scripts, etc. for illustrating some of the extended functionality |
  | `scripts` | collects various scripts useful for running, testing, etc. |
  | `tests` | collects test scripts for unit tests |

There are four configuration files which define the parameters of the problem.

  | File | Description |
  |------|-------------|
  | `run.config` | defines paths to EIC software, components, executables to be used, etc. |
  | `problem.config` | defines metadata and parameters for optimization algorithms |
  | `parameters.config` | defines design parameters to optimize with |
  | `objectives.config` | defines objectives to optimize for |

## Installation

Before beginning, please make sure conda and/or mamba is installed. Once
ready, the environment for the problem can be set up via:

```bash
./environment.py --create
```

And activated via `conda`
```bash
conda activate bic-mobo
```

At any point, this environment can be deleted with
```bash
./environment.py --remove
```

Lastly, you'll need to make sure the `eic-shell` is available on your
machine.  You can find instructions to do so [here](https://eic.github.io/tutorial-setting-up-environment/).

## Running the framework

Before running, make sure you source one of the generated scripts
in `./bin` to set appropriate environment variables:
```bash
source bin/this-mobo.sh
```

Subsitute the appropriate script for your shell.  Note that these
can be modified to point to other config files as needed.  For
example, if you wanted to run with a different parameter file
you could modify the scripts such that:
```bash
export PAR_CFG=$THIS_MOBO/configuration/different_parameters.config
```

(Modify as needed for the other scripts) These can also be changed
at runtime using the options described [here](https://github.com/aid2e/BICLowQ2-framework/blob/main/src/BICLowQ2/AID2ETools/OptionParser.py#L84).

Then, create a local installation of [the ePIC geometry description](https://github.com/eic/epic):
```bash
cd <where-the-geo-goes>
git clone git@github.com:eic/epic.git
```

Then, modify `configurations/run.config` accordingly so that the paths point to your
installations and relevent scripts, e.g.
```json
{
    "_comment"      : "Configures runtime options, and paths to EIC software components",
    "conda"         : "<path-to-your-script>/conda.sh", # <<< for example /home/<username>/.miniforge3/etc/profile.d
    "environment"   : "bic-mobo",
    "out_path"      : "$THIS_MOBO/out",
    "run_path"      : "$THIS_MOBO/run",
    "log_path"      : "$THIS_MOBO/log",
    "eic_shell"     : "$THIS_MOBO/run_singularity.sh", # <<< CHANGE THIS IF NOT USING PANDA, use the path to your eic-shell
    "overlap_check" : "checkOverlaps",
    "epic_setup"    : "$THIS_MOBO/epic/install/bin/thisepic.sh", # <<< might need to adjust
    "det_path"      : "$THIS_MOBO/epic/install/share/epic", # <<< might need to adjust
    "cmake_path"    : "$THIS_MOBO/epic", # <<< might need to adjust
    "det_config"    : "epic",
    "sim_exec"      : "npsim",
    "sim_input"     : {
        "single_electron" : {
            "location" : "$THIS_MOBO/steering/electron",
            "type"     : "gun"
        },
        "single_piminus" : {
            "location" : "$THIS_MOBO/steering/piminus",
            "type"     : "gun"
        },
        "single_pizero" : {
            "_comment" : "currently unused",
            "location" : "$THIS_MOBO/steering/pizero",
            "type"     : "gun"
        },
        "single_gamma" : {
            "_comment" : "currently unused",
            "location" : "$THIS_MOBO/steering/gammma",
            "type"     : "gun"
        }
    },
    "rec_exec"    : "eicrecon",
    "rec_collect" : [
        "MCParticles",
        "GeneratedParticles",
        "EcalBarrelScFiRawHits",
        "EcalBarrelScFiRawHitAssociations",
        "EcalBarrelScFiRecHits",
        "EcalBarrelScFiClusters",
        "EcalBarrelScFiClusterAssociations",
        "EcalBarrelImagingRawHits",
        "EcalBarrelImagingRawHitAssociations",
        "EcalBarrelImagingRecHits",
        "EcalBarrelImagingClusters",
        "EcalBarrelImagingClusterAssociations",
        "EcalBarrelClusters",
        "EcalBarrelClusterAssociations",
        "EcalBarrelTruthClusters",
        "EcalBarrelTruthClusterAssociations"
    ],
    "sched_n_jobs"        : 1,
    "monitoring_interval" : 30
}
```

Notice the `$THIS_MOBO` variable: this points to the directory holding the
`bin/this-mobo.*` scripts.  It can be used to specify paths relative to
the directory the wrapper script is in.

Once appropriately configured, the optimization can be run in 3 modes:
1. Locally with Joblib
2. Remotely with a single Slurm monitoring job
3. Remotely in waves with a sequence of Slurm monitoring jobs.
4. Remotely via 32 slurm jobs to sample the entire design space.

**(1) Local Running:**
```bash
python run-bic-mobo.py
```

**(2) Single Monitoring Job Running:**
```bash
python run-bic-mobo.py -l
```

**(3) Multi-Monitoring Job Running:**
```bash
python run-bic-mobo.py -w
```

**(4) Manual-Sampling:**
```bash
python run-bic-mobo.py -b
```
