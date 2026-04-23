# =============================================================================
## @file   launch-mobo.py
#  @author Derek Anderson
#  @date   04.23.2026
# -----------------------------------------------------------------------------
## @brief Launches a sequence of slurm pilot jobs and
#    generates relevant problem.config, environment
#    scripts.
# =============================================================================

# ----------------------------------
# REF FROM LUMO:
# ----------------------------------
# counter = 0
# for i from 1 to X:
#     counter = min(counter + Y, Z)
#     print(counter)
# ----------------------------------
# def job_waves(total_jobs, max_per_wave, cap):
#     """
#     total_jobs: X (number of iterations/waves)
#     max_per_wave: Y (max jobs per wave)
#     cap: Z (maximum total jobs)
#     """
#     waves = []
#     for i in range(1, total_jobs + 1):
#         cumulative = min(i * max_per_wave, cap)
#         waves.append(cumulative)
#     return waves
# 
# Example
#   >>> print(job_waves(3, 6, 15))  # Output: [6, 12, 15]
# ----------------------------------
# TODO
#   - Extract relevant paths
#   - Determine number of chunks
#   - Generate this-mobo, problem
#     config, & job script for
#     each chunk
#   - submit each job
# ----------------------------------

def main(*args, **kwargs):
    """main

    Wrapper to run BIC-MOBO via slurm. Runs
    the problem in chunks determined by
    n_max_trials and max_parallel_gen to
    avoid time limits on slurm jobs.
    """
    # slurm options
    #  - FIXME use slurm template instead!
    options = [
        "--account=<your-account>",
        "--partition=<your-partition>",
        "--mail-user=<your-email-address>",
        "--mail-type=END,FAIL",
        "--time=24:00:00",
        "--mem=8G",
        "--cpus-per-task=4",
        "--output=<where-the-logs-go>/pilot.out",
        "--error=<where-the-logs-go>/pilot.err",
    ]

if __name__ == "__main__":
   main()

# end =========================================================================
