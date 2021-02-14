"""
AIOEVT - Simple Asyncio-friendly Event Management

Events can be emitted from, and waited on, any event loop or thread.

Waiting for an event will return the parameters passed into it when emitted.
"""

from .event import Evt, EvtData, Event, Data
from .manager import Manager

name = "aioevt"
version = (2, 2, 1)

__all__ = ["Evt", "Event", "EvtData", "Data", "Manager", "name", "version"]

__author__ = "Austin Archer"
__version__ = ".".join(map(str, version))
