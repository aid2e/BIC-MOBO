# =============================================================================
## @file    GeometryEditor.py
#  @authors Connor Pecar,
#           with modifications by Derek Anderson
#  @date    09.02.2025
# -----------------------------------------------------------------------------
## @brief Class to generate and edit modified compact
#    files for a trial.
# =============================================================================

import os
import shutil
import sys
import xml.etree.ElementTree as ET

from EICMOBOTestTools import ConfigParser

class GeometryEditor:
    """GeometryEditor

    A class to generate and edit modified
    geometry (config and compact) files
    for a trial.
    """

    def __init__(self, run):
        """constructor accepting arguments

        Args:
          run: runtime configuration file
        """
        self.cfgRun = ConfigParser.ReadJsonFile(run)

    def __GetNewXMLName(self, name, tag):
        """GetNewXMLName

        Helper method to add tag to provided
        filename of xml.

        Args:
          name: name of the xml file to tag
          tag:  the tag to append
        Returns:
          filename with tag appended
        """
        newSuffix = "_aid2e_" + tag + ".xml"
        newName   = name.replace(".xml", newSuffix)
        return newName

    def __GetCompact(self, param, tag):
        """GetCompact

        Checks if the compact file associated with a parameter
        and a particular tag exists and returns the path to it.
        If it doesn't exist, it creates it.

        Args:
          param: a parameter, structured according to parameter config file
          tag:   the tag associated with the current trial
        Returns:
          path to compact file associated with parameter and tag
        """

        # extract path and create relevant name
        oldCompact = self.cfgRun["det_path"] + "/" + param["compact"]
        newCompact = self.__GetNewXMLName(oldCompact, tag)

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

        Args:
          tag: the tag associated with the current trial
        Returns:
          path to the config file associated with tag
        """

        # extract path and create relevant name
        oldConfig = self.cfgRun["det_path"] + "/" + self.cfgRun["det_config"] + ".xml"
        newConfig = self.__GetNewXMLName(oldConfig, tag) 

        # if new config does not exist, create it
        if not os.path.exists(newConfig):
            shutil.copyfile(oldConfig, newConfig)

        # and return path
        return newConfig

    def EditCompact(self, param, value, tag):
        """EditCompact

        Updates the value of a parameter in the compact
        file associated with it and the provided tag.

        Args:
          param: the parameter and its associated compact file
          value: the value to update to
          tag:   the tag associated with the current trial
        """

        # get path to compact file to edit, and
        # parse the xml
        fileToEdit = self.__GetCompact(param, tag)
        treeToEdit = ET.parse(fileToEdit)
 
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

    def EditConfig(self, param, tag):
        """EditConfig

        Updates the compact file associated with
        a provided parameter in the config file
        associated with the provided tag.

        Args:
          param: the parameter and its associated compact file
          tag:   the tag associated with the current trial
        Returns:
          new config name
        """

        # get path to config file to edit, and
        # parse the xml
        fileToEdit = self.__GetConfig(tag)
        treeToEdit = ET.parse(fileToEdit)

        # grab old & new compact files
        # associated with parameter
        oldCompact = param["compact"]
        newCompact = self.__GetNewXMLName(oldCompact, tag)

        # find old compact and replace
        # with new one
        path="${DETECTOR_PATH}/"
        for element in treeToEdit.getroot().findall('.//include'):
            if element.get('ref') == str(path + oldCompact):
                element.set('ref', str(path + newCompact))
                break

        # save edits and exit
        treeToEdit.write(fileToEdit)
        return fileToEdit

# end =========================================================================
