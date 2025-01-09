"""
PyStructs Struct Object UnitTests
"""
import struct
import unittest
from typing_extensions import Annotated

from pyderive import astuple

from .. import *

#** Variables **#
__all__ = ['StructTests']

#** Classes **#

class StructTests(unittest.TestCase):
    """Struct Object UnitTests"""

    def test_dataclass(self):
        """
        ensure struct object functions as a dataclass
        """
        class Foo(Struct):
            a: I8
            b: U16
            c: U32 = 3
        foo   = Foo(1, 2)
        slots = getattr(Foo, '__slots__')
        self.assertEqual(foo.a, 1)
        self.assertEqual(foo.b, 2)
        self.assertEqual(slots, ('a', 'b', 'c'))
        self.assertRaises(TypeError, Foo, 1)
        self.assertRaises(TypeError, Foo, 1, 2, 3, 4)

    def test_simple(self):
        """
        ensure simple struct pack/unpack works as intended
        """
        class Foo(Struct):
            a: I8
            b: U32
            d: bytes = field(field=StaticBytes(6))
        foo      = Foo(1, 2, b'greedy')
        packed   = foo.pack()
        unpacked = Foo.unpack(packed)
        repacked = unpacked.pack()
        self.assertEqual(foo, unpacked)
        self.assertEqual(packed, repacked)
        s_packed   = struct.pack('>bL6s', 1, 2, b'greedy')
        s_unpacked = struct.unpack('>bL6s', packed)
        self.assertEqual(s_packed, packed)
        self.assertEqual(s_unpacked, astuple(foo))

    def test_complex(self):
        """
        ensure complex struct pack/unpack works as intended
        """
        class Bar(Struct):
            bar: U8
            baz: Annotated[bytes, HintedBytes(U8)] = b'baz'
        class Foo(Struct):
            foo: I128
            bar: Bar
        foo      = Foo(1, Bar(2))
        packed   = foo.pack()
        unpacked = Foo.unpack(packed)
        repacked = unpacked.pack()
        self.assertEqual(foo, unpacked)
        self.assertEqual(packed, repacked)
