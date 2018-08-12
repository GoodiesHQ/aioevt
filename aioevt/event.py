"""
A simple event definition. Three pieces of information are needed:
    1. Callback function
    2. Calling event loop (current loop chosen if none provided)
    3. Recurring status
"""

from collections import namedtuple


__all__ = ["Event"]


Event = namedtuple("Event", [
    "func",
    "loop",
    "recurring",
])
