"""
Python Struct Utilities Library
"""
from typing import Any, Sequence, Tuple, overload

#** Variables **#
__all__ = [
    'pack',
    'unpack',
    'encode',
    'decode',

    'field',
    'Field',
    'Struct',

    'Context',
    'Codec',
    'CodecError',

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
    
    'SizedBytes', 
    'StaticBytes', 
    'GreedyBytes',
    
    'SizedList', 
    'StaticList', 
    'GreedyList',
    
    'IpType',
    'Ipv4Type',
    'Ipv6Type',
    'IpAddress',
    'IPv4',
    'IPv6',
    'MacAddr',
    'Domain',

    'Const',
    'Wrap',
]

#** Functions **#

def pack(codecs: Any, *values: Any) -> bytes:
    """
    Encode the following value into bytes

    :param codecs: codecs used to encode value
    :param values: value to encode in bytes using codec
    :return:       encoded bytes
    """
    ctx = Context()
    return encode(ctx, codecs, *values)

def unpack(codecs: Any, raw: bytes) -> Tuple[Any, ...]:
    """
    Decode the following bytes with specified Codec

    :param raw:    raw bytes to decode
    :param codecs: codec implementations used to decode value
    :return:       decoded bytes
    """
    ctx = Context()
    return decode(ctx, codecs, raw)

def encode(ctx: 'Context', codecs: Sequence[Any], *values: Any) -> bytes:
    """
    Encode the following value into bytes w/ Context

    :param ctx:    context object used to encode value
    :param codecs: codecs used to encode value
    :param values: values to encode in bytes using codec
    :return:       encoded bytes
    """
    codecs = (codecs, ) if not isinstance(codecs, Sequence) else codecs
    if len(values) < len(codecs):
        raise ValueError(f'Too few values. {len(codecs)} Specified.')
    if len(values) > len(codecs):
        raise ValueError(f'Too many values. {len(codecs)} Specified.')
    content = bytearray()
    for value, codec in zip(values, codecs):
        codec    = deanno(codec, Codec)
        content += codec.encode(ctx, value)
    return bytes(content)

def decode(ctx: 'Context', codecs: Sequence[Any], raw: bytes) -> Tuple[Any, ...]:
    """
    Decode the following bytes with the specified Codec w/ Context

    :param ctx:    context object used to decode value
    :param codecs: codec implementations used to decode value
    :param raw:    raw bytes to decode
    :return:       decoded bytes
    """
    codecs  = (codecs, ) if not isinstance(codecs, Sequence) else codecs
    content = []
    for codec in codecs:
        codec = deanno(codec, Codec)
        value = codec.decode(ctx, raw)
        content.append(value)
    return tuple(content)

#** Imports **#
from .struct import *
from .codec import *
from .integer import *
from .bytestr import *
from .lists import *
from .net import *
from .helpers import *
