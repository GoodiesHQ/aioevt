# Aioevt
#### Simplified Asyncio-Friendly Event Management


### Problem
Asyncio offers a lot of utilities that provide thread-safe execution of coroutines and synchronous functions. However, there isn't any one "unified" way of emitting/catching events accross threads, and synchronization primitives are not themselves thread-safe. This can lead to unexpected behavior when trying to synchronize multiple event loops on multiple threads.

### Solution
`aioevt` - After creating the manager, you can emit or await 'global' events in a thread-safe way. Callbacks can registered from any thread and target any event loop. This allows you to very easily share objects and quickly emit information without fussing with thread safety.

## Documentation


### Evt and EvtData

The core objects used throughout `aioevt` are the `Evt` and `EvtData` dataclassess.
 - `Evt` represents an event itself and is comprised of a `name` (identifier), `func` (callback), `loop` (for execution), and `recurring` (automatic re-scheduling)
 - `EvtData` consists only of `args` and `kwargs` which are splatted into callbacks as needed

### Create a manager    

Create an `aioevt` manager which uses the default event loop.

    mgr = aioevt.Manager()

### Register an event

Register a global event to be triggered from a provided event loop when a named event is emitted. This can be done in two ways: both through the `mgr.register` method, or the `mgr.on` decorator. An event can have multiple callbacks, and each callback will be invoked with the same parameters on each emit. **Note:** The return value of the event callback is not retrievable. If you'd like to handle a value from inside a callback, simply emit a different event and wait for it in the desired location.

    mgr.register(
        name="MyEvent",         # Name by which the event will be referenced
        func=my_func,           # Synchronous or Asynchronous function
        loop=my_event_loop,     # Provide a target loop in which to execute the function, Default: None (get running)
        recurring=True,         # Determines if the event should be re-registered after the first emit, Default: True
    )

and

    @mgr.on(name="Add", loop=my_event_loop, recurring=True)
    def my_callback(num1, num2, num3, num4):
        # e.g. run hard calculations within a ProcessPoolExecutor
        total = num1 + num2 + num3 + num4
        mgr.emit("Calculated", args=(total,))
    
    mgr.emit_after(0.1, "Add", args=(1, 2, 3, 4))
    data = await mgr.wait("Calculated")
    assert data.args[0] == 10

#### Emitting an event
Emit a signal with arbitrary positional and/or keyword parameters. This can be done with `mgr.emit` or `mgr.emit_after` which is identical except that it accepts an additional `delay` argument as its first parameter.


    mgr.emit(
        name="MyEvent",         # Name of the event to emit
        args=(1, 2, 3),         # Tuple of args used to emit
        kwargs={"num4": 4},     # Dict of kwargs used to emit     
    )

#### Waiting for an event
Using `mgr.wait`, you can asynchronously wait until an event is fired. This is commonly used just to wait for a certain status, but will also return an `EvtData` object which contains the `args` and `kwargs` values that were passed into the call to `mgr.emit`

    data = await mgr.wait(
        name="MyEvent",         # Name of the event to wait for
        timeout=None,           # Timeout in seconds, Default: None
    )

    print(data.args)            # mgr.emit(..., args=...)
    print(data.kwargs)          # mgr.emit(..., kwargs=...)

#### Unregistering an event

Recurring events can be unregistered manually both by name and by function value. **Note** that unregistering by name is significantly faster and more efficient, so use that when possible.

    mgr.unregister(name="MyEventName")
    mgr.unregister(func=my_callback_func)