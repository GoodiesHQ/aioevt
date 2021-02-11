import threading
import asyncio

from aioevt.event import EvtData
from aioevt.manager import Manager


def new_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def test_manager_creation():
    mgr = Manager()
    assert isinstance(mgr, Manager)


def test_register():
    mgr = Manager()

    mgr.register("test_register", lambda: None, recurring=False)
    assert len(mgr._events) == 1


def test_unregister():
    mgr = Manager()
    assert len(mgr._events) == 0
    mgr.register("test_unregister", lambda: None, recurring=False)
    assert len(mgr._events) == 1
    mgr.unregister("test_unregister")
    assert len(mgr._events) == 0

    def callback():
        pass

    mgr.register("test_unregister", callback, recurring=False)
    assert len(mgr._events) == 1
    mgr.unregister(func=callback)
    assert len(mgr._events) == 0


def test_sync_callback():
    loop = new_event_loop()
    mgr = Manager(loop=loop)
    evt = asyncio.Event()
    working = False

    def callback():
        nonlocal evt, working
        working = True
        evt.set()

    mgr.register("test_sync_callback", callback, loop, False)
    mgr.emit("test_sync_callback")
    loop.run_until_complete(evt.wait())
    assert working is True


def test_async_callback():
    loop = new_event_loop()
    mgr = Manager()
    evt = asyncio.Event()
    working = False

    async def callback():
        nonlocal evt, working
        working = True
        evt.set()

    mgr.register("test_async_callback", callback, loop)
    mgr.emit("test_async_callback")
    loop.run_until_complete(evt.wait())
    assert working is True


def test_multithread_sync_callback():
    main_loop = asyncio.get_event_loop()
    task_loop = asyncio.new_event_loop()
    mgr = Manager(loop=main_loop)
    evt = asyncio.Event()

    @mgr.on("test_multithread_sync_callback", loop=task_loop, recurring=False)
    def callback(*args, **kwargs):
        nonlocal main_loop, evt
        main_loop.call_soon_threadsafe(evt.set)
        mgr.emit("test_multithread_sync_callback_done")
    
    t1 = threading.Thread(
        target=task_loop.run_until_complete,
        args=[mgr.wait("test_multithread_sync_callback_done")],
    )
    t1.start()
    mgr.emit("test_multithread_sync_callback")
    task = asyncio.wait_for(evt.wait(), 2.0)
    main_loop.run_until_complete(task)
    t1.join(1.0)
    assert not t1.is_alive()
    assert evt.is_set()


def test_multithread_async_callback():
    main_loop = asyncio.get_event_loop()
    task_loop = asyncio.new_event_loop()
    mgr = Manager(loop=main_loop)
    evt = asyncio.Event()

    @mgr.on("test_multithread_async_callback", loop=task_loop, recurring=False)
    async def callback(*args, **kwargs):
        nonlocal main_loop, evt
        main_loop.call_soon_threadsafe(evt.set)
        mgr.emit("test_multithread_async_callback_done")
    
    t1 = threading.Thread(
        target=task_loop.run_until_complete,
        args=[mgr.wait("test_multithread_async_callback_done")],
    )
    t1.start()
    mgr.emit("test_multithread_async_callback")
    task = asyncio.wait_for(evt.wait(), 2.0)
    main_loop.run_until_complete(task)
    t1.join(1.0)
    assert not t1.is_alive()
    assert evt.is_set()


def test_args_and_kwargs():
    async def run_test():
        mgr = Manager()
        evt = asyncio.Event()
        args, kwargs = None, None

        @mgr.on("test_args_and_kwargs", recurring=False)
        def foo(arg1, arg2, *, kwarg1=None):
            nonlocal args, kwargs
            args = [arg1, arg2]
            kwargs = dict(kwarg1=kwarg1)
            evt.set()
        
        mgr.emit(
            "test_args_and_kwargs",
            args=(1, 2), kwargs={"kwarg1": "a"},
        )
        await asyncio.wait_for(evt.wait(), 1.0)
        assert args == [1, 2]
        assert kwargs == {"kwarg1": "a"}
    asyncio.run(run_test())

def test_evt_data():
    async def run_test():
        mgr = Manager()
        evt = asyncio.Event()
        args, kwargs = None, None

        @mgr.on("test_evt_data", recurring=False)
        def foo(arg1, arg2, *, kwarg1=None):
            nonlocal args, kwargs
            args = [arg1, arg2]
            kwargs = dict(kwarg1=kwarg1)
            evt.set()
        
        mgr.emit(
            "test_evt_data",
            data=EvtData(args=(1, 2), kwargs={"kwarg1": "a"}),
        )
        await asyncio.wait_for(evt.wait(), 1.0)
        assert args == [1, 2]
        assert kwargs == {"kwarg1": "a"}
    asyncio.run(run_test())



def test_wait():
    loop = new_event_loop()
    mgr = Manager()

    async def run():
        task = loop.create_task(mgr.wait("test_wait"))
        loop.call_soon(mgr.emit, "test_wait", [7], {"a": 3})
        value = await task
        assert value.args[0] == 7
        assert value.kwargs["a"] == 3

    loop.run_until_complete(run())

def test_multithread_wait():
    mgr = Manager()

    def run_emit():
        mgr.emit("test_multithread_wait", args=(7, 3))

    def run_wait():
        loop = new_event_loop()

        async def run():
            nonlocal loop
            t2 = threading.Thread(target=run_emit)
            task = loop.create_task(mgr.wait("test_multithread_wait"))
            loop.call_soon(t2.start)
            value = await task
            t2.join()
            assert value.args == (7, 3)
            loop.stop()

        asyncio.ensure_future(run())
        loop.run_forever()

    t1 = threading.Thread(target=run_wait)
    t1.start()
    t1.join(1.0)
    assert not t1.is_alive()