"""
Inspire Hand Control Library

A Python library for controlling the Inspire Hand robotic hand via serial and Modbus TCP communication.
"""

from .inspire_modbus import InspireHandModbus
from .inspire_serial import InspireHandSerial

__version__ = "0.1.0"
__author__ = "TechShare Inc."
__email__ = "contact@techshare.com"
__description__ = "Python interface for controlling the Inspire Hand robotic hand"

__all__ = ["InspireHandSerial", "inspire_modbus"]
