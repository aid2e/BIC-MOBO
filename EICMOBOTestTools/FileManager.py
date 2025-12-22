# =============================================================================
## @file    FileManager.py
#  @authors Derek Anderson
#  @date    09.09.2025
# -----------------------------------------------------------------------------
## @brief Module to generate appropriate
#    input/output and script file names
# =============================================================================

import os

def SplitPathAndFile(filepath):
    """SplitPathAndFile

    Helper method to split off
    a path from the actual file
    name.

    Args:
      filepath: filepath to split
    Returns:
      tuple of the path and the filename
    """
    file = os.path.basename(filepath)
    path = os.path.dirname(filepath)
    return path, file

def GetConfigFromPath(filepath):
    """GetConfigFromPath

    Helper method to extract
    epic config file from a
    provided absolute path.

    Args:
      filepath: absolute path to the config file
    Returns:
      the config file name without extension
    """
    path, file = SplitPathAndFile(filepath)
    return file.replace(".xml", "")

def ConvertSteeringToTag(steer):
    """ConvertSteeringToTag

    Converts the name of a steering file
    to a string to be used as a tag.

    Args:
      steer: steering file name
    Returns:
      created tag
    """
    tag = os.path.splitext(os.path.basename(steer))[0]
    tag = tag.replace(".", "_")
    return tag 

def GetBody(stage, label = "", steer = ""):
    """GetBody

    Construct body (input, steering file, stage) of
    file/script name

    Args:
      stage: the tag associated with the relevant stage of the trial
      label: the label associated with the input
      steer: the tag associated with the input steering file
    Returns:
      body of file/script name
    """
    sstage = "" if stage == "" else "_" + stage
    slabel = "" if label == "" else "_" + label
    ssteer = "" if steer == "" else "_" + steer
    body   = sstage + slabel + ssteer
    return body

def GetSuffix(stage, analysis = ""):
    """GetSuffix

    Grab correct suffix for stage.

    Args:
      stage:    the tag associated with the relevant stage of the trial
      analysis: the tag associated with the analysis being run
    Returns:
      suffix relevant to stage
    """
    suffix = ""
    if stage == "geo":
        suffix = ".overlaps.txt"
    elif stage == "sim":
        suffix = ".edm4hep.root"
    elif stage == "rec":
        suffix = ".edm4eic.root"
    elif stage == "ana":
        suffix = "_" + analysis + ".root"
    return suffix

def MakeDir(path):
    """MakeDir

    Creates a directory if it
    doesn't exist.

    Args:
      path: the path to the new directory
    """
    if not os.path.exists(path):
        os.makedirs(path)

def MakeOutName(stage, tag, label = "", steer = "", analysis = "", prefix = ""):
    """MakeOutName

    Creates output file name for
    any stage of a trial.

    Args:
      stage:    the tag associated with the relevant stage of the trial
      tag:      the tag associated with the current trial
      label:    the label associated with the input
      steer:    the tag associated with the input steering file
      analysis: optional tag associated with the analysis being run
      prefix:   optional string to inject at start of file name
    Returns:
      output file name
    """

    prefix = "aid2e_" if prefix == "" else "aid2e_" + prefix + "_"
    body   = GetBody(stage, label, steer)
    suffix = GetSuffix(stage, analysis)
    name   = prefix + tag + body + suffix
    return name 

def MakeScriptName(tag, label = "", steer = "", stage = "", analysis = ""):
    """MakeSimScriptName

    Creates file name for Geant4
    runner script.

    Args:
      tag:      the tag associated with the current trial
      label:    the label associated with the input
      steer:    the tag associated with the input steering file
      stage:    the tag associated with the relevant stage of the trial
      analysis: optional tag associated with the analysis being run
    Returns:
      script name
    """
    body = GetBody(label, steer, stage)
    return "do_aid2e_" + tag + body + ".sh"

def MakeDetSetCommands(setup, config):
    """MakeDetSetCommands

    Creates commands to set relevant
    detector path and configuration.

    Args:
      setup:  path to geometry installation script
      config: name of new detector config
    Returns:
      tuple of commands to set new detector path and config
    """
    setInsall = "source " + setup
    setConfig = "export DETECTOR_CONFIG=" + config
    return setInsall, setConfig

def MakeRecSetCommands(setup):
    """MakeRecSetCommands

    Creates commands to set relevant
    EICrecon path.

    Args:
      setup: path to eicrecon installation script
    Returns:
      command to be run
    """
    return "source " + setup

# end =========================================================================
