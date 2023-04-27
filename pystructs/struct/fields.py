"""
Struct Field Implementation
"""
from dataclasses import InitVar, MISSING, dataclass
from dataclasses import field as datafield
from dataclasses import Field as DataField
from typing import *
from typing_extensions import Self

from .. import Codec, Int32

#** Variables **#
__all__ = [
    'MISSING',
    'DataField',

    'field',
    'cname',
    'is_datavar',
    'compile_annotation',
    'Property',
    'Field',
    'Spec',
]

#** Functions **#

def field(*args, **kwargs) -> 'Spec':
    """generate field w/ following specifications"""
    return Spec(*args, **kwargs)

def cname(seq: Union[object, type]) -> str:
    """retrieve class name of object or type"""
    if isinstance(seq, type):
        return seq.__name__
    return seq.__class__.__name__

def is_datavar(anno: type) -> bool:
    """check if datatype is ClassVar or InitVar"""
    origin = get_origin(anno)
    return origin in (ClassVar, InitVar)

def not_missing(*args) -> Any:
    """return first arguent that is not missing"""
    assert len(args) > 0, 'no args provided'
    for arg in args:
        if arg is not MISSING:
            return arg
    return MISSING

def compile_annotation(name: str, anno: type, level: int = 1):
    """compile given annotation into a valid Codec or tupported type"""
    # skip processing if already a codec or supported type
    if isinstance(anno, Codec):
        return anno
    # convert common types to defaults
    if anno == int:
        return Int32
    # convert property
    if isinstance(anno, Property):
        anno.hint = compile_annotation(name, anno.hint, level+1)
        return anno
    # raise error on unsupported type
    raise ValueError(f'invalid annotatation: {name!r}: {anno}')

#** Classes **#

@dataclass
class Property:
    hint:    type
    init:    ClassVar[bool] = False
    default: ClassVar[Any]  = MISSING

    def __class_getitem__(cls, hint: type) -> Self:
        return cls(hint)

@dataclass
class Field:
    name:     str
    type:     Type[Codec]
    init:     bool = True
    default:  Any  = None
    dataattr: bool = True

@dataclass
class Spec:
    default:         Any                         = MISSING
    default_factory: Optional[Callable[[], Any]] = None
    init:            Optional[bool]              = None
    repr:            bool                        = True
    hash:            Optional[bool]              = None
    compare:         bool                        = True
    kwargs:          dict                        = datafield(default_factory=dict)

    def compile(self, name: str, anno: Type[Codec]) -> Tuple[Field, DataField]:
        """compile field-spec into official field"""
        init = anno.init if self.init is None else anno.init
        return (Field(name, anno, init), datafield(
            default=not_missing(self.default, anno.default),
            default_factory=self.default_factory or MISSING, #type: ignore
            init=init,
            repr=self.repr,
            hash=self.hash,
            compare=self.compare,
            **self.kwargs,
        ))
