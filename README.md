# Aioevt
#### Simplified Asyncio Event Management


### Problem
Asyncio offers a lot of utilities that provide thread-safe execution of coroutines and synchronous functions. However, there isn't any one "unified" way of emitting/catching events accross threads.

### Solution
aioevt - After creating the manager, you can emit 'global' events in a thread-safe way. Callbacks can be both registered and emitted from any thread. This allows you to very easily share objects through multithreaded HTTP servers such as Sanic or Vibora.


## Documentation

#### Create a manager

    import aiovt
    mgr = aiovt.Manager()
    

#### Register an event

    def double(number):
        print("Doubling a number")
        return number * 2
    
    mgr.register("double", double)

***Signature***

    def register(self, name: str, func: Callable, loop: asyncio.AbstractEventLoop=None, recurring: bool=True):
        """
        Register a global event to be triggered from a provided event loop when a named event is emitted.

        :param name: event name.
        :param func: callable function to be called when an event is emitted
        :param loop: the loop from which you want the callback to be executed
        :param recurring: whether or not the event should be re-registered after it is
        """
#### Emitting an event

    mgr.emit("double", 10)

***Signature***

    def emit(self, name: str, *args):
        """
        Non-blocking function to emit a signal with arbitrary parameters. This can execute both
        synchronous or asynchronous callbacks.

        :param name: event name
        :param args: additional event arguments

        :return None
        """


#### Waiting for an event

    # this will hang until "double" is emitted.
    await mgr.wait("double")


#### Unregistering an event

    mgr.unregister("double")
    
***Signature***

    def unregister(self, name=None, func=None):
        """
        Unregister an event
        NOTE: by name is significantly faster than by function since it just needs to do a single lookup.
        Unregistering an event via callback means it needs to iterate through ALL events.

        :param name: Event name
        :param func: callback function
        :return None
        """
