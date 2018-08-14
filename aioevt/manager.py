"""
Simple asyncio task manager
"""
from collections import defaultdict
from functools import partial
from threading import Condition, Lock as LockType
from typing import Callable
import asyncio
import sys

from .event import Event


__all__ = ["Manager"]


class Manager:
    """
    Simple thread-safe event management
    """

    def __init__(self, control_loop: asyncio.AbstractEventLoop=None):
        self._loop = control_loop or asyncio.get_event_loop()
        self._events = defaultdict(list)
        self._events_lock = LockType()

    def register(self, name: str, func: Callable, loop: asyncio.AbstractEventLoop=None, recurring: bool=True):
        """
        Register a global event to be triggered from a provided event loop when a named event is emitted.

        :param name: event name.
        :param func: callable function to be called when an event is emitted
        :param loop: the loop from which you want the callback to be executed
        :param recurring: whether or not the event should be re-registered after it is
        """
        with self._events_lock:
            self._events[name].append(Event(func=func, loop=loop or asyncio.get_event_loop(), recurring=recurring))

    def emit_after(self, delay: float, name: str, *args, loop: asyncio.AbstractEventLoop=None):
        """
        Emit an event after a given period of time.

        :param delay: a float of the time (in seconds) you want to delay the call
        :param name: event name
        :param args: additional event arguments
        :param loop: asyncio event loop from which you want the event to be emitted
        """
        loop = loop or asyncio.get_event_loop()
        loop.call_later(delay, self.emit, name, *args)

    def emit(self, name: str, *args):
        """
        Non-blocking function to emit a signal with arbitrary parameters. This can execute both
        synchronous or asynchronous callbacks.

        :param name: event name
        :param args: additional event arguments

        :return None
        """
        with self._events_lock:
            new_events = []
            for evt in self._events.pop(name, []):
                is_async = asyncio.iscoroutinefunction(evt.func)
                try:
                    if is_async:
                        asyncio.run_coroutine_threadsafe(evt.func(*args), loop=evt.loop)
                    else:
                        evt.loop.call_soon_threadsafe(evt.func, *args)
                    if evt.recurring:
                        new_events.append(evt)
                except Exception as e:
                    # TODO: handle debugging error output in a more streamlined way
                    print(e, file=sys.stderr)
            if new_events:
                self._events[name] = new_events

    @asyncio.coroutine
    def wait(self, name: str, timeout: float=None):
        """
        Wait until an event fures and return the emit parameters

        :param name: Event Name
        :param loop: the event loop
        :param timeout: the maximum time (in seconds) to wait before it raises an exception
        :return the parameters passed to `emit`
        :raises asyncio.TimeoutError when necessary
        """

        data = None
        evt = asyncio.Event()

        def callback(*args):
            nonlocal data, evt
            data = args[0] if len(args) == 1 else args
            evt.set()

        self.register(name, callback, recurring=False)
        yield from asyncio.wait_for(evt.wait(), timeout=timeout)
        return data


    def unregister(self, name=None, func=None):
        """
        Unregister an event
        NOTE: by name is significantly faster than by function since it just needs to do a single lookup.
        Unregistering an event via callback means it needs to iterate through ALL events.

        :param name: Event name
        :param func: callback function
        :return None
        """

        if name is not None:
            with self._events_lock:
                return self._events.pop(name, None)

        if func is not None:
            with self._events_lock:
                for evt in events:
                    self._events[evt] = [evt for evt in self._events[evt] if evt.func != func]

