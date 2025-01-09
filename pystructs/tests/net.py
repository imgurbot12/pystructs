"""
PyStructs Network Serializer UnitTests
"""
import unittest
from ipaddress import IPv4Address, IPv6Address

from .. import *

#** Variables **#
__all__ = ['NetSerializerTests']

#** Classes **#

class NetSerializerTests(unittest.TestCase):
    """Network Type Serializer UnitTests"""

    @property
    def ctx(self):
        return Context()

    def test_ipv4(self):
        """
        ensure net ipv4 field packs/unpacks correctly
        """
        value    = IPv4Address('127.0.0.1')
        ipv4     = IPv4Field()
        packed   = ipv4._pack(value, self.ctx)
        unpacked = ipv4._unpack(packed, self.ctx)
        repacked = ipv4._pack(unpacked, self.ctx)
        self.assertEqual(unpacked, value)
        self.assertEqual(packed, repacked)
        self.assertRaises(ValueError, ipv4._unpack, b'\x00' * 3, self.ctx)

    def test_ipv6(self):
        """
        ensure net ipv6 field packs/unpacks correctly
        """
        value    = IPv6Address('::1')
        ipv6     = IPv6Field()
        packed   = ipv6._pack(value, self.ctx)
        unpacked = ipv6._unpack(packed, self.ctx)
        repacked = ipv6._pack(unpacked, self.ctx)
        self.assertEqual(unpacked, value)
        self.assertEqual(packed, repacked)
        self.assertRaises(ValueError, ipv6._unpack, b'\x00' * 15, self.ctx)

    def test_macaddr(self):
        """
        ensure net mac-addr field packs/unpacks correctly
        """
        value    = '01:02:03:04:05:06'
        mac      = MACField()
        packed   = mac._pack(value, self.ctx)
        unpacked = mac._unpack(packed, self.ctx)
        repacked = mac._pack(unpacked, self.ctx)
        self.assertEqual(unpacked, value)
        self.assertEqual(packed, repacked)
        self.assertEqual(packed, bytes((1, 2, 3, 4, 5, 6)))
        self.assertRaises(ValueError, mac._pack, value[:-3], self.ctx)
        self.assertRaises(ValueError, mac._pack, value + ':07', self.ctx)
        self.assertRaises(OverflowError, mac._unpack, b'\x00' * 5, self.ctx)

    def test_domain(self):
        """
        ensure net domain field packs/unpacks correctly
        """
        value    = b'www.example.com'
        domain   = DomainField()
        packed   = domain._pack(value, self.ctx)
        unpacked = domain._unpack(packed, self.ctx)
        repacked = domain._pack(unpacked, self.ctx)
        self.assertEqual(unpacked, value)
        self.assertEqual(packed, repacked)
