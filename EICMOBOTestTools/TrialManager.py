# =============================================================================
## @file    TrialManager.py
#  @authors Derek Anderson
#  @date    09.19.2025
# -----------------------------------------------------------------------------
## @brief Class to generate commands and scripts to run
#    for a given trial.
# =============================================================================

import os

from EICMOBOTestTools import AnaGenerator
from EICMOBOTestTools import ConfigParser
from EICMOBOTestTools import FileManager
from EICMOBOTestTools import GeometryEditor
from EICMOBOTestTools import RecGenerator
from EICMOBOTestTools import SimGenerator

class TrialManager:
    """TrialManager

    A class to generate commands and scripts to be run
    for a given trial.
    """

    def __init__(self, run, par, ana):
        """constructor accepting arguments

        Args:
          run: runtime configuration file
          par: parameter configuration file
          ana: objectives configuration file
        """
        self.cfgRun  = ConfigParser.ReadJsonFile(run)
        self.cfgPar  = ConfigParser.ReadJsonFile(par)
        self.cfgAna  = ConfigParser.ReadJsonFile(ana)
        self.geoEdit = GeometryEditor(run)
        self.simGen  = SimGenerator(run)
        self.recGen  = RecGenerator(run)
        self.anaGen  = AnaGenerator(run, ana)

    def __DoGeometryEdits(self, tag, params):
        """DoGeometryEdits

        Generate new geometry files.

        Args:
          tag:    the tag associated with the current trial
          params: dictionary of parameter names and current values (eg. from Ax)
        Returns:
          name of new epic config file
        """
        trialConfig = ""
        for par, value in params.items():
            cfg = self.cfgPar["parameters"][par]
            if cfg["stage"] != "sim":
                continue
            else:
                self.geoEdit.EditCompact(cfg, value, tag)
                trialConfig = self.geoEdit.EditConfig(cfg, tag)

        # return name of new config file
        return trialConfig

    def __SetRecoArgs(self, params):
        """SetRecoArgs

        Set updated reconstruction arguments.

        Args:
          params: dictionary of parameter names and current values (eg. from Ax)
        """
        self.recGen.ClearArgs()
        for par, value in params.items():

            # ignore parameters from earlier stages
            cfg = self.cfgPar["parameters"][par]
            if cfg["stage"] != "rec":
                continue
            else:
                self.recGen.AddParamToArgs(cfg, value)

    def MakeTrialScript(self, tag, params):
        """MakeTrialScript

        Generate needed geometry files and script to run
        full sequence of trial.

        Args:
          tag:    the tag associated with the current trial
          params: dictionary of parameter names and current values (eg. from Ax)
        Returns:
          path to script
        """

        # step 1: edit geometry files, set
        # reconstruction parameters
        trialCfg = self.__DoGeometryEdits(tag, params)
        self.__SetRecoArgs(params)

        # create commands to set detector path, config
        # FIXME maybe DoGeometryEdits should just return the config
        #   name w/o the .xml
        cfgPath, cfgFile = FileManager.SplitPathAndFile(trialCfg)
        setInstall, setConfig = FileManager.MakeSetCommands(
            self.cfgRun["epic_setup"],
            cfgFile.replace(".xml", "")
        )
        commands = [setInstall, setConfig]

        # TODO add overlap check here

        # step 2: generate relevant simulation,
        # reconstruction commands
        for inKey, inCfg in self.cfgRun["sim_input"].items():

            # if there are multiple steering files,
            # loop over each
            inLoc  = inCfg["location"]
            inType = inCfg["type"]
            for inSteer in os.listdir(inLoc):

                # generate command to run simulation
                commands.append(
                    self.simGen.MakeCommand(
                        tag,
                        inKey,
                        inLoc,
                        inSteer,
                        inType
                    )
                )

                # now generate command to run reconstruction
                commands.append(
                    self.recGen.MakeCommand(
                        tag,
                        inKey,
                        inSteer
                    )
                )

            # TODO add merging command here
            # TODO add analysis command here

        # make sure run directory
        # exists for trial
        runDir = self.cfgRun["run_path"] + "/" + tag
        FileManager.MakeDir(runDir)

        # construct script name
        runScript = FileManager.MakeScriptName(tag)
        runPath   = runDir + "/" + runScript

        # compose script
        with open(runPath, 'w') as script:
            script.write("#!/bin/bash\n\n")
            for command in commands:
                script.write(command + "\n")

        # make sure script can be run
        os.chmod(runPath, 0o777)

        # return path to script
        return runPath

# end =========================================================================
