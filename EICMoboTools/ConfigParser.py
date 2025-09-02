# =============================================================================
## @file    ConfigParser.py
#  @authors Karthik Suresh,
#           with light modifications by Derek Anderson
#  @date    09.02.2025
# -----------------------------------------------------------------------------
## @brief Parses configuration JSON files
#    and returns appropriately structured
#    dictionaries
# =============================================================================

import json
import os
import sys

def ReadJsonFile(jsonFile):
    """ReadJsonFile

    Checks if specified json file exists, and loads
    it if it does.

    Keyword arguments:
    jsonFile -- file to read
    """
    if(os.path.isfile(jsonFile) == False):
        print ("ERROR: the json file you specified does not exist")
        sys.exit(1)
    with open(jsonFile) as f:
        data = json.loads(f.read())
    return data

# FIXME this might be needed...
def GetDesignParamNames(dataDict, rangeDict):
    designParams = {}
    for key, value in dataDict.items():
        for i in range(1, value[0] + 1):
            key1 = key.replace("_fill_", f"{i}")
            if(rangeDict.get(key1)):
                designParams[key1] = rangeDict[key1]
            else:
                designParams[key1] = rangeDict[key]
    return designParams

# end =========================================================================
