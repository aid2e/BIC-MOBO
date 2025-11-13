# =============================================================================
## @file    AxHelper.py
#  @authors Derek Anderson
#  @date    09.29.2025
# -----------------------------------------------------------------------------
## @brief Module to convert AID2E config
#    files to Ax-compliant dictionaries
# =============================================================================

import ast

from ax.api.configs import ChoiceParameterConfig, RangeParameterConfig
from ax.service.ax_client import ObjectiveProperties

def ConvertParamConfig(config):
    """ConvertParamConfig

    Helper method to convert a dictionary of
    AID2E parameter options into a list of
    Ax-compliant definitions.

    This is relevant for when interacting with
    the ax.service.ax_client.AxClient API.

    Args:
      config: dictionary to convert
    Returns:
      list of ax-compliant parameter definitions
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

def CreateParamList(config):
    """CreateParamList

    Helper method to create a list of Ax
    parameters from a dictionary of AID2E
    parameter options.

    This is relevant for when interacting with the
    ax.Client API.

    Args:
      config: dictionary to process
    Returns:
      list of ax parameters
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

        # if needed, check for ordering
        ordered = True
        if "is_ordered" in inParVal:
            ordered = ast.literal_eval(iParVal["is_ordered"])

        # create output ax parameter
        #   -- TODO add constraints
        outPar = None
        if pType == "choice":
            outPar = ChoiceParameterConfig(
                name = name,
                values = domain,
                parameter_type = vType,
                is_ordered = ordered
            )
        elif pType == "range":
            outPar = RangeParameterConfig(
                name = name,
                parameter_type = vType,
                bounds = bounds
            )

        # append parameter to list
        outPars.append(outPar)

    # return list of parameters
    return outPars

def ConvertObjectConfig(config):
    """ConvertObjectConfig

    Helper method to convert a dictionary of
    AID2E objective options into a dictionary
    of  AxClient-compliant objectives.

    This is relevant for when interacting with
    the ax.service.ax_client.AxClient API.

    Args:
      config: dictionary to convert
    Returns:
      a dictionary of ax-compliant objectives
    """

    # extract objectives
    inObjs = config["objectives"]

    # interate through them
    outObjs  = dict()
    for inObjKey, inObjVal in inObjs.items():

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

def CreateObjectiveNames(config):
    """CreateObjectiveNames

    Helper method to create a string of objective
    names to be provided to the Ax Client.

    This is relevant for when interacting with the
    ax.Client API.

    Args:
      config: dictionary to process
    Returns:
      a string defining a list of objective names
    """

    # extract objectives
    inObjs = config["objectives"]

    # interate through them
    outNames = ""
    for inObjKey, inObjVal in inObjs.items():

        # extract relevant info
        key  = inObjKey
        goal = inObjVal["goal"]

        # turn on/off minimization as appropriate
        sKeyAndGoal = ""
        if goal == "minimize":
            sKeyAndGoal = "-" + key
        else:
            sKeyAndGoal = key

        # append name to the string
        if outNames != "":
            outNames += ","
        outNames += sKeyAndGoal

    # return string of names
    return outNames

# end =========================================================================
