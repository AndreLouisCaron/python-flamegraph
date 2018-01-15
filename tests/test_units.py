# -*- coding: utf-8 -*-


import contextlib
import six
import sys
import time
import threading
import traceback

from flamegraph.flamegraph import (
    create_flamegraph_entry,
    default_format_entry,
    get_thread_name,
    profile,
)


@contextlib.contextmanager
def nursery():
    """Ensure cleanup of test threads."""

    e = threading.Event()

    def run():
        e.wait()

    threads = set()

    def spawn(name):
        t = threading.Thread(
            target=run, name=name,
        )
        t.start()
        threads.add(t)
        return t

    try:
        yield spawn
    finally:
        e.set()
        for t in threads:
            pass


def test_get_thread_name():
    """The thread name is used when the thread exists."""

    with nursery() as spawn:
        t1 = spawn('test-thread-1')
        t2 = spawn('test-thread-2')

        assert get_thread_name(t1.ident) == 'test-thread-1'
        assert get_thread_name(t2.ident) == 'test-thread-2'
        assert get_thread_name(0xffffffff) == str(0xffffffff)


def test_get_thread_name_thread_not_found():
    """The thread name equals the thread ID when the thread does not exist."""

    assert get_thread_name(0xffffffff) == str(0xffffffff)


def test_default_format_entry():
    """Frame formatting is compatible with the reference implementation."""

    thread_name = 'main'

    def foo():
        stack = traceback.extract_stack()
        fn, ln, fun, _ = stack[-1]
        return default_format_entry(thread_name, fn, ln, fun)

    assert foo() == 'main`foo'


def test_create_flamegraph_entry():
    """Frame formatting is compatible with the reference implementation."""

    thread_name = 'main'

    def bar():
        frame = sys._current_frames()[threading.current_thread().ident]
        stack = traceback.extract_stack(frame)[-2:]
        return create_flamegraph_entry(
            thread_name, stack, default_format_entry,
        )

    def foo():
        return bar()

    assert foo() == 'main`foo;main`bar'


def test_create_flamegraph_entry_collapse_recursion():
    """Frame formatting can collapse recursion."""

    thread_name = 'main'

    def bar(collapse):
        frame = sys._current_frames()[threading.current_thread().ident]
        stack = traceback.extract_stack(frame)[-4:]
        return create_flamegraph_entry(
            thread_name, stack, default_format_entry, collapse,
        )

    def foo(collapse, n):
        if n > 0:
            return foo(collapse, n - 1)
        return bar(collapse)

    assert foo(False, 3) == 'main`foo;main`foo;main`foo;main`bar'
    assert foo(True, 3) == 'main`foo;main`bar'


def test_profile():
    """Profiling can be run in the background."""

    stream = six.StringIO()
    with nursery() as spawn:
        spawn('test-thread-1')
        spawn('test-thread-2')

        profile_args = (
            stream,
            0.01,  # 10ms
            None,
            default_format_entry,
            False,
        )
        with profile(*profile_args):
            time.sleep(0.1)

    # Grab non-empty lines output to `stream`.
    lines = stream.getvalue().split('\n')
    lines = [line for line in lines if line]

    assert len(lines) >= 1
    assert all(len(line.split(';')) >= 1 for line in lines)


def test_profile_filter_include():
    """Profiling can selectively grab stack traces."""

    # NOTE: all results will include this string.
    f = r'test'

    stream = six.StringIO()
    with nursery() as spawn:
        spawn('test-thread-1')
        spawn('test-thread-2')

        profile_args = (
            stream,
            0.01,  # 10ms
            f,
            default_format_entry,
            False,
        )
        with profile(*profile_args):
            time.sleep(0.1)

    # Grab non-empty lines output to `stream`.
    lines = stream.getvalue().split('\n')
    lines = [line for line in lines if line]

    assert len(lines) >= 1
    assert all(len(line.split(';')) >= 1 for line in lines)
    assert all('test' in line for line in lines)


def test_profile_filter_exclude():
    """Profiling can selectively grab stack traces."""

    # NOTE: this will exclude all results.
    f = r'fubar'

    stream = six.StringIO()
    with nursery() as spawn:
        spawn('test-thread-1')
        spawn('test-thread-2')

        profile_args = (
            stream,
            0.01,  # 10ms
            f,
            default_format_entry,
            False,
        )
        with profile(*profile_args):
            time.sleep(0.1)

    # Grab non-empty lines output to `stream`.
    lines = stream.getvalue().split('\n')
    lines = [line for line in lines if line]

    assert len(lines) == 0
