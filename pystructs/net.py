"""
Network Related Codec Implementations
"""
import re
from ipaddress import IPv4Address, IPv6Address
from typing import *
from typing_extensions import Annotated

from .codec import *

#** Variables **#
__all__ = [
    'IpType',
    'Ipv4Type',
    'Ipv6Type',
    'IpAddress',
    'IPv4',
    'IPv6',
    'MacAddr',
    'Domain',
]

#: generic typevar for ipv4/ipv6
IP = TypeVar('IP', IPv4Address, IPv6Address)

#: typehint for valid iptypes
IpType = Union[str, bytes, IPv4Address, IPv6Address]

#: typehint for valid ipv4 types
Ipv4Type = Union[str, bytes, IPv4Address]

#: typehitn for valid ipv6 types
Ipv6Type = Union[str, bytes, IPv6Address]

#: typehint for both ipaddr types
IpTypeHint = Union[Type[IPv4Address], Type[IPv6Address]]

#** Classes **#

@protocol
class IpAddress(Codec[IP], Protocol):
    """
    Ipv4/Ipv6 Address Variable Codec Definition
    """
    size:      ClassVar[int]
    ip_type:   ClassVar[IpTypeHint]
    base_type: ClassVar[tuple]

    @protomethod
    def encode(cls, ctx: Context, value: IpType) -> bytes:
        ipaddr = value if isinstance(value, cls.ip_type) else cls.ip_type(value)
        packed = ipaddr.packed #type: ignore
        ctx.index += cls.size
        return packed

    @protomethod
    def decode(cls, ctx: Context, raw: bytes) -> IP:
        data = ctx.slice(raw, cls.size)
        return cls.ip_type(data) #type: ignore

class _IPv4(IpAddress[IPv4Address]):
    """
    IPv4 Codec Serialization
    """
    size      = 4
    ip_type   = IPv4Address
    base_type = (str, bytes, IPv4Address)

class _IPv6(IpAddress[IPv6Address]):
    """
    IPv6 Codec Serialization
    """
    size      = 16
    ip_type   = IPv6Address
    base_type = (str, bytes, IPv6Address) 

class _MacAddr(Codec[str]):
    """
    Serialized MacAddress Codec
    """
    replace:   re.Pattern      = re.compile('[:.-]')
    base_type: ClassVar[tuple] = (str, bytes)

    @classmethod
    def encode(cls, ctx: Context, value: Union[str, bytes]) -> bytes:
        if isinstance(value, bytes) and len(value) != 6:
            raise CodecError(f'invalid mac-address: {value!r}')
        if isinstance(value, str):
            value = bytes.fromhex(cls.replace.sub('', value))
        ctx.index += len(value)
        return value

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> str:
        return ':'.join(f'{i:02x}' for i in ctx.slice(raw, 6))

class _Domain(Codec[bytes]):
    """
    DNS Style Domain Serialization w/ Index Pointers to Eliminate Duplicates
    """
    ptr_mask:  ClassVar[int]   = 0xC0
    base_type: ClassVar[tuple] = (bytes, )

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
        domain: List[Tuple[bytes, Optional[int]]] = []
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

IPv4    = Annotated[Ipv4Type, _IPv4]
IPv6    = Annotated[Ipv6Type, _IPv6]
MacAddr = Annotated[Union[str, bytes], _MacAddr]
Domain  = Annotated[bytes, _Domain]
