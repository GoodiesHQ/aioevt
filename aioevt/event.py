"""
Module which provides the Event definition
"""

from dataclasses import dataclass
from asyncio import AbstractEventLoop

__all__ = ["Event", "Data", "Evt", "EvtData",]


@dataclass
class Evt:
    """
    A simple event definition. Three pieces of information are needed:
        1. Callback function
        2. Calling event loop (current loop chosen if none provided)
        3. Recurring status
    """
    func: callable
    loop: AbstractEventLoop
    recurring: bool

Event = Evt

@dataclass
class EvtData:
    args: tuple = ()
    kwargs: dict = None

Data = EvtData