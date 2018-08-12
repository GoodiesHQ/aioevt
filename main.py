#!/usr/bin/env python3
"""
Testing aioevt
"""

import threading
import asyncio
import aioevt
import time


mgr = aioevt.Manager()


def run1():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    mgr.emit("test", threading.current_thread())


def main():
    main_thread = threading.current_thread()
    evt = asyncio.Event()
    t = threading.Thread(target=run1)
    print("OK")

    def callback(current_thread):
        nonlocal main_thread
        print(main_thread, current_thread)
        assert current_thread is not main_thread
        evt.set()

    mgr.register("test", callback)
    t.start()
    asyncio.get_event_loop().run_until_complete(evt.wait())
    t.join()
    print("OK")

if __name__ == "__main__":
    main()
