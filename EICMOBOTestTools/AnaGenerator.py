# =============================================================================
## @file    AnaGenerator.py
#  @authors Derek Anderson
#  @date    09.19.2025
# -----------------------------------------------------------------------------
## @brief Class to generate commands and scripts to run
#    analyses/objectives for a trial.
# =============================================================================

import os
import stat

from EICMOBOTestTools import ConfigParser
from EICMOBOTestTools import FileManager

class AnaGenerator:
    """AnaGenerator

    A class to generate commands and scripts
    to run analyses/objectives for a trial.
    """

    def __init__(self, run, ana):
        """constructor accepting arguments

        Args:
          run: runtime configuration file
          ana: objectives configuration file
        """
        self.cfgRun = ConfigParser.ReadJsonFile(run)
        self.cfgAna = ConfigParser.ReadJsonFile(ana)

    # TODO finish filling in
    def MakeMergeCommand(self, tag, label, analysis):
        """MakeMergeCommand

        """
        merged = FileManager.MakeOutName(tag, label, steer, analysis, "merged")

# end =========================================================================
