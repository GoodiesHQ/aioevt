from threading import Thread
import asyncio

from aioevt import Event, Manager


def new_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def test_manager_creation():
    mgr = Manager()
    assert isinstance(mgr, Manager)


def test_register():
    mgr = Manager()
    assert len(mgr._events) == 0
    mgr.register("test_register", lambda: None, recurring=False)
    assert len(mgr._events) == 1


def test_unregister():
    mgr = Manager()
    assert len(mgr._events) == 0
    mgr.register("test_unregister", lambda: None, recurring=False)
    assert len(mgr._events) == 1
    mgr.unregister("test_unregister")
    assert len(mgr._events) == 0


def test_sync_callback():
    loop = new_event_loop()
    mgr = Manager()
    evt = asyncio.Event()
    working = False

    def callback():
        nonlocal evt, working
        working = True
        evt.set()

    mgr.register("test_sync_callback", callback, loop)
    mgr.emit("test_sync_callback")
    loop.run_until_complete(evt.wait())
    assert working is True


def test_async_callback():
    loop = new_event_loop()
    mgr = Manager()
    evt = asyncio.Event()
    working = False

    @asyncio.coroutine
    def callback():
        nonlocal evt, working
        working = True
        evt.set()

    mgr.register("test_async_callback", callback, loop)
    mgr.emit("test_async_callback")
    loop.run_until_complete(evt.wait())
    assert working is True


def test_multithread_sync_callback():
    mgr = Manager()

    def run_emit():
        mgr.emit("test_multithread_sync_callback")

    def run_register():
        loop = new_event_loop()
        working = False

        def callback():
            nonlocal loop, working
            assert working is False
            working = True
            loop.stop()

        loop = new_event_loop()
        mgr.register("test_multithread_sync_callback", callback, False)

        t2 = Thread(target=run_emit)
        t2.start()
        t2.join()
        loop.run_forever()
        assert working is True

    t1 = Thread(target=run_register)
    t1.start()
    t1.join()


def test_multithread_async_callback():
    mgr = Manager()

    def run_emit():
        mgr.emit("test_multithread_async_callback")

    def run_register():
        loop = new_event_loop()
        working = False

        @asyncio.coroutine
        def callback():
            nonlocal loop, working
            assert working is False
            working = True
            loop.stop()

        loop = new_event_loop()
        mgr.register("test_multithread_async_callback", callback, False)

        t2 = Thread(target=run_emit)
        t2.start()
        t2.join()
        loop.run_forever()
        assert working is True

    t1 = Thread(target=run_register)
    t1.start()
    t1.join()


def test_wait():
    loop = new_event_loop()
    mgr = Manager()

    @asyncio.coroutine
    def run():
        loop.call_soon(mgr.emit, "test_wait", 7)
        value = yield from mgr.wait("test_wait")
        assert value == 7

    loop.run_until_complete(run())

def test_multithread_wait():
    mgr = Manager()

    def run_emit():
        mgr.emit("test_multithread_wait", 7, 3)

    def run_wait():
        loop = new_event_loop()

        @asyncio.coroutine
        def run():
            t2 = Thread(target=run_emit)
            loop.call_soon(t2.start)
            value = yield from mgr.wait("test_multithread_wait")
            t2.join()
            assert value == (7, 3)
            loop.stop()

        asyncio.ensure_future(run())
        loop.run_forever()

    t1 = Thread(target=run_wait)
    t1.start()
    t1.join()
