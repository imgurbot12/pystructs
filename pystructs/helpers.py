"""
Misc Helper Codec Implementations
"""
from enum import Enum
from typing import ClassVar, Protocol, Tuple, Type, Any, List

from .codec import *

#** Variables **#
__all__ = ['Const', 'Wrap']

#** Functions **#

def enum_types(e: Type[Enum]) -> set:
    """retrieve all types contained with enum values"""
    return set(type(v.value) for v in e)

#** Classes **#

class Const(Codec[bytes], Protocol):
    """
    Bytes Constant to Inlcude in Serialized Data
    """
    const:     ClassVar[bytes]
    base_type: ClassVar[tuple] = (bytes, )
    
    def __class_getitem__(cls, const: bytes):
        name = f'Const[{len(const)}]'
        return type(name, (cls, ), {'const': const})
 
    @classmethod
    def encode(cls, ctx: Context, value: bytes) -> bytes:
        """encode and check const matches expected value"""
        if value != cls.const:
            raise CodecError(f'{cname(cls)} invalid value: {value!r}')
        ctx.index += len(cls.const)
        return value

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> bytes:
        """decode const and ensure value matches expected result"""
        value = ctx.slice(raw, len(cls.const))
        if value != cls.const:
            raise CodecError(f'{cname(cls)} invalid const: {value!r}')
        return value

class Wrap(Codec[T], Protocol):
    """
    Content Wrapper/Unwrapper for Types like Enums
    """
    wrap:      ClassVar[Type]
    codec:     ClassVar[Codec]
    base_type: ClassVar[tuple]

    def __class_getitem__(cls, settings: Tuple[Codec, Type]):
        codec, wrap = settings
        name        = f'{cname(codec)}[{cname(wrap)}]'
        base_types  = [wrap] #type: List[type]
        if isinstance(wrap, type) and issubclass(wrap, Enum):
            base_types.extend(enum_types(wrap))
        kwargs = {'wrap': wrap, 'codec': codec, 'base_type': tuple(base_types)}
        return type(name, (cls,), kwargs)
 
    @classmethod
    def encode(cls, ctx: Context, value: Any):
        value = cls.wrap(value)
        return cls.codec.encode(ctx, value.value)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> T:
        return cls.wrap(cls.codec.decode(ctx, raw))
