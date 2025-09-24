# =============================================================================
## @file    SimGenerator.py
#  @authors Derek Anderson
#  @date    09.09.2025
# -----------------------------------------------------------------------------
## @brief Class to generate commands and scripts to run
#    Geant4 simulation via npsim or ddsim for a trial.
# =============================================================================

import os

from EICMOBOTestTools import ConfigParser
from EICMOBOTestTools import FileManager

class SimGenerator:
    """SimGenerator

    A class to generate commands and scripts
    to run Gean4 simulation via npsim or
    ddsim for a trial.
    """

    def __init__(self, run):
        """constructor accepting arguments

        Args:
          run: runtime configuration file
        """
        self.cfgRun = ConfigParser.ReadJsonFile(run)

    def MakeCommand(self, tag, label, path, steer, inType): 
        """MakeCommand

        Generates command to run sim executable
        (npsim, ddsim) on provided inputs for
        a given tag.

        Args:
          tag:    the tag associated with the current trial
          label:  the label associated with the input
          path:   the path to the input steering file
          steer:  the input steering file
          inType: the type of input (e.g. gun, hepmc, etc.)
        Returns:
          command to be run
        """

        # construct output name
        steeTag = FileManager.ConvertSteeringToTag(steer)
        outFile = FileManager.MakeOutName(tag, label, steeTag, "sim")

        # make sure output directory
        # exists for trial
        outDir = self.cfgRun["out_path"] + "/" + tag
        FileManager.MakeDir(outDir)

        # create arguments for command
        #   --> n.b. this assumes the DETECTOR_CONFIG variable
        #       has already been set to the trial's config file
        compact = " --compactFile $DETECTOR_PATH/$DETECTOR_CONFIG.xml" 
        steerer = " --steeringFile " + path + "/" + steer
        output  = " --outputFile " + outDir + "/" + outFile

        # construct most of command
        command = self.cfgRun["sim_exec"] + compact + steerer
        if inType == "gun":
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

        # make sure run directory
        # exists for trial
        runDir = self.cfgRun["run_path"] + "/" + tag
        FileManager.MakeDir(runDir)

        # construct script name
        steeTag   = FileManager.ConvertSteeringToTag(steer)
        simScript = FileManager.MakeScriptName(tag, label, steeTag, "sim")
        simPath   = runDir + "/" + simScript

        # make commands to set detector config
        setInstall, setConfig = FileManager.MakeSetCommands(
            self.cfgRun["epic_setup"],
            config
        )

        # compose script
        with open(simPath, 'w') as script:
            script.write("#!/bin/bash\n\n")
            script.write(setInstall + "\n")
            script.write(setConfig + "\n\n")
            script.write(command)

        # make sure script can be run
        os.chmod(simPath, 0o777)

        # return path to script
        return simPath

# end =========================================================================
