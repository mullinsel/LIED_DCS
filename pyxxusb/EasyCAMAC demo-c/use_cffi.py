from cffi import FFI
ffibuilder = FFI()

# cdef() expects a single string declaring the C types, functions and
# globals needed to use the shared object. It must be in valid C syntax.

with open("xxusbdll.h", 'r') as f_headr:
    hdr = f_headr.read()

ffibuilder.cdef(hdr)

# set_source() gives the name of the python extension module to
# produce, and some C source code as a string.  This C code needs
# to make the declarated functions, types and globals available,
# so it is often just the "#include".
ffibuilder.set_source("_cc_cffi",
"""
       // the C header of the library
    #include <stdio.h>
    #include <string.h>
    #include <time.h>
    #include <windows.h>
    #include "xxusbdll.h"
""",
     libraries=['libxxusb'],   # library name, for the linker
     )#sources=["StdAfx.c"])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)