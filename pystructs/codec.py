"""
Base Codec Definitions
"""
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Protocol, Any, ClassVar
from typing_extensions import runtime_checkable

#** Variables **#
__all__ = ['Context', 'Codec']

#** Classes **#

@dataclass
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
class Codec(Protocol):
    """Encoding/Decoding Codec Protocol"""
    init:      ClassVar[bool] = True
    default:   ClassVar[Any]  = None
    base_type: type
    
    @classmethod
    def sizeof(cls) -> int:
        name = cls.__name__
        raise RuntimeError(f'Cannot get sizeof {name!r}')

    @classmethod
    @abstractmethod
    def encode(cls, ctx: Context, value: Any) -> bytes:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def decode(cls, ctx: Context, raw: bytes) -> Any:
        raise NotImplementedError
