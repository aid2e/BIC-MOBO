# =============================================================================
## @file    ConfigParser.py
#  @authors Karthik Suresh,
#           Connor Pecar,
#           with modifications by Derek Anderson
#  @date    09.02.2025
# -----------------------------------------------------------------------------
## @brief Module to parse configuration JSON files and
#    return appropriately structured dictionaries.
# =============================================================================

import json
import os
import sys

def ReadJsonFile(jsonFile):
    """ReadJsonFile

    Checks if specified json file exists, and loads
    it if it does.

    Args:
      jsonFile: file to read
    Returns:
      dictionary of loaded data
    """
    if(os.path.isfile(jsonFile) == False):
        print ("ERROR: the json file you specified does not exist")
        sys.exit(1)
    with open(jsonFile) as f:
        data = json.loads(f.read())
    return data

def GetParameter(param, file):
    """GetParameter

    Extracts specified parameter from  as a
    dictionary  from parameter configuration
    file. Raises exception if parameter is not
    found.

    Args:
      param: key of the parameter to extract
      file: parameter configuration file to parse
    Returns:
      dictionary associated with parameter
    """
    config = ReadJsonFile(file)["parameters"]
    if config[param] :
        return config[param]
    else:
        raise NameError('Parameter {param} not found in file {file}!')

def GetPathElementAndUnits(param):
    """GetPathElementAndUnits

    Helper method to extract the path, element,
    and units from a parameter.

    Args:
      param: the parameter to extract from
    Returns:
      tuple of the path, element, and units of parameter
    """
    return param["path"], param["element"], param["units"]

# end =========================================================================
