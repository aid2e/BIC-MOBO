# BIC-MOBO [Under construction]

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
- [ ] Run optimization locally on BIC simulation using scheduler
      with one objective, energy resolution
- [ ] Run workflow with one objective on hPC resources via
      SLURM using scheduler
- [ ] Implement second objective, electron-pion separation
- [ ] Run workflow with both objectives on HPC resources via
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
    4. And can be evolved to align with ongoing work in the [holistic
       optimization](https://github.com/aid2e/HolisticOptimization) example;

## Dependencies

- Python 3.11.5
- Conda or Mamba (eg. via [Miniforge](https://github.com/conda-forge/miniforge)) 
- [Ax](https://ax.dev)
- [EIC Software](https://eic.github.io)
- [AID2E Scheduler](https://github.com/aid2e/scheduler_epic)

## Code organization

This repository is structured like so:


  | `run_config.json` | defines paths to EIC software, components, executables to be used, etc. |
  | `problem_config.json` | defines metadata and parameters for optimization algorithms |
  | `parameters_config.json` | defines design parameters to optimize with |
  | `objectives` | collects analysis scripts to calculate objectives for optimize for |
  | `steering` | collects steering files for running single particle simulations |
  | `EICMOBOTestTools` | a python module which consolidates various tools for interfacing with the EIC software stack |

TODO: will be expanded/modified as development proceeds

## Installation

Before beginning, please make sure conda and/or mamba is installed. Once
ready, the environment for the problem can be set up via:

```
./create-environment
```

And activated via `conda`
```
conda activate bic-mobo
```

At any point, this environment can be deleted with
```
./remove-environment
```

Then, install the [AID2E scheduler](https://github.com/aid2e/scheduler_epic)
following the instructions in its repository.

## Running the framework

Before beginning, create a local installation of [the ePIC geometry
description](https://github.com/eic/epic) and compile it:
```
cd <where-the-geo-goes>
git clone git@github.com:eic/epic.git
cd epic
cmake -B build -S . -DCMAKE_INSTALL_PREFIX=install
cmake --build build
cmake --install build
```

Then, modify `run_config.json` so that the paths point to your
installations and relevent scripts, eg.
```
{
    "_comment"   : "Configures runtime options, and paths to EIC software components",
    "out_path"   : "<where-the-output-goes>/out",
    "run_path"   : "<where-the-running-goes>/run",
    "log_path"   : "<where-the-logs-go>/log",
    "eic_shell"  : "<path-to-your-script>/eic-shell",
    "epic_setup" : "<where-the-geo-goes>/epic/install/bin/thisepic.sh",
    "det_path"   : "<where-the-geo-goes>/epic/install/share/epic",
    "det_config" : "epic",
    "sim_exec"   : "npsim",
    "sim_input"  : {
        "location" : "<where-the-mobo-goes>/BIC-MOBO/steering",
        "type"     : "single"
    },
    "reco_exec"   : "eicrecon"
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
        "EcalBarrelClusters"
    ]
}
```

Where the angle brackets should be replaced with the appropriate
absolute paths. The values `det_path` and `det_config` should be
what `echo $DETECTOR_PATH` and `echo $DETECTOR_CONFIG` return after
sourcing your installation of the geometry.

TODO: fill in remainder when `main` is ready.
