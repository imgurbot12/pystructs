"""
Integer Codec Implementations
"""
from abc import abstractmethod
from enum import Enum
from typing import Protocol, Union, ClassVar
from typing_extensions import runtime_checkable

from .codec import *

#** Variables **#
__all__ = [
    'IntFmt',
    'IntLike',
    'Integer',
    'Signed',
    'Unsigned',

    'I8',
    'I16',
    'I24',
    'I32',
    'I48',
    'I64',
    'I128',
    'U8',
    'U16',
    'U24',
    'U48',
    'U64',
    'U128',
]

#** Classes **#

class IntFmt(Enum):
    BIG_ENDIAN    = 'big'
    LITTLE_ENDIAN = 'little'

@runtime_checkable
class IntLike(Protocol):

    @abstractmethod
    def __int__(self) -> int:
        raise NotImplementedError

class Integer(Codec[IntLike], Protocol):
    max:       ClassVar[int]
    min:       ClassVar[int]
    size:      ClassVar[int]
    fmt:       ClassVar[IntFmt] = IntFmt.BIG_ENDIAN
    sign:      ClassVar[bool]   = False
    base_type: ClassVar[tuple]  = (IntLike, )

    def __class_getitem__(cls, fmt: Union[str, IntFmt]):
        return type(cls.__name__, (cls, ), {'fmt': fmt})

    @classmethod
    def encode(cls, ctx: Context, value: IntLike):
        """encode integer using settings encoded into the type"""
        value = int(value)
        if value < cls.min:
            raise CodecError(f'{cname(cls)} {value!r} too small')
        if value > cls.max:
            raise CodecError(f'{cname(cls)} {value!r} too large')
        ctx.index += cls.size
        return value.to_bytes(cls.size, cls.fmt.value, signed=cls.sign)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> int:
        """decode integer from bytes using int-type settings"""
        data = ctx.slice(raw, cls.size)
        if len(data) != cls.size:
            raise CodecError(f'datalen={len(data)} != {cls.__name__}')
        value = int.from_bytes(data, cls.fmt.value, signed=cls.sign)
        return value

class Signed(Integer, Protocol):
    sign = True

class I8(Signed):
    min  = - int(2**8 / 2)
    max  = int(2**8 / 2) - 1 
    size = 1

class I16(Signed):
    min  = - int(2**16 / 2)
    max  = int(2**16 / 2) - 1
    size = 2

class I24(Signed):
    min  = - int(2**24 / 2)
    max  = int(2**24 / 2) - 1
    size = 3

class I32(Signed):
    min  = - int(2**32 / 2)
    max  = int(2**32 / 2) - 1
    size = 4

class I48(Signed):
    min  = - int(2**48 / 2)
    max  = int(2**48 / 2) - 1
    size = 6

class I64(Signed):
    min  = - int(2**64 / 2)
    max  = int(2**64 / 2) - 1
    size = 8

class I128(Signed):
    min  = - int(2**128 / 2)
    max  = int(2**128 / 2) - 1
    size = 16

class Unsigned(Integer, Protocol):
    sign = False

class U8(Unsigned):
    min  = 0
    max  = 2**8
    size = 1

class U16(Unsigned):
    min  = 0
    max  = 2**16
    size = 2

class U24(Unsigned):
    min  = 0
    max  = 2**24
    size = 3

class U32(Unsigned):
    min  = 0
    max  = 2**32
    size = 4

class U48(Unsigned):
    min  = 0
    max  = 2**48
    size = 6

class U64(Unsigned):
    min  = 0
    max  = 2**64
    size = 8

class U128(Unsigned):
    min  = 0
    max  = 2**128
    size = 16
