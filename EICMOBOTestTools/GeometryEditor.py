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
import pathlib
import re
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

    def __GetNewName(self, name, tag, ext = ".xml"):
        """GetNewName

        Helper method to add tag to provided
        filename.

        Args:
          name: name of the file to tag
          tag:  the tag to append
          ext:  the extension of the file
        Returns:
          filename with tag appended
        """
        newSuffix = "_aid2e_" + tag + ext
        newName   = name
        if  ext == "":
            newName = name + newSuffix
        else:
            newName = name.replace(ext, newSuffix)
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
        newCompact = oldCompact
        if not oldCompact.endswith(tag + ".xml"):
            newCompact = self.__GetNewName(oldCompact, tag)

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
          path to the config file with tag
        """

        # extract path and create relevant name
        install   = self.cfgRun["det_path"] + "/install/share/epic/"
        oldConfig = install + self.cfgRun["det_config"] + ".xml"
        newConfig = oldConfig
        if not oldConfig.endswith(tag + ".xml"):
            newConfig = self.__GetNewName(oldConfig, tag)

        # if new config does not exist, create it
        if not os.path.exists(newConfig):
            shutil.copyfile(oldConfig, newConfig)

        # and return path
        return newConfig

    def __GetFile(self, file, tag, ext = ".xml"):
        """GetFile

        Checks if a file associated with a particular
        tag exists and returns the path to it. If it
        doesn't exist, it creates it.

        Args:
          file: the file to get/be created
          tag:  the tag associated with the current trial
          ext:  the extension of the file
        Returns:
          path to the file with tag
        """

        # create relevant name
        newFile = file
        if not file.endswith(tag + ext):
            newFile = self.__GetNewName(file, tag, ext)

        # if new file does not exist, create it
        if not os.path.exists(newFile):
            shutil.copyfile(file, newFile)

        # and return path
        return newFile

    def __IsPatternInFile(self, pattern, file):
        """IsPatternInFile

        Checks if a provided pattern (eg. a
        file name) is in a file, and returns
        true or false of it is or isn't.

        Args:
          pattern: the pattern to look for
          file:    the file to look in
        Returns:
          whether or not pattern was found
        """

        # iterate through lines until pattern is found
        found = False
        with open(file, 'r') as lines:
            for iLine, line in enumerate(lines, start=1):
                if re.search(pattern, line):
                    found = True
                    break

        # return whether or not pattern was ever found
        return found

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
        newCompact = self.__GetNewName(oldCompact, tag)

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

    def EditRelatedFiles(self, param, tag):
        """EditRelatedFiles

        Updates _all_ xml files related to a
        provided parameter, including related
        config files and intermediaries.

        Args:
          param: the parameter and its associated compact file
          tag:   the tag associated with the current trial
        Returns:
          ...
        """

        # step 1:grab old & new compact files
        #   associated with parameter
        oldCompact = param["compact"]
        newCompact = self.__GetNewName(oldCompact, tag)

        # step 2: split old compact path into directories
        #   relative to cfg["det_path"] to search in
        split = oldCompact.split('/')

        # step 3: now iterate upwards through sequence
        #   of directories to check to find related
        #   files
        path    = ""
        steps   = len(split) + 1
        queries = [split[-1]]
        for step in range(2, steps):

            # step 3(a): loop through all files in directory
            search = '/'.join(part for part in split[0:steps - step])
            root   = self.cfgRun["det_path"] + '/' + search
            new    = list()
            for file in os.listdir(self.cfgRun["det_path"] + "/" + search):

                full = root + "/" + file
                if os.path.isdir(full):
                    continue

                # step 3(a)(i): check if any files include
                #   any of the files related to the compact
                for query in queries:
                    if self.__IsPatternInFile(query, full):

                        # step3(a)(ii): if it does, create
                        #   new version with filenames
                        #   updated accordingly
                        copy     = self.__GetFile(full, tag)
                        update   = self.__GetNewName(query, tag)
                        editable = pathlib.Path(copy)
                        text     = editable.read_text(encoding="utf-8")
                        edited   = text.replace(query, update)
                        editable.write_text(edited, encoding="utf-8")

                        if file not in new:
                            new.append(file)

            # step 3(b): add any new related files to list
            #   and update relative paths
            path = split[-step] + "/" + path
            add  = path.split("/")[0]

            queries.extend(new)
            queries[:] = [f"{add}/{query}" for query in queries]

        # step 4: now identify all YAML configurations
        #   that contain one of the updated files
        config  = self.cfgRun["det_path"] + "/configurations"
        for file in os.listdir(config):

            full = config + "/" + file
            if os.path.isdir(full):
                continue

            # step 4(a): check if any updated compact files'
            #   stems appear in configuration
            for query in queries:
                stem = os.path.splitext(os.path.basename(query))[0]
                if self.__IsPatternInFile(stem, full):

                    # step 4(b): if it does, create new
                    #   version and update stems
                    #   accordingly
                    copy     = self.__GetFile(full, tag, ".yml")
                    update   = self.__GetNewName(stem, tag, "")
                    editable = pathlib.Path(copy)
                    text     = editable.read_text(encoding="utf-8")
                    edited   = text.replace(stem, update)
                    editable.write_text(edited, encoding="utf-8")

# end =========================================================================
