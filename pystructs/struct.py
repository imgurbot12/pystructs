"""
DataClass-Like Struct Implementation
"""
from typing import Any, Type, Optional, get_origin, get_args
from typing_extensions import Self, Annotated, dataclass_transform

from pyderive import MISSING, BaseField, dataclass, fields, is_dataclass

from .codec import *

#** Variables **#
__all__ = ['field', 'compile', 'Field', 'Struct']

#** Functions **#

def field(*_, **kwargs) -> Any:
    """apply custom field to struct definition"""
    return Field(**kwargs)

def compile(cls=None, *_, **kwargs):
    """compile struct w/ the following dataclass options""" 
    @dataclass_transform(field_specifiers=(Field, field))
    def wrapper(cls):
        return dataclass(cls, field=Field, **kwargs)
    return wrapper(cls) if cls else wrapper

#** Classes **#

@dataclass(slots=True)
class Field(BaseField):
    codec: Optional[Type[Codec]] = None

    def finalize(self):
        """compile codec/annotation"""
        self.anno = deanno(self.codec or self.anno)
        if not isinstance(self.anno, type) or not isinstance(self.anno, Codec):
            raise CodecError(f'field {self.name} invalid anno: {self.anno!r}')

@dataclass_transform(field_specifiers=(Field, field))
class Struct:

    def __new__(cls, *_, **__):
        if not is_dataclass(cls):
            cls = dataclass(cls, field=Field)
        return super().__new__(cls)

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
