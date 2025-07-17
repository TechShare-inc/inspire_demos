"""
Inspire Hand Control Library

A Python library for controlling the Inspire Hand robotic hand via serial communication.
"""

from .api import InspireHandAPI

__version__ = "0.1.0"
__author__ = "TechShare Inc."
__email__ = "contact@techshare.com"
__description__ = "Python interface for controlling the Inspire Hand robotic hand"

__all__ = ["InspireHandAPI"]
