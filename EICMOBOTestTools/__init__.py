"""
EIC MOBO Tools (Test ver.)

A testbed library for AID2E tools to
simplify interfacing with the EIC
software stack
"""

__version__="0.0.0"

from .AnaGenerator import AnaGenerator
from .GeometryEditor import GeometryEditor
from .RecGenerator import RecGenerator
from .SimGenerator import SimGenerator
from .TrialManager import TrialManager

from .ConfigParser import *
from .FileManager import *

__all__ = [
    "AnaGenerator",
    "ConvertSteeringToTag",
    "GeometryEditor",
    "ReadJsonFile",
    "GetParameter",
    "GetPathElementAndUnits",
    "MakeOutName",
    "MakeScriptName",
    "RecGenerator",
    "SimGenerator",
    "SplitPathAndFile",
    "TrialManager"
]
