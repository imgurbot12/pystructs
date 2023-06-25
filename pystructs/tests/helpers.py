"""
PyStructs ByteString UnitTests
"""
import enum
import unittest

from ..codec import *
from ..helpers import *
from ..integer import U8

#** Variables **#
__all__ = ['HelperTests']

#** Classes **#

class E(enum.IntEnum):
    """Sample Enum for Wrapped Testing"""
    A = 1
    B = 2

class HelperTests(unittest.TestCase):
    """Helper Codec Tests"""

    @property
    def ctx(self):
        return Context()

    def test_protocol(self):
        """validate protocol usage errors"""
        self.assertRaises(TypeError, Const.decode, self.ctx, b'')
        self.assertRaises(TypeError, Wrap.decode, self.ctx, b'')

    def test_const(self):
        """ensure `Const` correctness"""
        CONST   = b'ayy lmao'
        OTHER   = b'this is another string'
        const   = Const[CONST]
        encoded = const.encode(self.ctx, CONST)
        decoded = const.decode(self.ctx, encoded)
        self.assertEqual(encoded, decoded)
        self.assertRaises(CodecError, const.encode, self.ctx, OTHER)
        self.assertRaises(CodecError, const.decode, self.ctx, OTHER)

    def test_wrap(self):
        """ensure `Wrap` correctness"""
        VALUE   = 1
        wrap    = Wrap[U8, E]
        encoded = wrap.encode(self.ctx, VALUE)
        decoded = wrap.decode(self.ctx, encoded)
        self.assertEqual(decoded, VALUE)
        self.assertIsInstance(decoded, E)
        self.assertRaises(ValueError, wrap.encode, self.ctx, -1)
