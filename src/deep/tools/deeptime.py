#!/usr/bin/env python

__copyright__ = """
################################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Deep Grant
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################
"""
__author__ = "Deep Grant"

import os
import sys
import ctypes
import time

class _monotime(ctypes.Structure):
    """
    Map the C TimeVal struct.
    """
    _fields_ = [
        ('tv_sec', ctypes.c_long),
        ('tv_nsec', ctypes.c_long),
        ]

class monotonic(object):
    """
    A Simple class to access the monotonic clock and return the counter.
    Simple divisors provided to convert the counter into
    SECONDS, MILLISECONDS, etc.
    """
    CLOCK_RAW = 4

    SECONDS      = int(1e9)
    TENTHS       = int(1e8)
    HUNDRETHS    = int(1e7)
    MILLISECONDS = int(1e6)
    MICROSECONDS = int(1e3)
    NANOSECONDS  = 1

    def __init__(self):
        """
        Load the DLL with the monotonic C Method.
        """
        self.__librt = ctypes.CDLL('librt.so.1',
                                   use_errno = True)

    def time(self):
        """
        Return the monotonic time in a 64bit Integer.
        Raises an OSError exception upon failure.
        """
        _mtime = _monotime()

        clock_gettime          = self.__librt.clock_gettime
        clock_gettime.argtypes = [ctypes.c_int,
                                  ctypes.POINTER(_monotime)]

        if 0 != clock_gettime(monotonic.CLOCK_RAW,
                              ctypes.pointer(_mtime)):
            _errno = ctypes.get_errno()
            raise OSError(_errno, os.strerror(_errno))

        return ((_mtime.tv_sec * monotonic.SECONDS) +
                _mtime.tv_nsec)


if __name__ == "__main__":
    _timer = monotonic()
    _start = _timer.time()

    time.sleep(1)

    _duration = (_timer.time() - _start) / monotonic.SECONDS

    print 'Duration %d seconds.' % (_duration,)

    _start = _timer.time()
    time.sleep(0.1)
    _duration = (_timer.time() - _start) / monotonic.TENTHS

    print 'Duration %d tenths.' % (_duration,)
