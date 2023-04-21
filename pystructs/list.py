"""
List Codec Implementations
"""
from typing import Type, List, Any

from .base import Int, codec
from .codec import Context, Codec

#** Variables **#
__all__ = ['SizedList', 'StaticList', 'GreedyList']

#** Classes **#

class SizedList(Codec):
    """
    Variable Sized List controlled by a Size-Hint Prefix
    """
    hint:      Int
    content:   Type[Codec]
    base_type: type = list
 
    def __class_getitem__(cls, hint: int, content: Type[Codec]) -> Type[Codec]:
        name   = f'{cls.__name__}[{hint!r},{content!r}]'
        hcodec = Int[hint]
        return codec(name, cls, hint=hcodec, content=content)
 
    @classmethod
    def encode(cls, ctx: Context, value: List[Any]) -> bytes:
        data  = bytearray()
        data += cls.hint.encode(ctx, len(value))
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @classmethod
    def decode(cls, ctx: Context, value: bytes) -> List[Any]:
        size    = cls.hint.decode(ctx, value)
        content = []
        for _ in range(0, size):
            item = cls.content.decode(ctx, value)
            content.append(item)
        return content

class StaticList(Codec):
    """
    Static List of the specified-type
    """
    size:      int
    content:   Type[Codec]
    base_type: type = list

    def __class_getitem__(cls, size: int, content: Type[Codec]) -> Type[Codec]:
        name = f'{cls.__name__}[{size!r},{content!r}]'
        return codec(name, cls, size=size, content=content)
 
    @classmethod
    def encode(cls, ctx: Context, value: List[Any]) -> bytes:
        assert len(value) == cls.size, f'len(array)[{len(value)}] != f{cls.size}'
        data = bytearray()
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @classmethod
    def decode(cls, ctx: Context, value: Any) -> list:
        content = []
        for _ in range(0, cls.size):
            item = cls.content.decode(ctx, value)
            content.append(item)
        return content

class GreedyList(Codec):
    """
    Greedy List that Consumes All Remaining Bytes
    """
    content:   Type[Codec]
    base_type: type = list

    def __class_getitem__(cls, content: Type[Codec]) -> Type[Codec]:
        name = f'{cls.__name__}[{content!r}]'
        return codec(name, cls, content=content)

    @classmethod
    def encode(cls, ctx: Context, value: Any) -> bytes:
        data = bytearray()
        for item in value:
            data += cls.content.encode(ctx, item)
        return bytes(data)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> Any:
        content = []
        while ctx.index < len(raw):
            item = cls.content.decode(ctx, raw)
            content.append(item)
        return content
