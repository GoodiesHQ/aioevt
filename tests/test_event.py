"""
Unit Tests for AIOEVT
"""


import asyncio

from aioevt import Evt, EvtData


def create_event_objects(recurring: bool=True):
    def func(*args):
        pass
    return func, asyncio.new_event_loop(), recurring

def test_data_creation():
    """
    Check simple creation of EvtData
    """
    data = EvtData(args=(1, 2), kwargs={"a": 1})
    assert data.args[0] == 1
    assert data.args[1] == 2
    assert data.kwargs["a"] == 1

def test_data_auto_creatio():
    def callback(*args, **kwargs):
        return EvtData(args, kwargs)
    data = callback(1, 2, a=1)
    assert data.args[0] == 1
    assert data.args[1] == 2
    assert data.kwargs["a"] == 1

def test_event_creation():
    """
    Check simple creation of an event
    """
    func, loop, recurring = create_event_objects(recurring=False)
    evt = Evt(func=func, loop=loop, recurring=recurring)
    assert evt.func is func
    assert evt.loop is loop
    assert evt.recurring is recurring

def test_event_order():
    """
    Test default parameter ordering and comparng to a keyword-instantiated namedtuple
    """
    func, loop, recurring = create_event_objects()
    assert Evt(func, loop, recurring) == Evt(loop=loop, recurring=recurring, func=func)

