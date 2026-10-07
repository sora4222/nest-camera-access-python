"""Run async code on one hidden background event loop.

All network work runs on this loop, so normal code, async code and Jupyter
(which already runs a loop) can share connections. See ADR 0002.
"""

import asyncio
import threading
from collections.abc import Coroutine
from typing import Any

_loop: asyncio.AbstractEventLoop | None = None
_lock = threading.Lock()


def _background_loop() -> asyncio.AbstractEventLoop:
    global _loop
    with _lock:
        if _loop is None:
            _loop = asyncio.new_event_loop()
            threading.Thread(
                target=_loop.run_forever, name="googlenestcam", daemon=True
            ).start()
        return _loop


def run[T](coroutine: Coroutine[Any, Any, T]) -> T:
    """Run ``coroutine`` on the background loop and wait for its result."""
    loop = _background_loop()
    if threading.current_thread().name == "googlenestcam":
        coroutine.close()
        raise RuntimeError("run() cannot be called from the background loop")
    return asyncio.run_coroutine_threadsafe(coroutine, loop).result()


async def run_async[T](coroutine: Coroutine[Any, Any, T]) -> T:
    """Await ``coroutine`` on the background loop from any other loop."""
    loop = _background_loop()
    if asyncio.get_running_loop() is loop:
        return await coroutine
    return await asyncio.wrap_future(asyncio.run_coroutine_threadsafe(coroutine, loop))
