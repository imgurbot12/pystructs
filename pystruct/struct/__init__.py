"""
DataClass-Like Struct Implementation
"""

#** Variables **#
__all__ = [
    'Property',
    'InitVar',
    'ClassVar',
    
    'struct',
    'make_struct',
    'Struct',
]

#** Imports **#
from .fields import Property, InitVar, ClassVar
from .struct import struct, make_struct, Struct
