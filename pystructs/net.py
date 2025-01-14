"""
Network Type Serializer Definitions
"""
import re
from ipaddress import IPv4Address, IPv6Address
from typing import ClassVar, List, Optional, Tuple
from typing_extensions import Annotated

from .abc import Context, Field

#** Variables **#
__all__ = [
    'IPv4Field',
    'IPv6Field',
    'MACField',
    'DomainField',

    'IPv4',
    'IPv6',
    'MACAddr',
    'Domain'
]

#** Classes **#

class IPv4Field(Field[IPv4Address]):
    """
    IPv4Address Serializer Field Definition
    """

    def _pack(self, value: IPv4Address, ctx: Context) -> bytes:
        return ctx.track_bytes(value.packed)

    def _unpack(self, raw: bytes, ctx: Context) -> IPv4Address:
        return IPv4Address(ctx.slice(raw, 4))

class IPv6Field(Field[IPv6Address]):
    """
    IPv6Address Serializer Field Definition
    """

    def _pack(self, value: IPv6Address, ctx: Context) -> bytes:
        return ctx.track_bytes(value.packed)

    def _unpack(self, raw: bytes, ctx: Context) -> IPv6Address:
        return IPv6Address(ctx.slice(raw, 16))

class MACField(Field[str]):
    """
    MACAddress Serializer Field Definition
    """
    replace: re.Pattern = re.compile('[:.-]')

    def _pack(self, value: str, ctx: Context) -> bytes:
        packed = bytes.fromhex(self.replace.sub('', value))
        if len(packed) != 6:
            raise ValueError(f'invalid mac-address: {value!r}')
        return ctx.track_bytes(packed)

    def _unpack(self, raw: bytes, ctx: Context) -> str:
        mac = ctx.slice(raw, 6)
        if len(mac) != 6:
            raise OverflowError('too little data to unpack macaddr(6)')
        return ':'.join(f'{i:02x}' for i in mac)

class DomainField(Field[bytes]):
    """
    DNS Domain Serializer Field Definition
    """
    ptr_mask: ClassVar[int] = 0xC0

    def _pack(self, value: bytes, ctx: Context) -> bytes:
        encoded = bytearray()
        while value:
            # check if ptr is an option for remaining domain
            if value in ctx.domain_to_index:
                index      = ctx.domain_to_index[value]
                pointer    = index.to_bytes(2, 'big')
                encoded   += bytes((pointer[0] | self.ptr_mask, pointer[1]))
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

    def _unpack(self, raw: bytes, ctx: Context) -> bytes:
        domain: List[Tuple[bytes, Optional[int]]] = []
        while True:
            # check for length of domain component
            length = raw[ctx.index]
            ctx.index += 1
            if length == 0:
                break
            # check if name is a pointer
            if length & self.ptr_mask == self.ptr_mask:
                name  = bytes((length ^ self.ptr_mask, raw[ctx.index]))
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

#** Annotations **#

IPv4    = Annotated[IPv4Address, IPv4Field()]
IPv6    = Annotated[IPv6Address, IPv6Field()]
MACAddr = Annotated[str, MACField()]
Domain  = Annotated[bytes, DomainField()]
