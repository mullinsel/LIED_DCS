from distutils.core import setup, Extension


xxusb_module = Extension('_pyxxusb',
                           sources=['pyxxusb_wrap.cxx', 'pyxxusb.cpp'],
                           libraries=['libxxusb'],
                           depends=["xxusbdll.h","pyxxusb.h"],
                           )

setup (name = 'pyxxusb',
       version = '0.1.0',
       author      = "Aziz Alqasem",
       description = """pyxxusb is a python wrapper around the libxxusb (c/c++ library), using swig wrapper software""",
       ext_modules = [xxusb_module],
       py_modules = ["pyxxusb"],
       )