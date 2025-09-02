# =============================================================================
## @file    CompactEditor.py
#  @authors Connor Pecar,
#           with modifications by Derek Anderson
#  @date    09.02.2025
# -----------------------------------------------------------------------------
## @brief Class to generate and edit modified compact
#    files for a trial.
# =============================================================================

import json
import math # FIXME maybe not needed?
import os
import shutil
import sys
import xml.etree.ElementTree as et

from EICMoboTools import ConfigParser

class CompactEditor
    """CompactEditor

    A class to generate and edit modified
    compact files for a trial.
    """

    ## environment configuration file
    cfgEnviro

    ## parameter configuration file
    cfgParams

    ## list of geometry parameters
    #  to edit
    parameters

    def __init__():
        """default constructor
        """
        cfgEnviro = ""
        cfgParams = ""
        parameters = []

    def __init__(enviro, params):
        """constructor accepting arguments

        Keyword arguments
        enviro -- environment configuration file
        params -- parameter configuration file
        """
        cfgEnviro = enviro
        cfgParams = params
        parameters = []

# end =========================================================================
