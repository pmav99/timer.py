#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Just some classes that help benchmark execution speed.

Timer    : A context manager
AutoTimer: A self-adjusting timer. It replicates the behavior of the timeit module.

"""

from __future__ import division
from __future__ import print_function

import gc
import timeit

__all__ = ["Timer", "AutoTimer"]


def format_timing(timing, number_of_loops=1):
    """
    Return timing + unit

    Input
    =====

    timing         : The timing in seconds.
    number_of_loops: The number of loops that were required to get this timing value.
                     It defaults to 1.

    """
    usec = timing * 1e6 / number_of_loops
    if usec < 1000:
        return usec, "usec"
    else:
        msec = usec / 1000
        if msec < 1000:
            return msec, "msec"
        else:
            return timing, "sec"


class Timer(object):
    """
    A context manager that can be used to benchmark blocks of code (function calls etc).

    Usage
    =====

    It should be used to code blocks of code that take "significant" time to be executed
    (e.g. milli-seconds). It is not suitable for micro-benchmarks because it introduces
    some overhead.

    Example
    =======

        >>> with Timer() as t:
        >>>     # whatever ...

    See also
    ========

    Something like this may end up in the Standard library: http://bugs.python.org/issue19495

    """
    def __init__(self, msg='', log_func=None, disable_gc=True, precision=3):
        self.log_func = log_func
        self.msg = "Executed '%s' in:" % msg if msg else 'Executed in:'
        self.msg += ' %.*g %s'
        self.disable_gc = disable_gc
        self.precision = precision
        self.timer = timeit.default_timer
        self.start = self.end = self.interval = None

    def __enter__(self):
        if self.disable_gc:
            self.gc_state = gc.isenabled()
            gc.disable()
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        self.end = self.timer()
        if self.disable_gc and self.gc_state:
            gc.enable()

        self.seconds = self.end - self.start
        self.interval, self.unit = format_timing(self.seconds)
        if self.log_func:
            self.log_func(self.msg, self.precision, self.interval, self.unit)
        else:
            print(self.msg % (self.precision, self.interval, self.unit))


class AutoTimer(timeit.Timer):
    """
    An auto-adjustable Timer. It subclasses timeit.Timer and adds a new method named `auto()`.

    This one is suitable for micro benchmarks. It can be used with both python functions and
    python statements (e.g. strings)

    Usage
    =====

    >>> def f():
    >>>     return [i**2 for i in range(int(1e2))]

    >>> best = AutoTimer(f).auto(verbose=True, repeat=10)
    >>> print(best)

    See also
    ========

    There is an open bug for this one too: http://bugs.python.org/issue6422

    The documentation: https://docs.python.org/3.4/library/timeit.html#timeit.Timer

    """
    def auto(self, repeat=3, verbose=True, precision=3):
        """ Auto-determine how many times to execute the given statement """
        # determine number of required loops so that 0.2 <= total time < 2.0
        number_of_loops = 0
        for i in range(1, 10):
            number_of_loops = 10**i
            try:
                execution_time = self.timeit(number_of_loops)
            except Exception:
                self.print_exc()
                return 1
            if verbose:
                print("%d loops -> %.*g secs" % (number_of_loops, precision, execution_time))
            if execution_time >= 0.2:
                break

        # now that we have determined how many times we should loop,
        # execute the statements as many times as we need
        try:
            r = self.repeat(repeat, number_of_loops)
        except Exception:
            self.print_exc()
            return 1
        best = min(r)
        timing, unit = format_timing(best, number_of_loops)

        # print results
        if verbose:
            print("raw times:", " ".join(["%.*g" % (precision, x) for x in r]))
        print("%d loops, best of %d: %.*g %s per loop" % (number_of_loops, repeat, precision, timing, unit))

        return best


if __name__ == "__main__":
    def f():
        return [i**2 for i in range(int(1e2))]

    best = AutoTimer(f).auto(verbose=True, repeat=10)

    print()
    print("context manager")

    with Timer() as t:
        f()

__all__ = [
    "Timer",
    "AutoTimer",
]
