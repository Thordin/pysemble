pysemble
========

Python Inline Assembler

Use i386 assembly inside Python without calling an external program. Python integers and ctype values can
be referenced inside the assembly just like C.

=== Example ===

```python
import pysemble
from ctypes import *

MessageBoxAddress = pysemble.get_function_address("user32.MessageBoxA")
register = c_int()

MessageBox = pysemble.assemble_function(c_int, [(c_char_p, "msg")],
"""
push 0x30
push 0
push dword msg
push 0
call MessageBoxAddress
mov [register],eax
ret
""")

MessageBox('hello world 123')
print register
```

=== Why Pysemble ===

There are quite a few "pyasm" projects on the Internet already but they all had shortcomings. Here is why
Pysemble is better.

* Doesn't call an external program.
* Supports all instructions thanks to FASM.
* Allows referencing python variables.
* Creates a callable function.

=== Requirements ===

Python with ctypes. Currently supports i386 on Windows only. It can be ported to Linux if you can port FASM.

