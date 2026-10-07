"""Tests for running async code from normal code."""

import asyncio

from googlenestcam.background_loop import run


def test_runs_a_coroutine_and_returns_its_result() -> None:
    """Normal code gets the coroutine's result."""

    async def add() -> int:
        await asyncio.sleep(0)
        return 2

    assert run(add()) == 2


def test_works_inside_a_running_loop() -> None:
    """It works where a loop already runs, as in Jupyter."""

    async def inner() -> str:
        return "ok"

    async def outer() -> str:
        return run(inner())

    assert asyncio.run(outer()) == "ok"


def test_errors_reach_the_caller() -> None:
    """Errors in the coroutine are raised to the caller."""

    async def fail() -> None:
        raise ValueError("boom")

    try:
        run(fail())
    except ValueError as error:
        assert str(error) == "boom"
    else:
        raise AssertionError("no error raised")
