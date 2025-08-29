# BIC-MOBO [Under construction]

An application of the AID2E framework to the ePIC Barrel Imaging Calorimeter (BIC).
As the BIC design is largely finalized and optimal, this exercise has three purposes:

  1. As a simple test of the AID2E framework to gain familiarity with the tool;
  2. As clarification of instructions on how to start, run, and utilize the tool.
  3. And as a demonstration of the framework, showing that it converges to a
     reasonable answer.

## Development strategy

Develoment will build this new problem from the ground-up, using the
[dRICH-MOBO](https://github.com/aid2e/dRICH-MOBO) as reference.

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

- Minimal startup for new users;
- Integration with developing AID2E scheduler;
- Ability to run small tests locally  and large productions remotely 
  (both can be handled by scheduler);
- Clear separation of interface to toolkit and definition of problem;
- And clear separation of EIC-specific analysis/software components and AID2E
  framework components.

## Dependencies

- Python 3.11.5
- Conda or Mamba (eg. via [Miniforge](https://github.com/conda-forge/miniforge)) 
- [Ax](https://ax.dev)
- [EIC Software](https://eic.github.io)
- [AID2E Scheduler](https://github.com/aid2e/scheduler_epic)

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

## Running the framework

TODO: fill in here
