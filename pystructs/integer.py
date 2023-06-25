"""
Integer Codec Implementations
"""
from enum import Enum
from typing import Protocol, SupportsInt, Union, ClassVar, TypeVar
from typing_extensions import Annotated

from .codec import *

#** Variables **#
__all__ = [
    'I',
    'IntFmt',
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
    'U32',
    'U48',
    'U64',
    'U128',
]

#: typehint bound to integer types
I = TypeVar('I', bound=Union[int, 'Integer'], contravariant=True)

#** Classes **#

class IntFmt(Enum):
    BIG_ENDIAN    = 'big'
    LITTLE_ENDIAN = 'little'

@protocol
class Integer(Codec[SupportsInt], Protocol):
    max:       ClassVar[int]
    min:       ClassVar[int]
    size:      ClassVar[int]
    fmt:       ClassVar[IntFmt] = IntFmt.BIG_ENDIAN
    sign:      ClassVar[bool]   = False
    base_type: ClassVar[tuple]  = (SupportsInt, )

    def __class_getitem__(cls, fmt: Union[str, IntFmt]):
        """validate and generate integer subclass"""
        assert isinstance(fmt, (str, IntFmt)), f'invalid integer format: {fmt}'
        fmt = IntFmt[fmt] if isinstance(fmt, str) else fmt
        return type(cls.__name__, (cls, ), {'fmt': fmt})

    @protomethod
    def encode(cls, ctx: Context, value: SupportsInt):
        """encode integer using settings encoded into the type"""
        value = int(value)
        if value < cls.min:
            raise CodecError(f'{cname(cls)} {value!r} too small')
        if value > cls.max:
            raise CodecError(f'{cname(cls)} {value!r} too large')
        ctx.index += cls.size
        return value.to_bytes(cls.size, cls.fmt.value, signed=cls.sign)

    @protomethod
    def decode(cls, ctx: Context, raw: bytes) -> int:
        """decode integer from bytes using int-type settings"""
        data = ctx.slice(raw, cls.size)
        if len(data) != cls.size:
            raise CodecError(f'datalen={len(data)} != {cname(cls)}')
        value = int.from_bytes(data, cls.fmt.value, signed=cls.sign)
        return value

@protocol
class Signed(Integer, Protocol):
    sign: ClassVar[bool] = True

class _I8(Signed):
    min  = - int(2**8 / 2)
    max  = int(2**8 / 2) - 1 
    size = 1

class _I16(Signed):
    min  = - int(2**16 / 2)
    max  = int(2**16 / 2) - 1
    size = 2

class _I24(Signed):
    min  = - int(2**24 / 2)
    max  = int(2**24 / 2) - 1
    size = 3

class _I32(Signed):
    min  = - int(2**32 / 2)
    max  = int(2**32 / 2) - 1
    size = 4

class _I48(Signed):
    min  = - int(2**48 / 2)
    max  = int(2**48 / 2) - 1
    size = 6

class _I64(Signed):
    min  = - int(2**64 / 2)
    max  = int(2**64 / 2) - 1
    size = 8

class _I128(Signed):
    min  = - int(2**128 / 2)
    max  = int(2**128 / 2) - 1
    size = 16

@protocol
class Unsigned(Integer, Protocol):
    sign: ClassVar[bool] = False

class _U8(Unsigned):
    min  = 0
    max  = 2**8
    size = 1

class _U16(Unsigned):
    min  = 0
    max  = 2**16
    size = 2

class _U24(Unsigned):
    min  = 0
    max  = 2**24
    size = 3

class _U32(Unsigned):
    min  = 0
    max  = 2**32
    size = 4

class _U48(Unsigned):
    min  = 0
    max  = 2**48
    size = 6

class _U64(Unsigned):
    min  = 0
    max  = 2**64
    size = 8

class _U128(Unsigned):
    min  = 0
    max  = 2**128
    size = 16

I8   = Annotated[int, _I8]
I16  = Annotated[int, _I16]
I24  = Annotated[int, _I24]
I32  = Annotated[int, _I32]
I48  = Annotated[int, _I48]
I64  = Annotated[int, _I64]
I128 = Annotated[int, _I128]

U8   = Annotated[int, _U8]
U16  = Annotated[int, _U16]
U24  = Annotated[int, _U24]
U32  = Annotated[int, _U32]
U48  = Annotated[int, _U48]
U64  = Annotated[int, _U64]
U128 = Annotated[int, _U128]
