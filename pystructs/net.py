"""
Network Related Codec Implementations
"""
import re
from ipaddress import IPv4Address, IPv6Address
from typing import Union, Type, Protocol, ClassVar

from .codec import *

#** Variables **#
__all__ = [
    'IpType',
    'IpAddress',
    'IPv4',
    'IPv6',
    'MacAddr',
    'Domain',
]

#: typehint for valid iptypes
IpType = Union[str, bytes, IPv4Address, IPv6Address]

#: typehint for both ipaddr types
IpTypeHint = Union[Type[IPv4Address], Type[IPv6Address]]

#** Classes **#

class IpAddress(Codec[T], Protocol):
    """
    Ipv4/Ipv6 Address Variable Codec Definition
    """
    size:      ClassVar[int]
    ip_type:   ClassVar[IpTypeHint]
    base_type: ClassVar[tuple]

    @classmethod
    def encode(cls, ctx: Context, value: IpType) -> bytes:
        ipaddr = value if isinstance(value, cls.ip_type) else cls.ip_type(value)
        packed = ipaddr.packed
        ctx.index += cls.size
        return packed

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> Union[IPv4Address, IPv6Address]:
        data = ctx.slice(raw, cls.size)
        return cls.ip_type(data)

class IPv4(IpAddress[IPv4Address]):
    """
    IPv4 Codec Serialization
    """
    size      = 4
    ip_type   = IPv4Address
    base_type = (str, bytes, IPv4Address)

class IPv6(IpAddress[IPv6Address]):
    """
    IPv6 Codec Serialization
    """
    size      = 16
    ip_type   = IPv6Address
    base_type = (str, bytes, IPv6Address) 

class MacAddr(Codec[str]):
    """
    Serialized MacAddress Codec
    """
    base_type: tuple      = (str, )
    replace:   re.Pattern = re.compile('[:.-]')

    @classmethod
    def encode(cls, ctx: Context, value: str) -> bytes:
        content = bytes.fromhex(cls.replace.sub('', value))
        ctx.index += len(content)
        return content

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> str:
        return ':'.join(f'{i:02x}' for i in ctx.slice(raw, 6))

class Domain(Codec[bytes]):
    """
    DNS Style Domain Serialization w/ Index Pointers to Eliminate Duplicates
    """
    ptr_mask:  int   = 0xC0
    base_type: tuple = (bytes, )

    @classmethod
    def encode(cls, ctx: Context, value: bytes) -> bytes:
        encoded = bytearray()
        while value:
            # check if ptr is an option for remaining domain
            if value in ctx.domain_to_index:
                index      = ctx.domain_to_index[value]
                pointer    = index.to_bytes(2, 'big')
                encoded   += bytes((pointer[0] | cls.ptr_mask, pointer[1]))
                ctx.index += 2 
                return bytes(encoded)
            # save partial domain as index
            ctx.save_domain(value, ctx.index)
            # handle components of name
            split       = value.split(b'.', 1)
            name, value = split if len(split) == 2 else (split[0], b'')
            encoded    += len(name).to_bytes(1, 'big') + name
            ctx.index  += 1 + len(name)
        # write final zeros before returning final encoded data
        encoded   += b'\x00'
        ctx.index += 1
        return bytes(encoded)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        domain = []
        while True:
            # check for length of domain component
            length     = raw[ctx.index]
            ctx.index += 1
            if length == 0:
                break
            # check if name is a pointer
            if length & cls.ptr_mask == cls.ptr_mask:
                name  = bytes((length ^ cls.ptr_mask, raw[ctx.index]))
                index = int.from_bytes(name, 'big')
                base  = ctx.index_to_domain[index]
                domain.append((base, None))
                ctx.index += 1
                break
            # slice name from bytes and updated counter
            idx  = ctx.index - 1
            name = ctx.slice(raw, length)
            domain.append((name, idx))
        # save domain components
        for n, (name, index) in enumerate(domain, 0):
            if index is None:
                continue
            subname = b'.'.join(name for name, _ in domain[n:])
            ctx.save_domain(subname, index)
        return b'.'.join(name for name, _ in domain)
