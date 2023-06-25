"""
PyStructs Integer UnitTests
"""
import unittest
from ipaddress import IPv4Address

from ..codec import *
from ..struct import *
from ..integer import I8, U32
from ..net import IPv4
from ..bytestr import GreedyBytes

#** Variables **#
__all__ = ['StructTests']

EXAMPLE_IP4 = IPv4Address('127.0.0.1')

#** Classes **#

class StructTests(unittest.TestCase):
    """Struct UnitTests"""
    
    @property
    def ctx(self):
        return Context()

    def test_protocol(self):
        """validate protocol usage errors"""
        self.assertRaises(TypeError, Struct.decode, self.ctx, b'')

    def test_dataclass(self):
        """test struct construction as a dataclass"""
        class Foo(Struct):
            a: I8
            b: I8
            c: U32 = 3
        foo   = Foo(1, 2)
        slots = getattr(Foo, '__slots__')
        self.assertEqual(slots, ('a', 'b', 'c'))
        self.assertRaises(TypeError, Foo, 1, 2, 3, 4)
        self.assertRaises(TypeError, Foo, 1, 2, 3, 4)

    def test_construct(self):
        """test `Struct` as correct data structure"""
        class Foo(Struct):
            a: I8
            b: U32
            c: IPv4
            d: bytes = field(codec=GreedyBytes)
        foo     = Foo(1, 2, EXAMPLE_IP4, b'ayy lmao')
        encoded = foo.encode(self.ctx)
        decoded = Foo.decode(self.ctx, encoded)
        recoded = decoded.encode(self.ctx)
        self.assertEqual(decoded, foo)
        self.assertEqual(encoded, recoded)
