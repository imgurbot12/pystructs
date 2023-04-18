"""
Struct Construction Implementation
"""
import dataclasses
from collections import OrderedDict
from typing import Optional, Dict, Type, Generic, TypeVar
from typing_extensions import Self, dataclass_transform

from .fields import *
from ..base import Context, Codec

#** Variables **#
__all__ = ['struct', 'make_struct', 'Struct']

#: generic typevar to help with type definitions
T = TypeVar('T')

#: codec-fields field on class objects
FIELDS = '__encoded__'

#: annotations field on class objects
ANNOTATIONS = '__annotations__'

#: placeholder type instead of None to allow for None as a default
MISSING = type('MISSING', (), {})

#** Functions **#

def struct(cls: Optional[Type[T]] = None, **kwargs) -> Type['Struct[T]']:
    """
    generate sequence object w/ codec-field and build dataclass-like object

    :param cls:    class object being converted into a sequence
    :param kwargs: kwargs to pass to dataclass generation
    :return:       sequence class object type
    """
    @dataclass_transform()
    def wrap(cls: Type[T]) -> Type[Struct[T]]:
        return make_struct(cls, **kwargs)
    if cls is None:
        return wrap #type: ignore
    return wrap(cls)

def make_struct(cls: Type[T], **kwargs) -> Type['Struct[T]']:
    """
    generate a sequence object w/ codec fields and build dataclass-like object

    :param cls:    class object being converted into a sequence
    :param kwargs: kwargs to pass to dataclass generation
    :return:       sequence class object type
    """
    values      = {}
    fields      = getattr(cls, FIELDS, OrderedDict())
    annotations = getattr(cls, ANNOTATIONS, {})
    for name in list(annotations.keys()):
        # skip processing if annotation is a InitVar or ClassVar
        anno = annotations[name]
        if is_datavar(anno):
            continue
        # retrieve default value
        value = getattr(cls, name, MISSING)
        if hasattr(cls, name):
            delattr(cls, name)
        # parse attribute into field if not already
        anno  = compile_annotation(name, anno)
        field = Field(name, anno)
        fields[name] = field
        # process property types
        if isinstance(anno, Property):
            # ensure annotation is deleted for dataclass
            del annotations[name]
            field.type     = anno.hint
            field.dataattr = False
            # validate property function value
            if not isinstance(value, property):
                if not callable(value):
                    raise ValueError(f'property: {name} must be a function')
                value = property(value)
            values[name] = value
            continue
        # process standard codec-types
        if isinstance(anno, Codec):
            annotations[name] = anno.base_type
            values[name]      = value
    # generate bases for new sequence dataclass
    bases = list(cls.__mro__)
    if Struct not in bases:
        bases.insert(1, Struct)
    # generate new unique object w/ fields parsed from original
    dataclassfunc = dataclasses.dataclass(**kwargs)
    return dataclassfunc(type(cname(cls), tuple(bases), { #type: ignore
        FIELDS:      fields,
        ANNOTATIONS: annotations,
        **values
    }))

#** Classes **#

class Struct(Generic[T]):
    """
    BaseClass for defining Struct behavior
    """
    base_type:   T
    __encoded__: Dict[str, Field]
   
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def __getattr__(self, name: str):
        raise AttributeError(f'{cname(self)} has no attribute {name}')

    def encode(self, ctx: Context) -> bytes:
        """encode the compiled sequence fields into bytes"""
        encoded = bytearray()
        for name, field in self.__encoded__.items():
            # retrieve value for the given attribute
            value = getattr(self, name, MISSING)
            if value is MISSING:
                raise ValueError(f'{cname(self)} missing attr {name!r}')
            # encode it according it's associated codec
            encoded += field.type.encode(ctx, value)
        return bytes(encoded)

    @classmethod
    def decode(cls, ctx: Context, raw: bytes) -> Self:
        """decode the given raw-bytes into a compiled sequence"""
        kwargs = {}
        for name, field in cls.__encoded__.items():
            kwargs[name] = field.type.decode(ctx, raw)
        return cls(**kwargs)
