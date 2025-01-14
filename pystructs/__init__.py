"""
Python Dataclass Struct Library
"""
from typing import Any, Optional, Sequence, Tuple, TypeVar, Union
from typing_extensions import _AnnotatedAlias

#** Variables **#
__all__ = [
    'pack',
    'unpack',

    'deanno',
    'Context',
    'Field',

    'IPv4Field',
    'IPv6Field',
    'MACField',
    'DomainField',
    'IPv4',
    'IPv6',
    'MACAddr',
    'Domain',

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

    'field',
    'Struct',
    'StructField',
]

T = TypeVar('T')

#** Functions **#

def pack(fields: Sequence[Any],
    *values: Any, ctx: Optional['Context'] = None) -> bytes:
    """
    pack struct fields into encoded bytes

    :param fields: list of fields used to serialize values
    :param values: list of values to match encoding fields
    :param ctx:    serialization tracker for packaging multiple objects
    :return:       packed bytes
    """
    if len(values) != len(fields):
        raise OverflowError(f'{len(fields)} fields vs {len(values)} values.')
    ctx     = ctx or Context()
    content = bytearray()
    for n, (field, value) in enumerate(zip(fields, values), 0):
        wrapper, packer = deanno(field, f'field({n}) ')
        try:
            value    = wrapper(value)
            content += packer._pack(value, ctx)
        except (ValueError, OverflowError) as e:
            name = packer.__class__.__name__
            raise e.__class__(f'field({n})->{name}->{e}') from None
    return bytes(content)

def unpack(fields: Sequence[Union['Field[T]', _AnnotatedAlias]],
    raw: bytes, ctx: Optional['Context'] = None) -> Tuple[T]:
    """
    unpack struct fields from encoded bytes

    :param fields: list of fields used to deserialize raw bytes
    :param raw:    raw encoded bytes to unpack
    :return:       unpacked struct field values
    """
    ctx     = ctx or Context()
    content = []
    for n, field in enumerate(fields, 0):
        wrapper, unpacker = deanno(field, f'field({n}) ')
        try:
            value = unpacker._unpack(raw, ctx)
            value = wrapper(value)
            content.append(value)
        except (ValueError, OverflowError) as e:
            name = unpacker.__class__.__name__
            raise e.__class__(f'field({n})->{name}->{e}') from None
    return tuple(content)

#** Imports **#
from .abc import *
from .net import *
from .std import *
from .struct import *
