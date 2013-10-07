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