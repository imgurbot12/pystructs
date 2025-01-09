PyStructs
---------
Implements a dataclass version of python's stdlib
[struct](https://docs.python.org/3/library/struct.html) library.

Structs decode values as defined by their type annotations and allows
for simple, easy, and fast encoding/decoding of complex data-structures.

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

# same as struct.pack('>BHI', 230, 6500, 2147483648)
foo    = Foo(230, 65000, Bar(2147483648))
packed = foo.pack()
print('foo', foo)
print('packed', packed)

foo = Foo.unpack(packed)
print('unpacked', foo)

encoded = pack((U8, U16), 230, 65000)
print(encoded)

decoded = unpack((U8, U16), encoded)
print(decoded)
```

###### More Complex Example

```python
from pystructs import *
from ipaddress import IPv4Address, IPv6Address
from typing_extensions import Annotated

class Foo(Struct):
    x:    I16
    y:    U32
    ip:   IPv4
    data: Annotated[bytes, HintedBytes(U16)]

class Bar(Struct):
    mac:  MACAddr
    ip6:  IPv6
    data: Annotated[bytes, StaticBytes(16)]

foo = Foo(69, 420, IPv4Address('1.2.3.4'), b'example message')
bar = Bar('00:01:02:03:04:05', IPv6Address('::1'), b'message two')
print('original foo+bar =', foo, bar)
print(foo.x, 'equals', 69)

# use context to encode/decode items in series
ctx = Context()
raw = foo.pack(ctx) + bar.pack(ctx)
print('packed foo+bar =', raw)

# reset context before switching between encoding/decoding
ctx.reset()

foo2 = Foo.unpack(raw, ctx)
bar2 = Bar.unpack(raw, ctx)
print('unpacked foo+bar =', foo2, bar2)

ctx.reset()
encoded = pack((I16, IPv4), 1, IPv4Address('1.2.3.4'), ctx=ctx) + \
    pack((U32, IPv6), 2, IPv6Address('::1'), ctx=ctx)

ctx.reset()
item1 = unpack((I16, IPv4), encoded, ctx=ctx)
item2 = unpack((U32, IPv6), encoded, ctx=ctx)
print(item1, item2)
```
