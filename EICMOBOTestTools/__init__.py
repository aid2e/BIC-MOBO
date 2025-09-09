"""
EIC MOBO Tools (Test ver.)

A testbed library for AID2E tools to
simplify interfacing with the EIC
software stack
"""

__version__="0.0.0"

from .GeometryEditor import GeometryEditor
from .ConfigParser import *

__all__ = [
    "GeometryEditor",
    "ReadJsonFile",
    "GetParameter",
    "GetDesignParamNames"
]
