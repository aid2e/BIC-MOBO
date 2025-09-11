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

def MakeOutName(tag, label, steer, stage, analysis = ""):
    """MakeOutName

    Creates output file name for
    any stage of a trial.

    Args:
      tag:      the tag associated with the current trial
      label:    the label associated with the input
      steer:    the tag associated with the input steering file
      stage:    the tag associated with the relevant stage of the trail
      analysis: the tag associated with the analysis being run
    Returns:
      output file name
    """

    # make sure extension is correct
    suffix = ""
    if stage == "sim":
        suffix = ".edm4hep"
    elif stage == "rec":
        suffix = ".edm4eic"
    elif stage == "ana":
        suffix = "_" + analysis

    # return output file name
    return "aid2e_" + stage + "." + tag + "_" + label + "_" + steer + suffix + ".root"

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
