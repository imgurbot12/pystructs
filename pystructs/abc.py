"""
Dataclass Struct Definition Components and Utilities
"""
from abc import abstractmethod
from typing import Any, Callable, Dict, Protocol, Tuple, TypeVar
from typing_extensions import (
    Annotated, _AnnotatedAlias, get_args, get_origin, runtime_checkable)

from pyderive import dataclass, field

#** Variable **#
__all__ = ['Context', 'Field', 'deanno']

T = TypeVar('T')

Wrapper = Callable[[Any], Any]

#** Functions **#

def deanno(anno: Any, prefix: str = '') -> Tuple[Wrapper, 'Field']:
    """
    retrieve field definition from annotated type (if required)

    :param anno:   field annotation value
    :param prefix: prefix to include on error
    :return:       (field value wrapper, field object definition)
    """
    annos = [anno]
    wrap  = lambda x: x
    while annos:
        sub_anno = annos.pop(0)
        if isinstance(sub_anno, Field):
            return (wrap, sub_anno)
        origin = get_origin(sub_anno)
        if origin is Annotated:
            args   = get_args(sub_anno)
            fields = [f for f in args if isinstance(f, Field)]
            #NOTE: a field annotations first argument may be used to wrap
            # input/output to the relevant type (if supported).
            # this is useful for working with things like ENUMS
            # within struct definitions
            farg = args[0]
            if sub_anno is anno \
                and get_origin(args[0]) is None \
                and callable(farg):
                wrap = farg
            if fields:
                return (wrap, fields[0])
            annos.extend([f for f in args if isinstance(f, _AnnotatedAlias)])
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
        """
        reset variables in context to their default state
        """
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
