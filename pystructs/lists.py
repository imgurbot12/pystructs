"""
List Codec Implementations
"""
from typing import Protocol, ClassVar, Type, Generic, List, Tuple

from .codec import *
from .integer import I, Integer

#** Variables **#
__all__ = ['SizedList', 'StaticList', 'GreedyList']

#** Classes **#

@protocol
class SizedList(Codec[T], Protocol[I, T]):
    """
    Variable Sized List controlled by a Size-Hint Prefix
    """
    hint:      ClassVar[Integer]
    content:   ClassVar[Codec]
    base_type: ClassVar[tuple] = (list, )

    def __class_getitem__(cls, s: Tuple[I, T]):
        hint, content = s
        hint, content = deanno(hint, Integer), deanno(content, Codec)
        name = f'{cname(cls)}[{hint!r},{content!r}]'
        return type(name, (cls, ), {'hint': hint, 'content': content})
 
    @protomethod
    def encode(cls, ctx: Context, value: List[T]) -> bytes:
        data  = bytearray()
        data += cls.hint.encode(ctx, len(value))
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @protomethod
    def decode(cls, ctx: Context, raw: bytes) -> List[T]:
        size    = cls.hint.decode(ctx, raw)
        content = []
        for _ in range(0, size):
            item = cls.content.decode(ctx, raw)
            content.append(item)
        return content

@protocol
class StaticList(Codec[T], Protocol, Generic[I, T]):
    """
    Static List of the specified-type
    """
    size:      ClassVar[int]
    content:   ClassVar[Type[Codec]]
    base_type: ClassVar[tuple] = (list, )

    def __class_getitem__(cls, s: Tuple[I, T]):
        size, content = s
        size    = deanno(size, int)
        content = deanno(content, Codec)
        name    = f'{cname(cls)}[{size!r},{content!r}]'
        return type(name, (cls,), {'size': size, 'content': content})
 
    @protomethod
    def encode(cls, ctx: Context, value: List[T]) -> bytes:
        if len(value) != cls.size:
            raise CodecError(f'arraylen={len(value)} != {cls.size}')
        data = bytearray()
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @protomethod
    def decode(cls, ctx: Context, raw: bytes) -> List[T]:
        content = []
        for _ in range(0, cls.size):
            item = cls.content.decode(ctx, raw)
            content.append(item)
        return content

@protocol
class GreedyList(Codec[T], Protocol):
    """
    Greedy List that Consumes All Remaining Bytes
    """
    content:   ClassVar[Type[Codec]]
    base_type: ClassVar[tuple] = (list, )

    def __class_getitem__(cls, anno_content: T):
        content = deanno(anno_content, Codec)
        name    = f'{cname(cls)}[{content!r}]'
        return type(name, (cls,), {'content': content})

    @protomethod
    def encode(cls, ctx: Context, value: List[T]) -> bytes:
        data = bytearray()
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @protomethod
    def decode(cls, ctx: Context, raw: bytes) -> List[T]:
        content = []
        while ctx.index < len(raw):
            item = cls.content.decode(ctx, raw)
            content.append(item)
        return content
