# =============================================================================
## @file    RecGenerator.py
#  @authors Derek Anderson
#  @date    09.10.2025
# -----------------------------------------------------------------------------
## @brief Class to generate commands and scripts to run
#    eicrecon for a trial.
# =============================================================================

import os
import stat

from EICMOBOTestTools import ConfigParser
from EICMOBOTestTools import FileManager

class RecGenerator:
    """RecGenerator

    A class to generate commands and scripts
    to run eicrecon for a trial.
    """

    def __init__(self, run):
        """constructor accepting arguments

        Args:
          run: runtime configuration file
        """
        self.cfgRun = ConfigParser.ReadJsonFile(run)
        self.argParams = dict()

    # FIXME this is not thread-safe!
    def ClearArgs(self):
        """ClearArgs

        Clear dictionary of arguments to apply
        """
        self.argParams.clear()

    def AddParamToArgs(self, param, value):
        """AddParamToArgs

        Adds a parameter to dictionary
        of arguments to apply.

        """
        self.argParams.update({param["path"] : (param["units"], value)})

    def MakeCommand(self, tag, label, steer):
        """MakeCommand

        Generates command to run reconstruction
        executable (eicrecon) on provided inputs
        for a given tag.

        Args:
          tag:   the tag associated with the current trial
          label: the label associated with the input
          steer: the input steering file
        Returns:
          command to be run
        """

        # construct input/output names
        steeTag = FileManager.ConvertSteeringToTag(steer)
        inFile  = FileManager.MakeOutName(tag, label, steeTag, "sim")
        outFile = FileManager.MakeOutName(tag, label, steeTag, "rec")

        # make sure output directory
        # exists for trial
        outDir = self.cfgRun["out_path"] + "/" + tag
        FileManager.MakeDir(outDir)

        # construct list of collections to make
        icollect = 0
        collects = ""
        for collect in self.cfgRun["rec_collect"]:
            if icollect + 1 < len(self.cfgRun["rec_collect"]):
                collects = collects + collect + ","
            else:
                collects = collects + collect
            icollect = icollect + 1

        # construct output arguments
        outArg  = "-Ppodio:output_file=" + outDir + "/" + outFile
        collArg = "-Ppodio:output_collections=" + collects

        # construct most of command
        command = self.cfgRun["rec_exec"] + " " + outArg + " " + collArg
        for param, unitsAndValue in self.argParams.items():
            units, value = unitsAndValue
            if units != '': 
                command = command + " -P" + param + "=\"{}*{}\"".format(value, units)
            else:
                command = command + " -P" + param + "=\"{}\"".format(value)

        # return command with input file attached
        command = command + " " + outDir + "/" + inFile
        return command

    def MakeScript(self, tag, label, steer, config, command):
        """MakeScript

        Generates single script to run reconstruction executable
        (eicrecon) on provided inputs for a given tag.

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
        recScript = FileManager.MakeScriptName(tag, label, steeTag, "rec")
        recPath   = runDir + "/" + recScript

        # make commands to set detector config
        setInstall, setConfig = FileManager.MakeSetCommands(
            self.cfgRun["epic_setup"],
            config
        )

        # compose script
        with open(recPath, 'w') as script:
            script.write("#!/bin/bash\n\n")
            script.write(setInstall + "\n")
            script.write(setConfig + "\n\n")
            script.write(command)

        # make sure script can be run
        os.chmod(recPath, 0o777)

        # return path to script
        return recPath

# end =========================================================================
