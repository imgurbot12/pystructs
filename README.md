PyStructs
---------

[![PyPI version](https://img.shields.io/pypi/v/pystructs3?style=for-the-badge)](https://pypi.org/project/pystructs3/)
[![Python versions](https://img.shields.io/pypi/pyversions/pystructs3?style=for-the-badge)](https://pypi.org/project/pystructs3/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://github.com/imgurbot12/pystructs/blob/master/LICENSE)
[![Made with Love](https://img.shields.io/badge/built%20with-%E2%99%A5-orange?style=for-the-badge)](https://github.com/imgurbot12/pystructs)

A convenient
[`dataclass`](https://docs.python.org/3/library/dataclasses.html)
version of python's
[`struct`](https://docs.python.org/3/library/struct.html) library
for packing and unpacking objects to their equivalent byte representations.

### Installation

```
pip install pystructs3
```

### Examples

###### Simple Example

```python
from pystructs import *

class Bar(Struct):
    z: U32

class Foo(Struct):
    x:   U8
    y:   U16
    bar: Bar

# pack and unpack structs with their builtin methods
foo1   = Foo(230, 65000, Bar(2147483648))
packed = foo1.pack()
foo2   = Foo.unpack(packed)
print('original', foo1)
print('packed', packed)
print('unpacked', foo2)

# equivalent functional version for additional utility
packed   = pack((U8, U16, U32), 230, 65000, 2147483648)
unpacked = unpack((U8, U16, U32), packed)
print('packed', packed)
print('unpacked', unpacked)
```

###### More Complex Example

```python
from typing import List
from ipaddress import IPv4Address, IPv6Address
from typing_extensions import Annotated
from pystructs import *

class Bar(Struct):
    mac:    MACAddr
    ip4:    IPv4
    ip6:    IPv6
    domain: Domain

class Foo(Struct):
    signed:   I8  # I8/I16/I32/I48/I64/I128
    unsigned: U32 # U8/U16/U32/U48/U64/U128
    custom:   Annotated[int, IntField(1, 'little', False)] # custom integer
    b_hinted: Annotated[bytes, HintedBytes(U16)] # dynamic with size hint
    b_static: bytes = field(field=StaticBytes(16)) # static sized bytes
    l_hinted: Annotated[List[int], HintedList(U8, U8)] # dynamic with size hint
    l_static: List[int] = field(field=StaticList(2, U8)) # static sized list

    # b_greedy: bytes = field(field=GreedyBytes()) # consumes rest of message
    # l_list: List[int] = field(field=GreedyList(U8)) # consumes rest of message

bar = Bar('01:02:03:04:05:06', IPv4Address('1.2.3.4'), IPv6Address('::1'), b'example.com')
foo = Foo(1, 2, 3, b'hinted', b'static', [4, 5, 6], [7, 8])

# use a context object when packing/unpacking multiple objects in sequence
ctx    = Context()
packed = bar.pack(ctx) + foo.pack(ctx)

ctx.reset() # context uses index to track place in buffer (must be reset)
bar2 = bar.unpack(packed, ctx)
foo2 = foo.unpack(packed, ctx)

print('foo1', foo)
print('bar1', bar)
print('packed', packed)
print('foo2', foo2)
print('bar2', bar2)
```
