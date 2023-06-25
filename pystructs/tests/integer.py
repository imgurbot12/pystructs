"""
PyStructs Integer UnitTests
"""
import random
import unittest
from typing import List

from ..codec import *
from ..integer import *

#** Variables **#
__all__ = ['IntegerTests']

SIGNED_RAW   = [I8, I16, I24, I32, I48, I64, I128]
UNSIGNED_RAW = [U8, U16, U24, U32, U64, U128]

SIGNED:   List[Signed]   = [deanno(i, Signed) for i in SIGNED_RAW]
UNSIGNED: List[Unsigned] = [deanno(i, Unsigned) for i in UNSIGNED_RAW]
INTEGERS: List[Integer]  = [*SIGNED, *UNSIGNED]

#** Classes **#

class IntegerTests(unittest.TestCase):
    """Integer Unit-Tests"""

    @property
    def ctx(self):
        return Context()

    def test_protocol(self):
        """validate protocol usage errors"""
        self.assertRaises(TypeError, Integer.decode, self.ctx, b'')
        self.assertRaises(TypeError, Signed.decode, self.ctx, b'')
        self.assertRaises(TypeError, Unsigned.decode, self.ctx, b'')

    def test_min(self):
        """validate `Integer` min-value contraints"""
        for i in INTEGERS:
            with self.subTest(int=cname(i)):
                self.assertRaises(CodecError, i.encode, self.ctx, i.min - 1)

    def test_max(self):
        """validate `Integer` max-size constraints"""
        for i in INTEGERS:
            with self.subTest(int=cname(i)):
                self.assertRaises(CodecError, i.encode, self.ctx, i.max + 1)

    def test_wrongsize(self):
        """validate `Integer` size constraints"""
        for i in INTEGERS:
            with self.subTest(int=cname(i)):
                ctx = self.ctx
                i.decode(ctx, bytes(128))
                self.assertEqual(ctx.index, i.size)
                self.assertRaises(CodecError, i.decode, self.ctx, b'')
 
    def test_correctness(self):
        """validate `Integer` correctness"""
        for i in INTEGERS:
            number = random.randint(i.min+1, i.max-1)
            with self.subTest(int=cname(i), number=number):
                enc1 = i.encode(self.ctx, number)
                dec  = i.decode(self.ctx, enc1)
                enc2 = i.encode(self.ctx, number)
                self.assertEqual(enc1, enc2)
                self.assertEqual(dec, number)
