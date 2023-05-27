"""
ByteRange Serialization Implementations
"""
from typing import Protocol, ClassVar, Type
from typing_extensions import Annotated, runtime_checkable

from .codec import *
from .integer import Integer

#** Variables **#
__all__ = ['SizedBytes', 'StaticBytes', 'GreedyBytes']

#** Classes **#

@runtime_checkable
class SizedBytes(Codec[bytes], Protocol):
    """
    Variable Sized Bytes Codec with Length Denoted by Prefixed Integer

    Example: SizedBytes[U8]
    """
    hint:      ClassVar[Integer]
    type:      ClassVar[Type]  = bytes 
    base_type: ClassVar[tuple] = (bytes, )

    def __class_getitem__(cls, hint: Type):
        hint = deanno(hint)
        if not isinstance(hint, type) or not isinstance(hint, Integer):
            raise ValueError(f'{cname(cls)} invalid hint: {hint!r}')
        name = f'{cname(cls)}[{cname(hint)}]'
        return type(name, (cls, ), {'hint': hint})

    @classmethod
    def encode(cls, ctx: Context, content: bytes) -> bytes:
        hint = cls.hint.encode(ctx, len(content))
        ctx.index += len(content)
        return hint + content

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        hint = cls.hint.decode(ctx, raw)
        return ctx.slice(raw, hint)

@runtime_checkable
class StaticBytes(Codec[bytes], Protocol):
    """
    Variable Staticly Sized Bytes Codec of a Pre-Determined Length

    Example: StaticBytes[32]
    """
    size:      ClassVar[int]
    type:      ClassVar[Type]  = bytes 
    base_type: ClassVar[tuple] = (bytes, )

    def __class_getitem__(cls, size: int):
        name = f'{cname(cls)}[{size}]'
        return type(name, (cls, ), {'size': size})

    @classmethod
    def encode(cls, ctx: Context, content: bytes) -> bytes:
        if len(content) > cls.size:
            raise CodecError(f'datalen={len(content)} >= {cls.size} bytes')
        ctx.index += cls.size
        content = content.ljust(cls.size, b'\x00')
        return content

    @classmethod
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
