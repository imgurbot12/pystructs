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

class Foo(Struct):
    x: U8
    y: U16
    z: U32

# same as struct.pack('>BHI', 230, 6500, 2147483648)
foo = Foo(230, 65000, 2147483648)
print(foo)
print(foo.pack())

encoded = pack((U8, U16), 230, 65000)
print(encoded)

decoded = unpack((U8, U16), encoded)
print(decoded)
```

###### More Complex Example

```python
from pystructs import *
from typing_extensions import Annotated

class Foo(Struct):
    x:    I16
    y:    U32
    ip:   IPv4
    data: Annotated[bytes, SizedBytes[U16]]

class Bar(Struct):
    mac:  MacAddr
    ip6:  IPv6
    data: Annotated[bytes, StaticBytes[16]]

# use context to encode/decode items in series
ctx = Context()

foo = Foo(69, 420, '1.2.3.4', b'example message')
bar = Bar('00:01:02:03:04:05', '::1', b'message two')
print(foo, bar)
print(foo.x)

raw = foo.encode(ctx) + bar.encode(ctx)
print(raw)

# reset context before switching between encoding/decoding
ctx.reset()

foo2 = Foo.decode(ctx, raw)
bar2 = Bar.decode(ctx, raw)
print(foo2, bar2)

ctx.reset()
encoded = encode(ctx, (I16, IPv4), 1, '1.2.3.4') + \
    encode(ctx, (U32, IPv6), 2, '::1')

ctx.reset()
item1 = decode(ctx, (I16, IPv4), encoded)
item2 = decode(ctx, (U32, IPv6), encoded)
print(item1, item2)
```

### Limitations

This implementation is intentionally simple and avoids doing things like
allowing hierarchies of structured-objects or any real dynamic behavior
outside of parsing a series of specified simple data-types. This is to
avoid any complex class definitions that often feel overly esoteric and
work like _magic_. Instead, dynamic parsing is left to standard python
code to make things simpler and easier to read.
