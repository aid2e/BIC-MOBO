import logging


# This file will be imported to load the objective function at remote sites in PanDA
# to avoid excuting the whole file, __name__ == "__main__" must be used.
# There is another way to only ship the codes of the objective function to remote sites.
# However, if this objective function calls some other functions, this way of only shipping
# the function codes will not work.
if __name__ == "__main__":
    # move imports here
    # so the remote execution will not import these libraries
    from ax.service.ax_client import AxClient, ObjectiveProperties
    from scheduler import AxScheduler, PanDAiDDSRunner
    from scheduler.utils.common import setup_logging
    from objectives.simple_objective import objective_function
    setup_logging(log_level="debug")

    logging.debug("setup ax client")
    # Initialize Ax client
    ax_client = AxClient()

    logging.info("Creating experiment")

    # Define your parameter space
    ax_client.create_experiment(
        name="my_experiment",
        parameters=[
            {
                "name": "x",
                "type": "range",
                "bounds": [0.0, 1.0],
                "value_type": "float",
            },
            {
                "name": "y",
                "type": "range",
                "bounds": [0.0, 1.0],
                "value_type": "float",
            },
        ],
        objectives={"objective": ObjectiveProperties(minimize=True)},
    )

    logging.info("defining objectives")

    # PanDA attributes
    '''
    init_env = [
        "source /cvmfs/unpacked.cern.ch/registry.hub.docker.com/fyingtsai/eic_xl:24.11.1/opt/conda/setup_mamba.sh;"
        "source /cvmfs/unpacked.cern.ch/registry.hub.docker.com/fyingtsai/eic_xl:24.11.1/opt/conda/dRICH-MOBO//MOBO-tools/setup_new.sh;"
        "command -v singularity &> /dev/null || export SINGULARITY=/cvmfs/oasis.opensciencegrid.org/mis/singularity/current/bin/singularity;"
        "export AIDE_HOME=$(pwd);"
        "export PWD_PATH=$(pwd);"
        'export SINGULARITY_OPTIONS="--bind /cvmfs:/cvmfs,$(pwd):$(pwd)"; '
        "export SIF=/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:24.11.1-stable; export SINGULARITY_BINDPATH=/cvmfs,/afs; "
        "env; "
    ]
    '''
    init_env = [
        "command -v singularity &> /dev/null || export SINGULARITY=/cvmfs/oasis.opensciencegrid.org/mis/singularity/current/bin/singularity;",
        "export AIDE_WORKDIR=$(pwd);",
        "export SIF=/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly;",
        "echo AIDE_WORKDIR: ${AIDE_WORKDIR};",

        # Install micromamba (minimal)
        "export MAMBA_ROOT_PREFIX=${AIDE_WORKDIR}/micromamba;",
        "export MAMBA_EXE=${MAMBA_ROOT_PREFIX}/bin/micromamba;",
        "mkdir -p ${MAMBA_ROOT_PREFIX}/bin;",
        'curl -Ls https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xj -C ${MAMBA_ROOT_PREFIX} bin/micromamba;',
        "chmod -R a+rx ${MAMBA_ROOT_PREFIX};",
        # Install Python 3.13
        "${MAMBA_EXE} install -y -r ${MAMBA_ROOT_PREFIX} -n base -c conda-forge python=3.13;",
        "${MAMBA_EXE} clean -a -y;",
        # Activate micromamba and install packages via pip
        'eval \"$(${MAMBA_EXE} shell hook -s posix)\";',
        "micromamba activate base;",
        "pip install pandas seaborn botorch ax-platform==1.0.0 numpy matplotlib torch;",

        # Make sure to use mamba python
        'export PATH=${MAMBA_ROOT_PREFIX}/bin:$PATH;',

        # Echo python being used
        'echo \"python version being used\" $(python --version; which python);',

        # Clone epic
        "git clone --depth 1 https://github.com/eic/epic.git ${AIDE_WORKDIR}/epic;",

        # Create build/install dirs WITHOUT changing cwd
        "mkdir -p ${AIDE_WORKDIR}/epic/build ${AIDE_WORKDIR}/epic/install;",

        # Build epic inside singularity WITHOUT cd side-effects
        '${SINGULARITY} exec --bind ${AIDE_WORKDIR}:${AIDE_WORKDIR} ${SIF} /bin/bash -c "cmake -B ${AIDE_WORKDIR}/epic/build -S ${AIDE_WORKDIR}/epic -DCMAKE_INSTALL_PREFIX=${AIDE_WORKDIR}/epic/install && cmake --build ${AIDE_WORKDIR}/epic/build && cmake --install ${AIDE_WORKDIR}/epic/build";',

        # Singularity setup
        'export SINGULARITY_OPTIONS="--bind /cvmfs:/cvmfs,${AIDE_WORKDIR}:${AIDE_WORKDIR}";',
        "export SIF=/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly;",
        "export SINGULARITY_BINDPATH=/cvmfs;",

        # Set MOBO path
        "export BIC_MOBO=${AIDE_WORKDIR};",
        "echo BIC_MOBO path: $BIC_MOBO;",

        # Debug
        "env;",
        "pwd;",
        "python --version; which python;",
        "echo \"Testing objective function execution:\";",
        'python -c "import objectives.simple_objective; print(objectives.simple_objective.objective_function(0.1, 0.2))";',
        'echo "END OF ENVIRONMENT SETUP;"',
    ]
    init_env = " ".join(init_env)
    dset_name_prefix = "user.abashyal2"+".simple-panda-idds"
    panda_attrs = {
        "name": dset_name_prefix,
        "init_env": init_env,
        "cloud": "US",
        "queue": "BNL_PanDA_1", # Test runs locally # Other options are BNL_OSG_PanDA_2, BNL_OSG_PanDA_1, BNL_PanDA_1, BNL_PanDA_2
        "source_dir":None,
        "source_dir_parent_level":1,
        "exclude_source_files":[
            r"(^|/)\.[^/]+", # hidden files and directories
            "out","run","epic","share","calibrations","fieldmaps","gdml",
            "scheduler_epic",
            "doc*",
            ".*log","examples",
            ".*txt","__pycache__" # calibrations dir has sym links
        ],
        "max_walltime":3600,
        "core_count":2,
        "total_memory":8000,
        "enable_separate_log":True,
        "job_dir":None,
    }

    # Create a runner
    runner = PanDAiDDSRunner(**panda_attrs)
    logging.info(f"created runner: {runner}")

    # Create the scheduler
    scheduler = AxScheduler(ax_client, runner)
    logging.info(f"created scheduler: {scheduler}")

    # Set the objective function
    scheduler.set_objective_function(objective_function)

    logging.info("running optimization")
    # Run the optimization
    best_params = scheduler.run_optimization(max_trials=10)
    print("Best parameters:", best_params)
