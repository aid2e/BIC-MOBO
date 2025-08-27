# BIC-MOBO [Under construction]

An application of the AID2E framework to the ePIC Barrel Imaging Calorimeter (BIC).
As the BIC design is largely finalized and optimal, this exercise has three purposes:

  1. As a simple test of the AID2E framework to gain familiarity with the tool;
  2. As clarification of instructions on how to start, run, and utilize the tool.
  3. And as a demonstration of the framework, showing that it converges to a
     reasonable answer.

## Development strategy

Develoment will start with the toolkit as-is (no EIC components) and build
this new problem from the ground-up, using the
[dRICH-MOBO](https://github.com/aid2e/dRICH-MOBO) as reference.

### Steps:

- [x] Create simplified environment creation/deletion scripts
- [ ] Run toy example on BIC simulation using only Ax, AID2E, and
      dummy objectives
- [ ] Integrate and run toy example with aid2e scheduler
- [ ] Implement realistic objectives inspired by previous BIC studies
- [ ] Run optimization at scale.

### Design Goals:

- Minimal startup for new users;
- Integration with developing AID2E scheduler;
- Ability to run small tests locally (without scheduler), and large
  productions remotely (with scheduler);
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
