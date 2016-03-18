#!/usr/bin/env python

__copyright__ = """ MIT License
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

import struct
import sys

class binary(object):
    """
    Binary Encoding Formats.
    """
    INT8   = 'b'
    UINT8  = 'B'
    INT16  = 'h'
    UINT16 = 'H'
    INT32  = 'l'
    UINT32 = 'L'
    INT64  = 'q'
    UINT64 = 'Q'
    FLOAT  = 'f'
    DOUBLE = 'd'
    STRING = 's'

class endian(object):
    """
    Endian encoding.
    """
    LITTLE = '<'
    BIG    = '>'

    def check(self):
        """
        Return the Endian type for this system.
        """
        if 'little' == sys.byteorder:
            return endian.LITTLE

        return endian.BIG

ENDIAN = endian()

class binArray(object):
    """
    Binary Array for encoding/decoding.
    """
    def __init__(self):
        """
        Create a fixed binary array.
        """
        self.__format = None

    def elementEndian(self):
        """
        Overload to define the endian encoding.
        """
        return ENDIAN.check()

    def elementType(self):
        """
        Overload to return the binary type.
        """
        return binary.UINT8

    def encode(self, *elements):
        """
        Encode the elements into binary array.
        """
        _len = len(elements)
        _fmt = self.elementEndian() + \
               (_len * self.elementType())
        _pck = struct.Struct(_fmt)

        return (struct.calcsize(_fmt),
                _pck.pack(*elements),)

    def decode(self, arraySize, binaryArray):
        """
        Decode the binary array.
        """
        _fmt = self.elementEndian() + \
               (arraySize * self.elementType())
        _pck = struct.Struct(_fmt)

        return _pck.unpack(binaryArray)

if __name__ == "__main__":
    _array = binArray()
    _val   = _array.encode(1,2,3,4)

    print _val

    _x = _array.decode(_val[0], _val[1])
    print _x

    _elems = range(255)
    _val2  = _array.encode(*_elems)

    print _val2

    _x = _array.decode(_val2[0], _val2[1])
    print _x

    _elems = 1024*(255,)
    _val3  = _array.encode(*_elems)

    print _val3

    _x = _array.decode(_val3[0], _val3[1])
    print _x

