"""
DataClass-Like Struct Implementation
"""
from typing import Any, Type, Optional, ClassVar
from typing_extensions import Self, dataclass_transform, get_type_hints

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

def compile(cls, slots: bool = True, **kwargs):
    """compile uncompiled structs"""
    global COMPILED
    name   = f'{cls.__module__}.{cls.__name__}'
    hints  = tuple(get_type_hints(cls).items())
    tohash = (name, hints)
    if tohash in COMPILED:
        return
    COMPILED.add(tohash)
    newcls = dataclass(cls, field=Field, slots=slots, **kwargs)
    setattr(cls, '__slots__', getattr(newcls, '__slots__'))

#** Classes **#

@dataclass(slots=True)
class Field(BaseField):
    codec: Optional[Type[Codec]] = None

    def finalize(self):
        """compile codec/annotation"""
        self.anno = deanno(self.codec or self.anno, (Codec, Struct))

@protocol(checkable=False)
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
            try:
                encoded += f.anno.encode(ctx, value)
            except (CodecError, ValueError, TypeError) as e:
                raise ValueError(f'{cname(self)}.{f.name}: {e}') from None
        return bytes(encoded)

    @protomethod
    def decode(cls, ctx: Context, raw: bytes) -> Self:
        """decode the given raw-bytes into a compiled sequence"""
        kwargs = {}
        for f in fields(cls):
            try:
                value = f.anno.decode(ctx, raw)
            except (CodecError, ValueError, TypeError) as e:
                raise ValueError(f'{cname(cls)}.{f.name}: {e}') from None
            if f.init:
                kwargs[f.name] = value
        return cls(**kwargs)
