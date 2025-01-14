"""
PyStructs Standard Serializer Field UnitTests
"""
import random
import unittest
from typing import List

from .. import *

#** Variables **#
__all__ = ['StdSerializerTests']

INTEGERS: List[IntField] = [
    IntField(size=1, signed=False),
    IntField(size=2, signed=False),
    IntField(size=4, signed=False),
    IntField(size=6, signed=False),
    IntField(size=8, signed=False),
    IntField(size=16, signed=False),
    IntField(size=1, signed=True),
    IntField(size=2, signed=True),
    IntField(size=4, signed=True),
    IntField(size=6, signed=True),
    IntField(size=8, signed=True),
    IntField(size=16, signed=True),
]

#** Functions **#

def imin(i: IntField) -> int:
    return (- int(2**(8*i.size) / 2)) if i.signed else 0

def imax(i: IntField) -> int:
    max = int(2**(8*i.size))
    return int(max / 2) if i.signed else max

#** Classes **#

class StdSerializerTests(unittest.TestCase):
    """Standard Type Serializer Unit-Tests"""

    @property
    def ctx(self):
        return Context()

    def test_int_underflow(self):
        """
        ensure int field errors on value underflow
        """
        for i in INTEGERS:
            with self.subTest(i=f'int({i.size})'):
                self.assertRaises(OverflowError, i._pack, imin(i) - 1, self.ctx)

    def test_int_overflow(self):
        """
        ensure int field errors on value overflow
        """
        for i in INTEGERS:
            with self.subTest(i=f'int({i.size})'):
                self.assertRaises(OverflowError, i._pack, imax(i) + 1, self.ctx)

    def test_int_undersize(self):
        """
        ensure int field errors when too little data is present
        """
        for i in INTEGERS:
            with self.subTest(i=f'int({i.size})'):
                ctx    = Context()
                s_data = b'\xff' * i.size
                e_data = b'\xff' * (i.size - 1)
                i._unpack(s_data, ctx)
                self.assertEqual(ctx.index, i.size)
                self.assertRaises(ValueError, i._unpack, e_data, self.ctx)

    def test_int_correctness(self):
        """
        ensure int field packs/unpacks correctly
        """
        for i in INTEGERS:
            number = random.randint(imin(i)+1, imax(i)-1)
            with self.subTest(i=f'int({i.size})'):
                packed   = i._pack(number, self.ctx)
                unpacked = i._unpack(packed, self.ctx)
                repacked = i._pack(number, self.ctx)
                self.assertEqual(number, unpacked)
                self.assertEqual(packed, repacked)

    def test_bytes_hinted(self):
        """
        ensure size-hinted bytestring packs/unpacks correctly
        """
        value    = b'hinted'
        hinted   = HintedBytes(U8)
        packed   = hinted._pack(value, self.ctx)
        unpacked = hinted._unpack(packed, self.ctx)
        self.assertEqual(hinted.hint.size + len(value), len(packed))
        self.assertEqual(packed[hinted.hint.size:], value)
        self.assertEqual(unpacked, value)

    def test_bytes_static(self):
        """
        ensure static-size bytestring packs/unpacks correctly
        """
        value    = b'static'
        static   = StaticBytes(128)
        packed   = static._pack(value, self.ctx)
        unpacked = static._unpack(packed, self.ctx)
        self.assertEqual(static.size, len(packed))
        self.assertEqual(unpacked, value)
        self.assertRaises(OverflowError, static._pack, bytes(129), self.ctx)

    def test_bytes_greedy(self):
        """
        ensure greedy bytestring packs/unpacks correctly
        """
        value    = b'greedy'
        greedy   = GreedyBytes()
        packed   = greedy._pack(value, self.ctx)
        unpacked = greedy._unpack(packed, self.ctx)
        self.assertEqual(value, unpacked)
        self.assertEqual(packed, unpacked)

    def test_list_hinted(self):
        """
        ensure size-hinted list packs/unpacks correctly
        """
        value    = [b'hinted', b'hinted-2', b'hinted-3']
        hinted   = HintedList(U8, StaticBytes(8))
        packed   = hinted._pack(value, self.ctx)
        unpacked = hinted._unpack(packed, self.ctx)
        repacked = hinted._pack(unpacked, self.ctx)
        self.assertEqual(unpacked, value)
        self.assertEqual(packed, repacked)

    def test_list_static(self):
        """
        ensure static-sized list packs/unpacks correctly
        """
        value    = [b'hinted', b'hinted-2', b'hinted-3']
        static   = StaticList(3, StaticBytes(8))
        packed   = static._pack(value, self.ctx)
        unpacked = static._unpack(packed, self.ctx)
        repacked = static._pack(unpacked, self.ctx)
        self.assertEqual(unpacked, value)
        self.assertEqual(packed, repacked)
        self.assertRaises(OverflowError, static._pack, [b''] * 4, self.ctx)

    def test_list_greedy(self):
        """
        ensure greedy list packs/unpacks correctly
        """
        value    = [b'hinted', b'hinted-2', b'hinted-3']
        greedy   = GreedyList(StaticBytes(8))
        packed   = greedy._pack(value, self.ctx)
        unpacked = greedy._unpack(packed, self.ctx)
        repacked = greedy._pack(unpacked, self.ctx)
        self.assertEqual(unpacked, value)
        self.assertEqual(packed, repacked)

    def test_const(self):
        """
        ensure const packs/unpacks correctly
        """
        value    = b'hello'
        const    = Const(value)
        packed   = const._pack(value, self.ctx)
        unpacked = const._unpack(packed, self.ctx)
        repacked = const._pack(unpacked, self.ctx)
        self.assertEqual(unpacked, value)
        self.assertEqual(packed, repacked)
        self.assertRaises(ValueError, const._pack, b'hell', self.ctx)
        self.assertRaises(ValueError, const._unpack, b'hell', self.ctx)

