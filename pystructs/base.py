"""
Base Common Sequence Types
"""
from abc import abstractmethod
import re
from ipaddress import IPv4Address, IPv6Address
from typing import ClassVar, Callable, Any, Protocol, Union, Type
from typing_extensions import runtime_checkable

from .codec import Codec, Context

#** Variables **#
__all__ = [
    'Const',
    'Int',
    'IpAddr',
    'MacAddr',
    'SizedBytes',
    'StaticBytes',
    'GreedyBytes',
    'Domain',
]

#** Functions **#

def codec(name: str, base: Type[Codec], **kwargs) -> Type[Codec]:
    """spawn new singleton codec type"""
    return type(name, (base, ), kwargs)

#** Classes **#

class Const(Codec):
    """
    Bytes Constant to Inlcude in Serialized Data
    """
    size:      int
    init:      bool = False
    default:   bytes
    base_type: type

    def __class_getitem__(cls, const: bytes) -> Type[Codec]:
        """generate const type w/ given const"""
        name = cls.__name__
        return codec(f'{name}[{const!r}]', cls, 
            size=len(const), default=const, base_type=bytes)
    
    @classmethod
    def sizeof(cls) -> int:
        return cls.size

    @classmethod
    def encode(cls, ctx: Context, value: bytes) -> bytes:
        assert value == cls.default, f'{value} does not match {cls}'
        ctx.index += cls.size
        return cls.default
    
    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        value = ctx.slice(raw, cls.size)
        assert value == cls.default, f'{value} does not match {cls}'
        return value

@runtime_checkable
class IntLike(Protocol):

    @abstractmethod
    def __int__(self) -> int:
        raise NotImplementedError

class Int(Codec):
    """
    Variable Size Integer Codec Definition

    Examples: Int[16], Int[32], Int[64, MyIntEnum]
    """
    size: ClassVar[int]
    wrap: ClassVar[Callable[[int], Any]]
    base_type: type
 
    def __class_getitem__(cls, s: Union[int, tuple]) -> Type[Codec]:
        """generate custom Int subclass with the given options"""
        size = s if isinstance(s, int) else s[0]
        wrap = s[1] if isinstance(s, tuple) and len(s) > 1 else lambda x: x
        name = s[2] if isinstance(s, tuple) and len(s) > 2 else cls.__name__
        assert size % 8 == 0, 'size must be multiple of eight'
        cname = f'{name}[{size}]'
        return codec(cname, cls, size=size // 8, wrap=wrap, base_type=IntLike)
    
    @classmethod
    def sizeof(cls) -> int:
        return cls.size

    @classmethod
    def encode(cls, ctx: Context, value: IntLike) -> bytes:
        ctx.index += cls.size
        return int(value).to_bytes(cls.size, 'big')

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> int:
        data = ctx.slice(raw, cls.size)
        size = cls.size * 8
        assert len(data) == cls.size, f'len(bytes)[{len(data)}] != Int[{size}]'
        value = int.from_bytes(data, 'big')
        return cls.wrap(value)

class IpAddr(Codec):
    """
    Ipv4/Ipv6 Address Variable Codec Definition

    Example: IpAddr['ipv4'] or IpAddr['ipv6']
    """
    size:      int
    ip_type:   Union[Type[IPv4Address], Type[IPv6Address]]
    base_type: Union[type, tuple] = (str, bytes, IPv4Address)

    def __class_getitem__(cls, iptype: str) -> Type[Codec]:
        """generate ipv4 or ipv6 ipaddress supporting codec type"""
        assert iptype in ('ipv4', 'ipv6'), 'invalid ipaddress type'
        size = 4 if iptype == 'ipv4' else 16
        addr = IPv4Address if iptype == 'ipv4' else IPv6Address
        return codec(f'IPv{iptype[-1]}', cls, size=size, ip_type=addr)

    @classmethod
    def sizeof(cls) -> int:
        return cls.size

    @classmethod
    def encode(cls, ctx: Context, value: Union[str, bytes]) -> bytes:
        ipaddr = value if isinstance(value, cls.ip_type) else cls.ip_type(value)
        packed = ipaddr.packed
        ctx.index += cls.size
        return packed

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> Union[IPv4Address, IPv6Address]:
        data = ctx.slice(raw, cls.size)
        return cls.ip_type(data)

class MacAddr(Codec):
    """
    Serialized MacAddress Codec
    """
    base_type: type       = str
    replace:   re.Pattern = re.compile('[:.-]')
  
    @classmethod
    def sizeof(cls) -> int:
        return 6

    @classmethod
    def encode(cls, ctx: Context, value: str) -> bytes:
        content = bytes.fromhex(cls.replace.sub('', value))
        ctx.index += len(content)
        return content

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> str:
        return ':'.join(f'{i:02x}' for i in ctx.slice(raw, 6))

class SizedBytes(Codec):
    """
    Variable Sized Bytes Codec with Length Denoted by Prefixed Integer

    Example: SizedBytes[32]
    """
    hint:      Int
    base_type: type
 
    def __class_getitem__(cls, hint: int) -> Type[Codec]:
        name   = cls.__name__
        hcodec = Int[hint]
        return codec(f'{name}[{hint!r}]', cls, hint=hcodec, base_type=bytes)

    @classmethod
    def encode(cls, ctx: Context, content: bytes) -> bytes:
        hint = cls.hint.encode(ctx, len(content))
        ctx.index += len(content)
        return hint + content

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        hint = cls.hint.decode(ctx, raw)
        return ctx.slice(raw, hint)

class StaticBytes(Codec):
    """
    Variable Staticly Sized Bytes Codec of a Pre-Determined Length

    Example: StaticBytes[32]
    """
    size:      int
    base_type: type

    def __class_getitem__(cls, size: int) -> Type[Codec]:
        name = cls.__name__
        return codec(f'{name}[{size!r}]', cls, size=size, base_type=bytes)
    
    @classmethod
    def sizeof(cls) -> int:
        return cls.size

    @classmethod
    def encode(cls, ctx: Context, content: bytes) -> bytes:
        assert len(content) <= cls.size, f'len(content) >= {cls.size} bytes'
        ctx.index += cls.size
        content = content.ljust(cls.size, b'\x00')
        return content

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        return ctx.slice(raw, cls.size).rstrip(b'\x00')

class GreedyBytes(Codec):
    """
    Variable Bytes that Greedily Collects all Bytes left in Data
    """
    base_type: type = bytes
 
    @classmethod
    def encode(cls, ctx: Context, value: Any) -> bytes:
        ctx.index += len(value)
        return value

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        data = raw[ctx.index:]
        ctx.index += len(data)
        return data

class Domain(Codec):
    """
    DNS Style Domain Serialization w/ Index Pointers to Eliminate Duplicates
    """
    ptr_mask:  int  = 0xC0
    base_type: type = bytes

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
