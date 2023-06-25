"""
ByteRange Serialization Implementations
"""
from typing import Protocol, ClassVar, Type
from typing_extensions import Annotated

from .codec import *
from .integer import Integer

#** Variables **#
__all__ = ['SizedBytes', 'StaticBytes', 'GreedyBytes']

#** Classes **#

@protocol
class SizedBytes(Codec[T], Protocol):
    """
    Variable Sized Bytes Codec with Length Denoted by Prefixed Integer

    Example: SizedBytes[U8]
    """
    hint:      ClassVar[Integer]
    type:      ClassVar[Type]  = bytes 
    base_type: ClassVar[tuple] = (bytes, )

    def __class_getitem__(cls, anno_hint: T):
        hint = deanno(anno_hint, Integer)
        name = f'{cname(cls)}[{cname(hint)}]'
        return type(name, (cls, ), {'hint': hint})

    @protomethod
    def encode(cls, ctx: Context, content: bytes) -> bytes:
        hint = cls.hint.encode(ctx, len(content))
        ctx.index += len(content)
        return hint + content

    @protomethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        hint = cls.hint.decode(ctx, raw)
        return ctx.slice(raw, hint)

@protocol
class StaticBytes(Codec[bytes], Protocol):
    """
    Variable Staticly Sized Bytes Codec of a Pre-Determined Length

    Example: StaticBytes[32]
    """
    size:      ClassVar[int]
    type:      ClassVar[Type]  = bytes 
    base_type: ClassVar[tuple] = (bytes, )

    def __class_getitem__(cls, size: int):
        size = deanno(size, int)
        name = f'{cname(cls)}[{size}]'
        return type(name, (cls, ), {'size': size})

    @protomethod
    def encode(cls, ctx: Context, content: bytes) -> bytes:
        if len(content) > cls.size:
            raise CodecError(f'datalen={len(content)} >= {cls.size} bytes')
        ctx.index += cls.size
        content = content.ljust(cls.size, b'\x00')
        return content

    @protomethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        return ctx.slice(raw, cls.size).rstrip(b'\x00')

class _GreedyBytes(Codec[bytes]):
    """
    Variable Bytes that Greedily Collects all Bytes left in Data
    """
    base_type: ClassVar[tuple] = (bytes, )
 
    @classmethod
    def encode(cls, ctx: Context, value: bytes) -> bytes:
        ctx.index += len(value)
        return value

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        data = raw[ctx.index:]
        ctx.index += len(data)
        return data

GreedyBytes = Annotated[bytes, _GreedyBytes]
