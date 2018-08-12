"""
Unit Tests for AIOEVT
"""


import asyncio

from aioevt import Event


def create_event_objects(recurring: bool=True):
    def func(*args):
        pass
    return func, asyncio.new_event_loop(), recurring

def test_event_creation():
    """
    Check simple creation of an event
    """
    func, loop, recurring = create_event_objects(recurring=False)
    evt = Event(func=func, loop=loop, recurring=recurring)
    assert evt.func is func
    assert evt.loop is loop
    assert evt.recurring is recurring

def test_event_order():
    """
    Test default parameter ordering and comparng to a keyword-instantiated namedtuple
    """
    func, loop, recurring = create_event_objects()
    assert Event(func, loop, recurring) == Event(loop=loop, recurring=recurring, func=func)

