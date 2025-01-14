"""
Standard Serializer Type Defintions
"""
from typing import Any, List, Literal, Tuple, Union
from typing_extensions import Annotated, _AnnotatedAlias

from pyderive import dataclass

from .abc import T, Context, Field, Wrapper, deanno

#** Variables **#
__all__ = [
    'deanno_int',

    'IntHint',
    'IntFmt',
    'IntField',

    'HintedBytes',
    'StaticBytes',
    'GreedyBytes',

    'HintedList',
    'StaticList',
    'GreedyList',

    'Const',

    'I8',
    'I16',
    'I32',
    'I48',
    'I64',
    'I128',
    'U8',
    'U16',
    'U32',
    'U48',
    'U64',
    'U128',
]

IntHint = Union['IntField', _AnnotatedAlias]

IntFmt  = Literal['big', 'little']
IntSize = Literal[1, 2, 4, 6, 8, 16, 32]

#** Functions **#

def deanno_int(anno: Any, prefix: str = '') -> Tuple[Wrapper, 'IntField']:
    """
    retrieve int-field definition from annotated type (if required)

    :param anno:   int-field annotation value
    :param prefix: prefix to include on error
    :return:       (field value wrappper, field object definition)
    """
    wrapper, field = deanno(anno, prefix)
    if not isinstance(field, IntField):
        raise TypeError(f'{prefix}invalid integer annotation: {anno!r}')
    return wrapper, field

#** Classes **#

@dataclass(slots=True)
class IntField(Field[int]):
    """
    Generalized Integer Serializer Definition
    """
    size:   IntSize = 1
    format: IntFmt  = 'big'
    signed: bool    = True

    def _pack(self, value: int, ctx: Context) -> bytes:
        packed = value.to_bytes(self.size, self.format, signed=self.signed)
        ctx.track_bytes(packed)
        return packed

    def _unpack(self, raw: bytes, ctx: Context) -> int:
        val = ctx.slice(raw, self.size)
        if len(val) != self.size:
            raise ValueError(f'too little data to unpack integer({self.size})')
        return int.from_bytes(val, self.format, signed=self.signed)

class HintedBytes(Field[bytes]):
    """
    Arbitrary Bytes Serializer with Prefixed Sizehint
    """
    __slots__ = ('hint', )

    def __init__(self, hint: IntHint):
        self.hint: IntField = deanno_int(hint, 'HintedBytes ')[1]

    def __repr__(self) -> str:
        return f'HintedBytes(hint={self.hint!r})'

    def _pack(self, value: bytes, ctx: Context) -> bytes:
        hint = self.hint._pack(len(value), ctx)
        return hint + ctx.track_bytes(value)

    def _unpack(self, raw: bytes, ctx: Context) -> bytes:
        size = self.hint._unpack(raw, ctx)
        return ctx.slice(raw, size)

@dataclass(slots=True)
class StaticBytes(Field[bytes]):
    """
    Arbitary Bytes Serializer of Fixed Static Bytesize
    """
    size: int

    def _pack(self, value: bytes, ctx: Context) -> bytes:
        if len(value) > self.size:
            raise OverflowError(f'length of bytes greater than {self.size}')
        data = value.ljust(self.size, b'\x00')
        return ctx.track_bytes(data)

    def _unpack(self, raw: bytes, ctx: Context) -> bytes:
        value = ctx.slice(raw, self.size)
        if len(value) != self.size:
            raise ValueError(f'too little data to unpack slice({self.size})')
        return value.rstrip(b'\x00')

class GreedyBytes(Field[bytes]):
    """
    Arbitrary Bytes Serializer of Unlimited Size
    """

    def _pack(self, value: bytes, ctx: Context) -> bytes:
        return ctx.track_bytes(value)

    def _unpack(self, raw: bytes, ctx: Context) -> bytes:
        return ctx.slice(raw, len(raw))

class HintedList(Field[List[T]]):
    """
    Object List Serializer with Prefixed Sizehint
    """
    __slots__ = ('hint', 'item', 'wrap')

    def __init__(self, hint: IntHint, item: Union[Field[T], _AnnotatedAlias]):
        wrap, item = deanno(item, 'HintedList ')
        self.hint: IntField = deanno_int(hint, 'HintedList ')[1]
        self.item: Field[T] = item
        self.wrap: Wrapper  = wrap

    def __repr__(self) -> str:
        return f'HintedList(hint={self.hint!r}, item={self.item!r})'

    def _pack(self, value: List[T], ctx: Context) -> bytes:
        data  = bytearray()
        data += self.hint._pack(len(value), ctx)
        for item in value:
            data += self.item._pack(item, ctx)
        return bytes(data)

    def _unpack(self, raw: bytes, ctx: Context) -> List[T]:
        size  = self.hint._unpack(raw, ctx)
        return [self.wrap(self.item._unpack(raw, ctx)) for _ in range(size)]

class StaticList(Field[List[T]]):
    """
    Object List Serializer of Fixed Static Bytesize
    """
    __slots__ = ('size', 'item', 'wrap')

    def __init__(self, size: int, item: Union[Field[T], _AnnotatedAlias]):
        wrapper, item = deanno(item, 'StaticList ')
        self.size: int      = size
        self.item: Field[T] = item
        self.wrap: Wrapper  = wrapper

    def __repr__(self) -> str:
        return f'StaticList(size={self.size}, item={self.item!r})'

    def _pack(self, value: List[T], ctx: Context) -> bytes:
        if len(value) > self.size:
            raise OverflowError(f'length of list greater than {self.size}')
        return b''.join(self.item._pack(item, ctx) for item in value)

    def _unpack(self, raw: bytes, ctx: Context) -> List[T]:
        return [self.wrap(self.item._unpack(raw, ctx)) for _ in range(self.size)]

class GreedyList(Field[List[T]]):
    """
    Object List Serializer of Unlimited Size
    """
    __slots__ = ('item', 'wrap')

    def __init__(self, item: Union[Field[T], _AnnotatedAlias]):
        wrapper, item = deanno(item, 'GreedyList ')
        self.item: Field[T] = item
        self.wrap: Wrapper  = wrapper

    def __repr__(self) -> str:
        return f'GreedyList(item={self.item!r})'

    def _pack(self, value: List[T], ctx: Context) -> bytes:
        return b''.join(self.item._pack(item, ctx) for item in value)

    def _unpack(self, raw: bytes, ctx: Context) -> List[T]:
        items = []
        while ctx.index < len(raw):
            item = self.wrap(self.item._unpack(raw, ctx))
            items.append(item)
        return items

class Const(Field[bytes]):
    """
    Constant Static Bytes Assignment Field Validator
    """
    __slots__ = ('const', )

    def __init__(self, const: bytes):
        self.const = const

    def __repr__(self):
        return f'Const({self.const!r})'

    def _pack(self, value: bytes, ctx: Context) -> bytes:
        if value != self.const:
            raise ValueError(f'{value!r} does not match const {self.const!r}')
        return ctx.track_bytes(value)

    def _unpack(self, raw: bytes, ctx: Context) -> bytes:
        value = ctx.slice(raw, len(self.const))
        if value != self.const:
            raise ValueError(f'{value!r} does not match const {self.const!r}')
        return value

#** Annotations **#

I8   = Annotated[int, IntField(1, signed=True)]
I16  = Annotated[int, IntField(2, signed=True)]
I32  = Annotated[int, IntField(4, signed=True)]
I48  = Annotated[int, IntField(6, signed=True)]
I64  = Annotated[int, IntField(8, signed=True)]
I128 = Annotated[int, IntField(16, signed=True)]

U8   = Annotated[int, IntField(1, signed=False)]
U16  = Annotated[int, IntField(2, signed=False)]
U32  = Annotated[int, IntField(4, signed=False)]
U48  = Annotated[int, IntField(6, signed=False)]
U64  = Annotated[int, IntField(8, signed=False)]
U128 = Annotated[int, IntField(16, signed=False)]
