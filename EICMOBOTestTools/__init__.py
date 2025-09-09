"""
EIC MOBO Tools (Test ver.)

A testbed library for AID2E tools to
simplify interfacing with the EIC
software stack
"""

__version__="0.0.0"

from .GeometryEditor import GeometryEditor
from .SimGenerator import SimGenerator

from .ConfigParser import *
from .FileManager import *

__all__ = [
    "ConvertSteeringToTag",
    "GeometryEditor",
    "ReadJsonFile",
    "GetParameter",
    "GetPathElementAndUnits",
    "SimGenerator",
    "SplitPathAndFile"
]
