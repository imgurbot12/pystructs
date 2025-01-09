"""
Serializer Struct Object Definition
"""
from typing import Any, Optional, Type, cast
from typing_extensions import Self, dataclass_transform

from pyderive import BaseField, dataclass, fields, gen_slots

from .abc import Context, Field, Wrapper, deanno

#** Variables **#
__all__ = ['Struct', 'StructField', 'field']

#: tracker of already compiled struct instances
COMPILED = set()

#** Functions **#

def field(**kwargs) -> Any:
    """
    define serialization field metadata

    :param kwargs: arguments to pass to field definition
    :return:       struct field definition
    """
    return StructField(**kwargs)

def _compile(cls, slots: bool = True, **kwargs):
    """compile uncompiled structs"""
    global COMPILED
    if cls in COMPILED:
        return
    COMPILED.add(cls)
    dataclass(cls, field=StructField, **kwargs)
    if slots:
        setattr(cls, '__slots__', gen_slots(cls, fields(cls)))

#** Classes **#

@dataclass
class StructField(BaseField):
    field: Optional[Field] = None
    wrap:  Wrapper         = lambda x: x

    def __compile__(self, cls: Type):
        """ensure serialization field/wrapper is present"""
        if self.field is None:
            wrap, field = deanno(self.anno, f'{cls.__name__}.{self.name} ')
            self.field = field
            self.wrap  = wrap

@dataclass_transform(field_specifiers=(StructField, field))
class Struct(Field):
    """
    Collection of Serialization Fields to Pack/Unpack
    """

    def __init_subclass__(cls, **kwargs):
        _compile(cls, **kwargs)

    @classmethod
    def _pack(cls, value: Self, ctx: Context) -> bytes: #type: ignore
        raw = bytearray()
        for f in fields(cls):
            field = cast(StructField, f)
            wrap  = cast(Wrapper, field.wrap)
            try:
                val  = wrap(getattr(value, f.name))
                raw += cast(Field, field.field)._pack(val, ctx)
            except (ValueError, OverflowError) as e:
                raise e.__class__(f'{cls.__name__}.{f.name}->{e}') from None
        return bytes(raw)

    @classmethod
    def _unpack(cls, raw: bytes, ctx: Context) -> Self: #type: ignore
        kwargs = {}
        for f in fields(cls):
            field = cast(StructField, f)
            wrap  = cast(Wrapper, field.wrap)
            try:
                value = cast(Field, field.field)._unpack(raw, ctx)
                kwargs[f.name] = wrap(value)
            except (ValueError, OverflowError) as e:
                raise e.__class__(f'{cls.__name__}.{f.name}->{e}') from None
        return cls(**kwargs)

    def pack(self, ctx: Optional[Context] = None) -> bytes:
        """
        pack struct fields into encoded bytes

        :param ctx: serialization tracker for packaging multiple objects
        :return:    packed bytes
        """
        ctx = ctx or Context()
        return self._pack(self, ctx)

    @classmethod
    def unpack(cls, raw: bytes, ctx: Optional[Context] = None) -> Self:
        """
        unpack struct fields from encoded bytes

        :param raw: raw encoded bytes to unpack
        :param ctx: deserialization tracker for packaging multiple objects
        :return:    unpacked struct object
        """
        ctx = ctx or Context()
        return cls._unpack(raw, ctx)
