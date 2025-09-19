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
    if stage == "sim":
        suffix = ".edm4hep"
    elif stage == "rec":
        suffix = ".edm4eic"
    elif stage == "ana":
        suffix = "_" + analysis
    return suffix

def MakeOutName(tag, label, steer, stage, analysis = "", prefix = ""):
    """MakeOutName

    Creates output file name for
    any stage of a trial.

    Args:
      tag:      the tag associated with the current trial
      label:    the label associated with the input
      steer:    the tag associated with the input steering file
      stage:    the tag associated with the relevant stage of the trial
      analysis: optional tag associated with the analysis being run
      prefix:   optional string to inject at start of file name
    Returns:
      output file name
    """

    prefix = "aid2e_" if prefix == "" else "aid2e_" + prefix + "_"
    suffix = GetSuffix(stage, analysis)
    name   = prefix + stage + "." + tag + "_" + label + "_" + steer + suffix + ".root"
    return name 

def MakeScriptName(tag, label, steer, stage):
    """MakeSimScriptName

    Creates file name for Geant4
    runner script.

    Args:
      tag:   the tag associated with the current trial
      label: the label associated with the input
      steer: the tag associated with the input steering file
      stage: the tag associated with the relevant stage of the trail
    Returns:
      script name
    """
    return "do_aid2e_" + stage + "." + tag + "_" + label + "_" + steer + ".sh"

def MakeSetCommands(setup, config):
    """MakeSetCommands

    Creates commands to set relevant
    detector path and configuration"

    Args:
      setup:  path to geometry installation
      config: name of new detector config
    Returns:
      tuple of commands to set new detector path and config
    """
    setInsall = "source " + setup
    setConfig = "export DETECTOR_CONFIG=" + config
    return setInsall, setConfig

def MakeDir(path):
    """MakeDir

    Creates a directory if it
    doesn't exist.

    Args:
      path: the path to the new directory
    """
    if not os.path.exists(path):
        os.makedirs(path)

# end =========================================================================
