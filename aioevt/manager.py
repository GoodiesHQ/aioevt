"""
Simple asyncio task manager
"""
from collections import defaultdict
from functools import partial, wraps
from threading import Condition, Lock as LockType
from typing import Callable, Union, Optional
import asyncio
import sys

from .event import Evt, EvtData


__all__ = ["Manager"]


class Manager:
    """
    Simple thread-safe event management for both async and sync
    """

    def __init__(self,
                 loop: asyncio.AbstractEventLoop = None,
                 async_retry_delay: float = 0.1,
                 async_retry_count: int = 5,
    ):
        """
        Initialize the Manager class
        """
        self._loop = loop
        self._events = defaultdict(list)
        self._async_retry_delay = async_retry_delay
        self._async_retry_count = async_retry_count
        self._events_lock = LockType()
    
    @property
    def async_retry_delay(self) -> float:
        return self._async_retry_delay
    
    @async_retry_delay.setter
    def async_retry_delay(self, new_delay: float):
        self._async_retry_delay = new_delay
    
    @property
    def async_retry_count(self) -> int:
        return self._async_retry_count
    
    @async_retry_count.setter
    def async_retry_count(self, new_count: int):
        self._async_retry_count = new_count

    def on(self,
           name: str,
           loop: asyncio.AbstractEventLoop = None,
           recurring: bool = True,
    ):
        """
        A function to create a decorator for registering events

        :param name: event name as a string
        :param loop: the loop from which you want the callback to be executed
        :param recurring: whether or not the event should be re-registered
        """
        def wrapper(func):
            self.register(name, func, loop, recurring)
            return func
        return wrapper

    def register(self,
                 name: str,
                 func: Callable,
                 loop: asyncio.AbstractEventLoop = None,
                 recurring: bool = True,
    ):
        """
        Register a global event to be triggered from a
        provided event loop when a named event is emitted.

        :param name: event name.
        :param func: callable function or coroutine invoked on event emission
        :param loop: the loop from which you want the callback to be executed
        :param recurring: whether the event should be re-registered after run
        """
        with self._events_lock:
            self._events[name].append(
                Evt(
                    func=func,
                    loop=loop or asyncio.get_event_loop(),
                    recurring=recurring,
                )
            )
    
    @property
    def loop(self):
        try:
            return self._loop or asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.get_event_loop()
    
    @loop.setter
    def loop(self, new_loop: Optional[asyncio.AbstractEventLoop]):
        self._loop = new_loop

    def emit_after(self,
                   delay: float,
                   name: str,
                   args: tuple = (),
                   kwargs: dict = None,
                   loop: asyncio.AbstractEventLoop = None,
                   retries: int = None,
    ):
        """
        Emit an event after a given period of time.

        :param delay: a float of the time (in seconds) you want to delay the call
        :param name: event name
        :param args: additional event arguments
        :param kwargs: addition event keyword arguments
        :param loop: asyncio event loop from which you want the event to be emitted
        """
        event = self._events.get(name)
        loop = loop or event.loop or asyncio.get_event_loop()
        loop.call_later(delay, self.emit, name,
                        args=args, kwargs=kwargs, retries=retries)
    @property
    def proxy(self):
        return type("Proxy", (), {
            "__getattribute__": lambda s, name: \
                partial(object.__getattribute__(s, "func"), name),
            "func": lambda _, name, *a, **k:\
                self.emit(name, args=a, kwargs=k),
        })()

    def emit(self,
             name: str,
             args: tuple = (),
             kwargs: dict = None,
             retries: int = None,
             data: EvtData = None,
    ):
        """
        Emit a signal with arbitrary parameters.
        This can execute both synchronous or asynchronous callbacks.

        NOTE: If a `EvtData` object is provided, then args/kwargs are ignored

        :param name:    event name
        :param args:    additional event positional arguments
        :param kwargs:  additional event keyword arguments
        :param retries: number of retries allowed (None = default)

        :return None
        """
        if retries is None:
            retries = self.async_retry_count
        
        if data:
            args = data.args
            kwargs = data.kwargs

        with self._events_lock:
            new_events = []
            # Remove the event name from the event list, re-add if recurring
            for evt in self._events.pop(name, ()):
                re_add = False
                try:
                    # Re-add event if recurring (or event loop hasn't started)
                    if not evt.loop.is_running():
                        if retries == 0:  # no more retries
                            raise RuntimeError("The target event loop is not running")
                        self.loop.call_later(
                            self.async_retry_delay,
                            self.emit,
                            name, args, kwargs, retries - 1,
                        )
                        re_add = True
                    elif asyncio.iscoroutinefunction(evt.func):
                        asyncio.run_coroutine_threadsafe(
                            evt.func(*(args or ()), **(kwargs or {})),
                            loop=evt.loop,
                        )
                    elif callable(evt.func):
                        evt.loop.call_soon_threadsafe(
                            partial(
                                evt.func, *args, **(kwargs or {}),
                            )
                        )
                    else:
                        # Invalid function
                        re_add = False
                    if re_add or evt.recurring:
                        new_events.append(evt)
                except Exception as e:
                    # TODO better output handling
                    import traceback
                    traceback.print_exc()
            if new_events:
                self._events[name] = new_events

    async def wait(self,
                   name: str,
                   timeout: float=None,
    ) -> Union[EvtData, None]:
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

        def callback(*args, **kwargs):
            # Set the provided parameters as a EvtData object
            nonlocal data, evt
            data = EvtData(args=args, kwargs=kwargs)

            # indicate the callback is complete and data is set
            evt.set()

        self.register(name, callback, recurring=False)
        await asyncio.wait_for(evt.wait(), timeout=timeout)
        return data


    def unregister(self, name=None, func=None):
        """
        Unregister an event
        NOTE: by name is significantly faster than by function since
        it just needs to do a single lookup. Unregistering an event
        via callback means it needs to iterate through ALL events.

        :param name: Event name
        :param func: callback function
        :return None
        """

        if name is not None:
            with self._events_lock:
                return self._events.pop(name, None)

        if func is not None:
            with self._events_lock:
                for evt in list(self._events.keys()):
                    new_events = [e for e in self._events[evt] \
                                    if e.func is not func]
                    if new_events:
                        self._events[evt] = new_events
                    else:
                        del self._events[evt]

