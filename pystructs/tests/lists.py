"""
PyStructs Integer UnitTests
"""
import unittest

from ..codec import *
from ..lists import *
from ..integer import U8
from ..bytestr import StaticBytes

#** Variables **#
__all__ = ['ListTests']

DATA  = [b'ayy', b'lmao', b'whats', b'up', b'kyle?']

CODEC = StaticBytes[8]

#** Classes **#

class ListTests(unittest.TestCase):
    """List Helpers UnitTests"""

    @property
    def ctx(self):
        return Context()

    def test_protocol(self):
        """validate protocol usage errors"""
        self.assertRaises(TypeError, SizedList.decode, self.ctx, b'')
        self.assertRaises(TypeError, StaticList.decode, self.ctx, b'')
        self.assertRaises(TypeError, GreedyList.decode, self.ctx, b'')

    def test_sized(self):
        """ensure `SizedList` correctness"""
        sized   = SizedList[U8, CODEC]
        encoded = sized.encode(self.ctx, DATA)
        decoded = sized.decode(self.ctx, encoded)
        recoded = sized.encode(self.ctx, decoded)
        self.assertEqual(decoded, DATA)
        self.assertEqual(encoded, recoded)

    def test_static(self):
        """ensure `StaticList` correctness"""
        static  = StaticList[len(DATA), CODEC]
        encoded = static.encode(self.ctx, DATA)
        decoded = static.decode(self.ctx, encoded)
        recoded = static.encode(self.ctx, decoded)
        self.assertEqual(decoded, DATA)
        self.assertEqual(encoded, recoded)
        self.assertRaises(CodecError, static.encode, self.ctx, [*DATA][1:])

    def test_greedy(self):
        """ensure `GreedyList` correctness"""
        greedy  = GreedyList[CODEC]
        encoded = greedy.encode(self.ctx, DATA)
        decoded = greedy.decode(self.ctx, encoded)
        recoded = greedy.encode(self.ctx, decoded)
        self.assertEqual(decoded, DATA)
        self.assertEqual(encoded, recoded)
