import sys
import fasm

from ctypes import *

__all__ = [
    'assemble_function',
]

GetModuleHandle = windll.kernel32.GetModuleHandleA
GetProcAddress = windll.kernel32.GetProcAddress
LoadLibrary = windll.kernel32.LoadLibraryA
FreeLibrary = windll.kernel32.FreeLibrary

# get the private _CData variable
_CData = None
for t in c_int.__mro__:
    if '_CData' in str(t):
        _CData = t

header = 'use32\n'

def assemble_function(return_type, argument_types, script):
    prefix = header
    
    # give the argument names nice aliases
    for i,arg in enumerate(argument_types[::-1]):
        prefix += "%s equ [ebp-%i]\n" % (arg[1], i*4+8)
    
    # add integer constants
    try:
        frame = sys._getframe(1)
        for name,value in frame.f_locals.iteritems():
            if hasattr(value, '__int__'):
                prefix += "%s = %i\n" % (name, value)
            elif isinstance(value, _CData):
                prefix += "%s = %i\n" % (name, addressof(value))
    finally:
        del frame
    
    # fix the argument type list
    argument_types = [type for type,name in argument_types]
    
    # assemble the code and write it to memory
    code = fasm.assemble(prefix+script)
    executable_code = create_string_buffer(code, len(code))
    executable_code_address = addressof(executable_code)
    
    # fix the origin of the codes (hope the code length doesn't change?)
    origin = 'org %i\n' % executable_code_address
    executable_code.raw = fasm.assemble(''.join((prefix,origin,script)))
    
    # mark the memory as executable
    PAGE_EXECUTE_READWRITE = 0x40
    windll.kernel32.VirtualProtect(executable_code_address, len(code), 
                                   PAGE_EXECUTE_READWRITE, byref(c_int()))
    
    # create the python wrapper
    python_wrapper = CFUNCTYPE(return_type, *argument_types)(executable_code_address)
    # prevent GC from deleting code when the function ends
    python_wrapper.executable_code = executable_code 
    return python_wrapper

def get_function_address(name):
    module,func = name.split('.')
    handle = GetModuleHandle(module)

    if handle == 0:
        handle = LoadLibrary(module)
        if handle == 0:
            raise RuntimeError("Could not load module: %s" % module)
        address = GetProcAddress(handle, func)
        FreeLibrary(module)
    else:
        address = GetProcAddress(handle, func)

    return address