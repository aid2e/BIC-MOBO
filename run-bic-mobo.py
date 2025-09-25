# =============================================================================
## @file   run-bic-mobo.py
#  @author Derek Anderson
#  @date   09.25.2025
# -----------------------------------------------------------------------------
#  Main executable and wrapper script for
#  running the BIC-MOBO problem.
# =============================================================================

from ax.service.ax_client import AxClient, ObjectiveProperties
from scheduler import AxScheduler, JobLibRunner

import EICMOBOTestTools as emt

def counter(function):
    """counter

    Decorator to count how many times
    a function's been called
    """
    def wrapped(parameterization):
        wrapped.calls += 1
        return function(parameterization)
    wrapped.calls = 0
    return wrapped

@counter
def RunObjectives(parameterization):
    # TODO
    #   - translate call # into tag
    #   - create trial manager and script
    #     to run
    #   - run script
    #   - extract objectives from output
    #   - create and return dictionary
    #     of objectives

def main():
    # TODO
    #   - load config files
    #   - translate parameters, objectives into
    #     ax-compliant ones
    #   - initialize ax client
    #   - set up scheduler and run
    #   - save everything for analysis

if __name__ == "__main__":
   main()

# end =========================================================================
