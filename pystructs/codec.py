"""
Base Codec Definitions
"""
from abc import abstractmethod
from typing import Dict, TypeVar, Protocol, ClassVar
from typing_extensions import runtime_checkable

from pyderive import dataclass, field

#** Variables **#
__all__ = ['T', 'cname', 'CodecError', 'Context', 'Codec']

#: generic typevar
T = TypeVar('T')

#** Functions **#

def cname(cls) -> str:
    cls = cls if isinstance(cls, type) else type(cls)
    return cls.__name__

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
        self.__init__()

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
