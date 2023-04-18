PyStructs
---------
Dataclass-Like Serialization Helpers for More Complex Data-Types

This library allows for easy encoding/decoding of standardized struct-like
objects. However, it's designed to avoid any dynamic parsing or encoding
beyond a basic structure. Dynamic behavior is intentionally excluded and 
is best left to standard code to reduce the amount of _magic_ involved,
and to make for a simpler and more understandable codebase.

### Installation

```
pip install pystructs3
```

### Examples

```python
from pystructs import *

@struct
class A:
    x:    Int16
    y:    Int32
    ip:   Ipv4
    data: SizedBytes[16]

ctx = Context()

a = A(69, 420, '1.2.3.4', b'example message')
print(a)
print(a.x)

raw = a.encode(ctx)
print(raw)

ctx.reset()

a2 = A.decode(ctx, raw)
print(a2)
```

