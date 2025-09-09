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
    """
    tag = steer
    tag = tag.replace(".", "_")
    tag = tag.replace("_py", "")
    return tag 

def MakeSimOutName(tag, label, steer):
    """MakeSimOutName

    Creates file name for Geant4
    simulation output.

    Args:
      tag:   the tag associated with the current trial
      label: the label associated with the input
      steer: the tag associated with the input steering file
    """
    return "aid2e_sim." + tag + "_" + label + "_" + steer + ".edm4hep.root"

def MakeSimScriptName(tag, label, steer):
    """MakeSimScriptName

    Creates file name for Geant4
    runner script.

    Args:
      tag:   the tag associated with the current trial
      label: the label associated with the input
      steer: the tag associated with the input steering file
    """
    return "do_aid2e_sim." + tag + "_" + label + "_" + steer + ".sh"

def MakeRecOutName(tag, label, steer):
    """MakeSimOutName

    Creates file name for eicrecon
    output.

    Args:
      tag:   the tag associated with the current trial
      label: the label associated with the input
      steer: the tag associated with the input steering file
    """
    return "aid2e_rec." + tag + "_" + label + "_" + steer + ".edm4eic.root"

# end =========================================================================
