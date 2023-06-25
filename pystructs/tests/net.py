"""
PyStructs Integer UnitTests
"""
import unittest
from ipaddress import IPv4Address, IPv6Address, AddressValueError

from ..codec import *
from ..net import *
from ..net import IpAddress

#** Variables **#
__all__ = ['NetTests']

DOMAIN = b'www.example.com'

MACSTR   = '01:02:03:04:05:06'
MACBYTES = bytes((1, 2, 3, 4, 5, 6))

EXAMPLE_IP4 = IPv4Address('127.0.0.1')
EXAMPLE_IP6 = IPv6Address('::1')

#** Classes **#

class NetTests(unittest.TestCase):
    """Net Related UnitTests"""

    @property
    def ctx(self):
        return Context()

    def test_protocol(self):
        """validate protocol usage errors"""
        self.assertRaises(TypeError, IpAddress.decode, self.ctx, b'')

    def test_ipv4(self):
        """validate `IPv4` correctness"""
        ipv4    = deanno(IPv4, Codec)
        encoded = ipv4.encode(self.ctx, str(EXAMPLE_IP4))
        decoded = ipv4.decode(self.ctx, encoded)
        recoded = ipv4.encode(self.ctx, decoded)
        self.assertEqual(decoded, EXAMPLE_IP4)
        self.assertEqual(encoded, recoded)
        self.assertRaises(AddressValueError, ipv4.encode, self.ctx, EXAMPLE_IP6)

    def test_ipv6(self):
        """validate `IPv6` correctness"""
        ipv6    = deanno(IPv6, Codec)
        encoded = ipv6.encode(self.ctx, str(EXAMPLE_IP6))
        decoded = ipv6.decode(self.ctx, encoded)
        recoded = ipv6.encode(self.ctx, decoded)
        self.assertEqual(decoded, EXAMPLE_IP6)
        self.assertEqual(encoded, recoded)
        self.assertRaises(AddressValueError, ipv6.encode, self.ctx, EXAMPLE_IP4)

    def test_macaddr(self):
        """validate `MacAddr` correctness"""
        macaddr = deanno(MacAddr, Codec)
        encoded = macaddr.encode(self.ctx, MACSTR)
        decoded = macaddr.decode(self.ctx, encoded)
        recoded = macaddr.encode(self.ctx, MACBYTES)
        self.assertEqual(decoded, MACSTR)
        self.assertEqual(encoded, recoded)
        self.assertRaises(CodecError, macaddr.encode, self.ctx, bytes(7))

    def test_domain(self):
        """validate `Domain` correctness"""
        domain  = deanno(Domain, Codec)
        encoded = domain.encode(self.ctx, DOMAIN)
        decoded = domain.decode(self.ctx, encoded)
        recoded = domain.encode(self.ctx, decoded)
        self.assertEqual(decoded, DOMAIN)
        self.assertEqual(encoded, recoded)
