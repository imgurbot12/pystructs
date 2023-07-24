"""
DataClass-Like Struct Implementation
"""
from typing import Any, Type, Optional, ClassVar
from typing_extensions import Self, dataclass_transform, get_type_hints

from pyderive import MISSING, BaseField, dataclass, fields, gen_slots

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
    if cls in COMPILED:
        return
    COMPILED.add(cls)
    dataclass(cls, field=Field, **kwargs)
    if slots:
        setattr(cls, '__slots__', gen_slots(cls, fields(cls)))

#** Classes **#

@dataclass(slots=True)
class Field(BaseField):
    codec: Optional[Type[Codec]] = None

    def __compile__(self, _):
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
    
    def pack(self) -> bytes:
        """
        pack contents into serialized bytes

        :return: serialized struct contents
        """
        ctx = Context()
        return self.encode(ctx)
    
    @classmethod
    def unpack(cls, raw: bytes) -> Self:
        """
        unpack serialized bytes into struct object

        :param raw: raw bytes to unpack into struct
        :return:    deserialized struct object
        """
        ctx = Context()
        return cls.decode(ctx, raw)

    def encode(self, ctx: Context) -> bytes:
        """
        encode the compiled sequence fields into bytes

        :param ctx: context helper used to encode bytes
        :return:    packed and serialized struct object
        """
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
        """
        decode the given raw-bytes into a compiled sequence
        
        :param ctx: context helper used to decode bytes
        :param raw: raw bytes content to decode
        :return:    decoded struct object
        """
        kwargs = {}
        for f in fields(cls):
            try:
                value = f.anno.decode(ctx, raw)
            except (CodecError, ValueError, TypeError) as e:
                raise ValueError(f'{cname(cls)}.{f.name}: {e}') from None
            if f.init:
                kwargs[f.name] = value
        return cls(**kwargs)
