# =============================================================================
## @file    AxHelper.py
#  @authors Derek Anderson
#  @date    09.29.2025
# -----------------------------------------------------------------------------
## @brief Module to convert AID2E config
#    files to Ax-compliant dictionaries
# =============================================================================

import ast

from ax.service.ax_client import ObjectiveProperties

def ConvertParamConfig(config):
    """ConvertParamConfig

    Helper method to convert a dictionary of
    AID2E parameter options into Ax-compliant
    ones.

    Args:
      config: dictionary to convert
    Returns:
      list of ax-compliant parameters
    """

    # extract parameters & constraints
    inPars = config["parameters"]
    inCons = config["constraints"]

    # iterate through parameters
    outPars = list()
    for inParKey, inParVal in inPars.items():

        # extract relevant info
        name   = inParKey
        pType  = inParVal["param_type"]
        vType  = inParVal["value_type"]

        # if needed, extra bounds
        bounds = None
        if pType == "range": 
            lLimit = ast.literal_eval(inParVal["lower"])
            uLimit = ast.literal_eval(inParVal["upper"])
            bounds = (lLimit, uLimit)

        # if needed, extract domain
        domain = None
        if "domain" in inParVal:
            domain = ast.literal_eval(inParVal["domain"])

        # create output ax parameter
        #   -- TODO add constraints
        outPar = dict()
        outPar["name"]       = name
        outPar["type"]       = pType
        outPar["value_type"] = vType

        # add bounds/domain as needed
        if bounds is not None:
            outPar["bounds"] = bounds 
        if domain is not None:
            outPar["values"] = domain

        # append parameter to list
        outPars.append(outPar)

    # return list of parameters
    return outPars

def ConvertObjectConfig(config):
    """ConvertObjectConfig

    Helper method to convert a dictionary of
    AID2E objective options into Ax-compliant
    ones.

    Args:
      config: dictionary to convert
    Returns:
      dictionary of ax-compliant objectives
    """

    # extract objectives
    inObjs = config["objectives"]

    # interate through parameters
    idxObj  = 0
    outObjs = dict()
    for inObjKey, inObjVal in inObjs.items():

        # increment counter
        idxObj += 1

        # extract relevant info
        key  = inObjKey
        goal = inObjVal["goal"]

        # turn on/off minimization as appropriate 
        if goal == "minimize":
            outObjs[key] = ObjectiveProperties(minimize = True)
        else:
            outObjs[key] = ObjectiveProperties(minimize = False)

    # return dictionary of objectives
    return outObjs

# end =========================================================================
