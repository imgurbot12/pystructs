"""
Python Struct Utilities Library
"""
from .list import *
from .base import *
from .codec import *

#** Variables **#
__all__ = [
    'Codec',
    'Context',
    'Const',
    'Int',
    'Int8',
    'Int16',
    'Int32',
    'Int48',
    'Int64',
    'IpAddr',
    'Ipv4',
    'Ipv6',
    'MacAddr',
    'SizedBytes',
    'StaticBytes',
    'GreedyBytes',
    'Domain',
    'SizedList',
    'StaticList',
    'GreedyList',

    'field',
    'fields',
    'struct',
    'make_struct',
    'Struct',
    'Property',
]

Int8  = Int[8]
Int16 = Int[16]
Int32 = Int[32]
Int48 = Int[48]
Int64 = Int[64]

Ipv4 = IpAddr['ipv4']
Ipv6 = IpAddr['ipv6']

#** Imports **#
from .struct import *
