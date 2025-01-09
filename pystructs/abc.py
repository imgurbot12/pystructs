"""
Dataclass Struct Definition Components and Utilities
"""
from abc import abstractmethod
from typing import Any, Dict, Protocol, TypeVar
from typing_extensions import (
    Annotated, get_args, get_origin, runtime_checkable)

from pyderive import dataclass, field

#** Variable **#
__all__ = ['Context', 'Field', 'deanno']

T = TypeVar('T')

#** Functions **#

def deanno(anno: Any, prefix: str = '') -> 'Field':
    """
    retrieve field definition from annotated type (if required)

    :param anno:   field annotation value
    :param prefix: prefix to include on error
    :return:       field object definition
    """
    if isinstance(anno, Field):
        return anno
    origin = get_origin(anno)
    if origin is Annotated:
        args   = get_args(anno)
        fields = [f for f in args if isinstance(f, Field)]
        if fields:
            return fields[0]
    raise TypeError(f'{prefix}invalid field annotation: {anno!r}')

#** Classes **#

@dataclass(slots=True)
class Context:
    """
    Encoding/Decoding Context Tracking
    """
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
        data = raw[self.index:self.index + length]
        self.index += len(data)
        return data

    def track_bytes(self, data: bytes) -> bytes:
        """
        track additional length of bytes within context

        :param data: extra bytes appended to final message
        """
        self.index += len(data)
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
class Field(Protocol[T]):
    """
    Abstract Serialization Object Definition
    """

    @abstractmethod
    def _pack(self, value: T, ctx: Context) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def _unpack(self, raw: bytes, ctx: Context) -> T:
        raise NotImplementedError
