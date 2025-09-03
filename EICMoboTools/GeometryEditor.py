# =============================================================================
## @file    GeometryEditor.py
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

import xml.etree.ElementTree as ET

from EICMoboTools import ConfigParser

class GeometryEditor:
    """GeometryEditor

    A class to generate and edit modified
    geometry (config and compact) files
    for a trial.
    """

    def __init__(self, enviro, params):
        """constructor accepting arguments

        Keyword arguments:
        enviro -- environment configuration file
        params -- parameter configuration file
        """
        self.cfgEnviro = ConfigParser.ReadJsonFile(enviro)
        self.cfgParams = ConfigParser.ReadJsonFile(params)

    def __GetCompact(self, param, tag):
        """GetCompact

        Checks if the compact file associated
        with a parameter and a particular tag
        exists and returns the path to it. If
        it doesn't exist, it creates it.

        Keyword arguments:
        param -- a parameter, structured according to parameter config file
        tag   -- the tag associated with the relevant trial
        """

        # extract path and create relevant name
        oldCompact = self.cfgEnviro["det_path"] + "/" + param["compact"]
        newSuffix  = "_" + tag + ".xml"
        newCompact = oldCompact.replace(".xml", newSuffix)

        # if new compact does not exist, create it
        if not os.path.exists(newCompact):
            shutil.copyfile(oldCompact, newCompact)

        # and return path
        return newCompact

    def __GetConfig(self, tag):
        """GetConfig

        Checks if the configuration file associated
        a particular tag exists and returns the path
        to it. If it doesn't exist, it creates it.

        Keyword arguments:
        param -- a parameter, structured according to parameter config file
        tag   -- the tag associated with the relevant trial
        """

        # extract path and create relevant name
        oldConfig = self.cfgEnviro["det_path"] + "/" + self.cfgEnviro["det_config"] + ".xml"
        newSuffix = "_" + tag + ".xml"
        newConfig = oldConfig.replace(".xml", newSuffix)

        # if new config does not exist, create it
        if not os.path.exists(newConfig):
            shutil.copyfile(oldConfig, newConfig)

        # and return path
        return newConfig

    def EditCompact(self, param, value, tag):
        """EditCompact

        Creates and edits a compact file to update
        the specified parameter and tag.

        Keyword arguments:
        param -- a parameter, structured according to parameter config file
        value -- the new value of the parameter
        tag   -- the tag associated with the relevant trial
        """

        # get path to compact file to edit, and
        # parse the xml
        fileToEdit = self.__GetCompact(param, tag)
        treeToEdit = ET.parse(fileToEdit)
        #treeRoot = treeToEdit.getroot()
 
        # extract relevant info from parameter
        path, elem, unit = ConfigParser.GetPathElementAndUnits(param)

        # now find and edit the relevant info 
        elemToEdit = treeToEdit.getroot().find(path)
        if unit != '':
            elemToEdit.set(elem, "{}*{}".format(value, unit))
        else:
            elemToEdit.set(elem, "{}".format(value))

        # save edits and exit
        treeToEdit.write(fileToEdit)
        return

# end =========================================================================
