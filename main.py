#!/usr/bin/env python3
"""
Testing aioevt
"""

import threading
import asyncio
import aioevt
import time

import functools
import gc
import inspect

# Create handles to our two event loops
main_loop = asyncio.get_event_loop()
task_loop = asyncio.new_event_loop()
mgr = aioevt.Manager(loop=main_loop)

# Patch asyncio Event object to allow a thread-safe "set" variant
asyncio.Event.set_threadsafe = lambda self: self._loop.call_soon_threadsafe(self.set)

## Alternative to `@mgr.on`
# mgr.register("MyEvent", func=callback, loop=child_loop)

def set_it(evt, loop):
    """
    Set an event from a given loop
    """
    print("Setting event from thread", threading.current_thread().getName())
    loop.call_soon_threadsafe(evt.set)

@mgr.on("AsyncEvent", loop=task_loop) 
async def async_task(evt: asyncio.Event,  delay: float = 1.0):
    global main_loop
    await asyncio.sleep(delay)
    set_it(evt, main_loop)
    mgr.emit("complete", kwargs={"func": "async"})

@mgr.on("SyncEvent", loop=task_loop) 
def sync_task(evt: asyncio.Event, delay: float = 1.0):
    global main_loop
    time.sleep(delay)
    set_it(evt, main_loop)
    mgr.emit("complete", kwargs={"func": "sync"})

async def main():
    # create an event that will control access between threads
    evt = asyncio.Event() 

    # get handles to 2 threads, MAIN and TASK
    main_thread = threading.current_thread()
    main_thread.setName("MAIN")

    # Create the task thread as a dameon for run_forever
    task_thread = threading.Thread(target=task_loop.run_forever, daemon=True)
    task_thread.setName("TASK")

    pfx = lambda s: " ~ " + s
    print("Threads Created:",
          pfx(main_thread.getName()),
          pfx(task_thread.getName()),
          sep="\n", end="\n\n"
    )

    # start the thread, even if it is slightly delayed, emit will automatically re-schedule
    task_thread.start()

    # Emit the event, even though the event loop is not currently running.
    # By default, it will retry 5 times to address delay issues when starting
    # new threads

    mgr.emit("AsyncEvent", args=(evt, 0.1))                     # invoke with ARGS
    resp = await mgr.wait("complete")
    print("Completed from", resp.kwargs["func"])

    mgr.emit("SyncEvent", kwargs=dict(evt=evt, delay=1.0))      # invoke with KWARGS
    resp = await mgr.wait("complete")
    print("Completed from", resp.kwargs["func"])

    # wait for the event to complete
    await evt.wait()

if __name__ == "__main__":
    try:
        main_loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("[+] Exiting")
    finally:
        main_loop.close()