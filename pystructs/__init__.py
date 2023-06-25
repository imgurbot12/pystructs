"""
Python Struct Utilities Library
"""
from typing import Any

#** Variables **#
__all__ = [
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

def encode(ctx: 'Context', value: Any, codec: Any) -> bytes:
    """
    Encode the following value into bytes

    :param value: value to encode in bytes using codec
    :param codec: codec used to encode value
    :return:      encoded bytes
    """
    codec = deanno(codec, Codec)
    return codec.encode(ctx, value)

def decode(ctx: 'Context', raw: bytes, codec: Any) -> Any:
    """
    Decode the following bytes with the specified Codec

    :param raw:   raw bytes to decode
    :param codec: codec implementation used to decode value
    :return:      decoded bytes
    """
    codec = deanno(codec, Codec)
    return codec.decode(ctx, raw)

#** Imports **#
from .struct import *
from .codec import *
from .integer import *
from .bytestr import *
from .lists import *
from .net import *
from .helpers import *
