"""
Base Codec Definitions
"""
import functools
from abc import abstractmethod
from typing import *
from typing_extensions import Annotated, runtime_checkable, get_args, get_origin

from pyderive import dataclass, field

#** Variables **#
__all__ = [
    'T',
    'cname',
    'deanno',
    'protocol',
    'protomethod',

    'CodecError', 
    'Context', 
    'Codec'
]

#: generic typevar bound to type
T = TypeVar('T', bound=Type)

#: protocol tracker attribute
PROTOCOL_ATTR = '__protocols__'

#** Functions **#

def cname(cls) -> str:
    """retrieve classname from object or type"""
    cls = cls if isinstance(cls, type) else type(cls)
    return cls.__name__.lstrip('_')

def deanno(t: T, validate: Union[Type[T], Tuple[Type[T], ...]]) -> T:
    """remove annotation if present and validate type value"""
    t = t if get_origin(t) is not Annotated else get_args(t)[1]
    if isinstance(t, type) and not isinstance(t, validate):
        raise ValueError(f'{t!r} must be subclass of {validate!r}')
    return t

def is_protocol(cls) -> bool:
    """return true if class if codec protocol object"""
    registry = getattr(cls, PROTOCOL_ATTR, None)
    return registry is not None and cls in registry

@overload
def protocol(cls: T, checkable: bool = True) -> T:
    ...

@overload
def protocol(cls: Optional[T] = None, checkable: bool = True) -> Callable[[T], T]:
    ...

def protocol(cls: Optional[T] = None, checkable: bool = True):
    """
    designate the following codec instance as a protocol

    :param cls: codec object to designate as a protocol
    :return:    registered and runtime-checkable protocol class
    """
    def wrap_protocol(cls):
        if checkable:
            cls = runtime_checkable(cls)
        registry = getattr(cls, PROTOCOL_ATTR, None) or set()
        registry.add(cls)
        setattr(cls, PROTOCOL_ATTR, registry)
        return cls
    return wrap_protocol if cls is None else wrap_protocol(cls)

def protomethod(func: Callable) -> Callable:
    """
    custom classmethod decorator that checks for protocol types

    :param func: method to wrap as protocol classmethod
    :return:     wrapped protocol method
    """
    @classmethod
    @functools.wraps(func)
    def wrapper(cls, *args, **kwargs):
        if is_protocol(cls):
            raise TypeError(f'Protocol {cname(cls)!r} cannot be called directly')
        return func(cls, *args, **kwargs)
    return wrapper

#** Classes **#

class CodecError(Exception):
    """Codec Encoding/Decoding Exception"""
    pass

@dataclass(slots=True)
class Context:
    """Encoding/Decoding Context Tracking"""
    index: int = 0
    index_to_domain: Dict[int, bytes] = field(default_factory=dict)
    domain_to_index: Dict[bytes, int] = field(default_factory=dict)

    def reset(self):
        """reset variables in context to their default state"""
        self.index = 0
        self.index_to_domain.clear()
        self.domain_to_index.clear()

    def slice(self, raw: bytes, length: int) -> bytes:
        """
        parse slice of n-length starting from current context index

        :param raw:    raw bytes to slice from
        :param length: length of slice to retrieve
        :return:       slice from raw bytes
        """
        end  = self.index + length
        data = raw[self.index:end]
        self.index = end
        return data

    def save_domain(self, domain: bytes, index: int):
        """
        save domain to context-manager for domain PTR assignments
        
        :param domain: domain to save in context
        :param index:  index of the domain being saved
        """
        self.index_to_domain[index] = domain
        self.domain_to_index[domain] = index

@runtime_checkable
class Codec(Protocol[T]):
    """Encoding/Decoding Codec Protocol"""
    base_type: ClassVar[tuple]

    @classmethod
    @abstractmethod
    def encode(cls, ctx: Context, value: T) -> bytes:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def decode(cls, ctx: Context, raw: bytes) -> T:
        raise NotImplementedError
