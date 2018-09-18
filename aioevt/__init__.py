"""
AIOEVT - Simple Asyncio Event Management

Package exports the event and manager classes.

Managers are used for managing the event list.
An Event is just a named tuple.
"""

from .event import Event
from .manager import Manager

name = "aioevt"
version = (1, 0, 1)

__all__ = ["Event", "Manager", "name", "version"]

__author__ = "Austin Archer"
__version__ = "0.1.1"

