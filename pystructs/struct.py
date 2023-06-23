"""
DataClass-Like Struct Implementation
"""
from typing import Any, Type, Optional, ClassVar
from typing_extensions import Self, dataclass_transform

from pyderive import MISSING, BaseField, dataclass, fields

from .codec import *

#** Variables **#
__all__ = ['field', 'Field', 'Struct']

#: tracker of already compiled struct instances
COMPILED = set()

#** Functions **#

def field(*_, **kwargs) -> Any:
    """apply custom field to struct definition"""
    return Field(**kwargs)

def compile(cls, **kwargs):
    """compile uncompiled structs"""
    global COMPILED
    name = f'{cls.__module__}.{cls.__name__}'
    if name in COMPILED:
        return
    COMPILED.add(name)
    newcls = dataclass(cls, field=Field, slots=True, **kwargs)
    setattr(newcls, '__slots__', getattr(newcls, '__slots__'))

#** Classes **#

@dataclass(slots=True)
class Field(BaseField):
    codec: Optional[Type[Codec]] = None

    def finalize(self):
        """compile codec/annotation"""
        self.anno = deanno(self.codec or self.anno, (Codec, Struct))

@dataclass_transform(field_specifiers=(Field, field))
class Struct(Codec):
    base_type: ClassVar[tuple] = ()
 
    def __init__(self):
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        compile(cls, **kwargs) 
        cls.base_type = (cls, )

    def encode(self, ctx: Context) -> bytes:
        """encode the compiled sequence fields into bytes"""
        encoded = bytearray()
        for f in fields(self):
            value = getattr(self, f.name, f.default or MISSING)
            if value is MISSING:
                raise ValueError(f'{cname(self)} missing attr {f.name!r}')
            if not isinstance(value, f.anno.base_type):
                raise ValueError(f'{cname(self)}.{f.name} invalid value: {value!r}')
            encoded += f.anno.encode(ctx, value)
        return bytes(encoded)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> Self:
        """decode the given raw-bytes into a compiled sequence"""
        kwargs = {}
        for f in fields(cls):
            value = f.anno.decode(ctx, raw)
            if f.init:
                kwargs[f.name] = value
        return cls(**kwargs)
