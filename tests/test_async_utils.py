"""Approval tests for core/async_utils.run_in_background.

These tests document the contract that 23 downstream call sites depend on.
They were written during the fix-print-and-counter-bug SDD change to lock
in the post-refactor behavior:

  1. run_in_background returns a concurrent.futures.Future
  2. On success, the callback is invoked exactly once with the return value
  3. On failure (worker raises), the callback is NOT invoked
  4. The exception from a failed worker is logged via the module logger
  5. No DEBUG noise is printed to stdout (was the bug: print statements)

This is the strict-TDD approval-test pattern: capture contract before and
after the refactor, then refactor with confidence.
"""
from __future__ import annotations

import logging
import time
from concurrent.futures import Future

import pytest

from core.async_utils import run_in_background


def _wait(fut: Future, timeout: float = 2.0) -> None:
    """Block until the future completes; production UI never blocks on these."""
    deadline = time.time() + timeout
    while not fut.done() and time.time() < deadline:
        time.sleep(0.01)


class TestRunInBackgroundContract:
    def test_returns_future(self):
        fut = run_in_background(lambda: 42)
        assert isinstance(fut, Future)
        _wait(fut)
        assert fut.result() == 42

    def test_no_stdout_pollution(self, capsys):
        """No DEBUG print() noise on stdout. Bug we are fixing."""
        run_in_background(lambda: 1)
        _wait(run_in_background(lambda: 2))
        captured = capsys.readouterr()
        assert "DEBUG run_in_background" not in captured.out
        assert "DEBUG: done_callback" not in captured.out

    def test_callback_invoked_once_on_success(self, capsys):
        received: list[object] = []

        def cb(value):
            received.append(value)

        fut = run_in_background(lambda: "hello", callback=cb)
        _wait(fut)

        assert received == ["hello"]
        # No DEBUG pollution on success path either
        assert "DEBUG" not in capsys.readouterr().out

    def test_callback_not_invoked_on_failure(self, caplog):
        """Failed worker must not invoke callback (callers expect callback
        only on success). The exception is logged for observability."""
        received: list[object] = []

        def cb(value):
            received.append(value)

        def boom():
            raise RuntimeError("kaboom")

        with caplog.at_level(logging.DEBUG, logger="core.async_utils"):
            fut = run_in_background(boom, callback=cb)
            _wait(fut)

        assert received == []
        # Exception must be logged so it's not silently swallowed.
        # logger.exception() attaches exc_info; check the chained exception
        # (rec.message holds the log template, not the exception text).
        assert any(
            rec.exc_info is not None and rec.exc_info[1] is not None
            and "kaboom" in str(rec.exc_info[1])
            for rec in caplog.records
        ), "Expected exception to be logged via logger.exception/logger.error"

    def test_no_callback_still_completes(self):
        fut = run_in_background(lambda: "ok")
        _wait(fut)
        assert fut.result() == "ok"

    def test_callback_exception_does_not_corrupt_pool(self):
        """A user callback that raises must not kill the threadpool worker."""
        def bad_cb(_):
            raise RuntimeError("user callback error")

        fut1 = run_in_background(lambda: 1, callback=bad_cb)
        _wait(fut1)

        # The pool must still serve new work after a bad callback
        received: list[object] = []
        fut2 = run_in_background(lambda: 2, callback=received.append)
        _wait(fut2)
        assert received == [2]
