# =============================================================================
## @file    RecGenerator.py
#  @authors Derek Anderson
#  @date    09.10.2025
# -----------------------------------------------------------------------------
## @brief Class to generate commands and scripts to run
#    eicrecon for a trial.
# =============================================================================

from EICMOBOTestTools import ConfigParser
from EICMOBOTestTools import FileManager

class RecGenerator:
    """RecGenerator

    A class to generated commands and scripts
    to run eicrecon for a trial.
    """

    def __init__(self, enviro):
        """constructor accepting arguments

        Args:
          enviro: environment configuration file
        """
        self.cfgEnviro = ConfigParser.ReadJsonFile(enviro)
        self.argParams = dict()

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

        # construct most of command
        command = self.cfgEnviro["rec_exec"] + " -Ppodio:output_file=" + outFile
        for param, unitsAndValue in self.argParams.items():
            units, value = unitsAndValue
            if units != '': 
                command = command + " -P" + param + "=\"{}*{}\"".format(value, units)
            else:
                command = command + " -P" + param + "=\"{}\"".format(value)

        # return command with input file attached
        command = command + " " + inFile
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

        # construct script name
        steeTag   = FileManager.ConvertSteeringToTag(steer)
        recScript = FileManager.MakeScriptName(tag, label, steeTag, "rec")
        recPath   = self.cfgEnviro["run_path"] + "/" + recScript

        # make commands to set detector config
        setInstall = "source " + self.cfgEnviro["epic_setup"]
        setConfig  = "DETECTOR_CONFIG=" + config

        # open script name
        with open(recPath, 'w') as script:
            script.write("#!/bin/bash\n\n")
            script.write(setInstall + "\n")
            script.write(setConfig + "\n\n")
            script.write(command)

        # return path to script
        return recPath

# end =========================================================================
