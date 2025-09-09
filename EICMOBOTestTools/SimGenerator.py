# =============================================================================
## @file    SimGenerator.py
#  @authors Derek Anderson, building off work by
#           Connor Pecar
#  @date    09.09.2025
# -----------------------------------------------------------------------------
## @brief Class to generate commands and scripts to run
#    Geant4 simulation via npsim or ddsim for a trial.
# =============================================================================

import os
import shutil
import sys

from EICMOBOTestTools import ConfigParser
from EICMOBOTestTools import FileManager

class SimGenerator:
    """SimGenerator

    A class to generate commands and scripts
    to run Gean4 simulation via npsim or
    ddsim for a trial.
    """

    def __init__(self, enviro):
        """constructor accepting arguments

        Args:
          enviro: environment configuration file
          params: parameter configuration file
        """
        self.cfgEnviro = ConfigParser.ReadJsonFile(enviro)

    def MakeCommand(self, tag, label, path, steer, inType): 
        """MakeCommand

        Generates command to run sim executable
        (npsim, ddsim) on provided inputs for
        a given tag.

        Args:
          tag:    the tag associated with the current trial
          label:  the label associated with the input
          steer:  the input steering file
          inType: the type of input (e.g. gun, hepmc, etc.)
        Returns:
          command to be run
        """

        # construct output name
        steeTag = FileManager.ConvertSteeringToTag(steer)
        outFile = FileManager.MakeSimOutName(tag, label, steeTag)

        # create arguments for command
        #   --> n.b. this assumes the DETECTOR_CONFIG variable
        #       has already been set to the trial's config file
        compact = " --compactFile $DETECTOR_PATH/$DETECTOR_CONFIG.xml" 
        steerer = " --steeringFile " + path + "/" + steer
        output  = " --outputFile " + self.cfgEnviro["out_path"] + "/" + outFile

        # construct most of command
        command = self.cfgEnviro["sim_exec"] + compact + steerer
        if inType is "gun":
            command = command + " -G "

        # return command with output file attached
        command = command + output
        return command

    def MakeScript(self, tag, label, steer, config, command):
        """MakeScript

        Generates single script to run sim executable
        (npsim, ddsim) on provided inputs for a given
        tag.

        Args:
          tag:     the tag associated with the current trial
          label:   the label associated with the input
          steer:   the input steering file
          config:  the detector config file to use
          command: the command to be run
        Returns:
          path to the script created
        """

        # construct script name
        steeTag   = FileManager.ConvertSteeringToTag(steer)
        simScript = FileManager.MakeSimScriptName(tag, label, steeTag)
        simPath   = self.cfgEnviro["run_path"] + "/" + simScript

        # make commands to set detector config
        setConfig = "DETECTOR_CONFIG=" + config

        # open script name
        with open(simPath, 'w') as script:
            script.write("#!/bin/bash\n\n")
            script.write(setConfig + "\n\n")
            script.write(command)

        # return path to script
        return simPath

# end =========================================================================
