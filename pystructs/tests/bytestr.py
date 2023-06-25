"""
PyStructs ByteString UnitTests
"""
import unittest

from ..codec import *
from ..bytestr import *
from ..integer import U8

#** Variables **#
__all__ = ['ByteStringTests']

DATA = b'ayy lmao'
DLEN = len(DATA)

#** Classes **#

class ByteStringTests(unittest.TestCase):
    """ByteString Unit-Tests"""
    
    @property
    def ctx(self):
        return Context()

    def test_protocol(self):
        """validate protocol usage errors"""
        self.assertRaises(TypeError, SizedBytes.decode, self.ctx, b'')
        self.assertRaises(TypeError, StaticBytes.decode, self.ctx, b'')

    def test_sized(self):
        """test `SizedBytes` correctness"""
        sized   = SizedBytes[U8]
        encoded = sized.encode(self.ctx, DATA)
        decoded = sized.decode(self.ctx, encoded)
        self.assertEqual(sized.hint.size + len(DATA), len(encoded))
        self.assertEqual(encoded[sized.hint.size:], DATA)
        self.assertEqual(decoded, DATA)

    def test_static(self):
        """test `StaticBytes` correctness"""
        size    = 128
        static  = StaticBytes[size]
        encoded = static.encode(self.ctx, DATA)
        decoded = static.decode(self.ctx, encoded)
        self.assertEqual(static.size, len(encoded))
        self.assertEqual(decoded, DATA)

    def test_greedy(self):
        """test `GreedyBytes` correctness"""
        greedy  = deanno(GreedyBytes, Codec)
        encoded = greedy.encode(self.ctx, DATA)
        decoded = greedy.decode(self.ctx, encoded)
        self.assertEqual(encoded, decoded)

 
