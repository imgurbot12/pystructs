"""
DataClass-Like Struct Implementation
"""

#** Variables **#
__all__ = [
    'Property',
    'InitVar',
    'ClassVar',
    
    'field',
    'struct',
    'make_struct',
    'Struct',
]

#** Imports **#
from .fields import Property, InitVar, ClassVar, field
from .struct import Struct, struct, make_struct
