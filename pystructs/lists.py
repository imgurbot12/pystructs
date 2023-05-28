"""
List Codec Implementations
"""
from typing import Protocol, ClassVar, Type
from typing_extensions import Annotated, runtime_checkable

from .codec import *
from .integer import Integer

#** Variables **#
__all__ = ['SizedList', 'StaticList', 'GreedyList']

#** Classes **#

@runtime_checkable
class SizedList(Codec[list], Protocol):
    """
    Variable Sized List controlled by a Size-Hint Prefix
    """
    hint:      ClassVar[Integer]
    content:   ClassVar[Codec]
    base_type: ClassVar[tuple] = (list, )

    def __class_getitem__(cls, s: tuple):
        hint, content = s
        hint, content = deanno(hint), deanno(content)
        if not isinstance(hint, type) or not isinstance(hint, Integer):
            raise ValueError(f'{cname(cls)} invalid hint: {hint!r}')
        name = f'{cname(cls)}[{hint!r},{content!r}]'
        return type(name, (cls, ), {'hint': hint, 'content': content})
 
    @classmethod
    def encode(cls, ctx: Context, value: list) -> bytes:
        data  = bytearray()
        data += cls.hint.encode(ctx, len(value))
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> list:
        size    = cls.hint.decode(ctx, raw)
        content = []
        for _ in range(0, size):
            item = cls.content.decode(ctx, raw)
            content.append(item)
        return content

@runtime_checkable
class StaticList(Codec[list], Protocol):
    """
    Static List of the specified-type
    """
    size:      ClassVar[int]
    content:   ClassVar[Type[Codec]]
    base_type: ClassVar[tuple] = (list, )

    def __class_getitem__(cls, s: tuple):
        size, content = s
        content = deanno(content)
        name    = f'{cname(cls)}[{size!r},{content!r}]'
        return type(name, (cls,), {'size': size, 'content': content})
 
    @classmethod
    def encode(cls, ctx: Context, value: list) -> bytes:
        if len(value) != cls.size:
            raise CodecError(f'arraylen={len(value)} != {cls.size}')
        data = bytearray()
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> list:
        content = []
        for _ in range(0, cls.size):
            item = cls.content.decode(ctx, raw)
            content.append(item)
        return content

class _GreedyList(Codec[list]):
    """
    Greedy List that Consumes All Remaining Bytes
    """
    content:   ClassVar[Type[Codec]]
    base_type: ClassVar[tuple] = (list, )

    def __class_getitem__(cls, content: Type[Codec]) -> Type[Codec]:
        name    = f'{cname(cls)}[{content!r}]'
        content = deanno(content)
        return type(name, (cls,), {'content': content})

    @classmethod
    def encode(cls, ctx: Context, value: list) -> bytes:
        data = bytearray()
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> list:
        content = []
        while ctx.index < len(raw):
            item = cls.content.decode(ctx, raw)
            content.append(item)
        return content

GreedyList = Annotated[list, _GreedyList]