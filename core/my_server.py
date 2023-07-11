from msl.loadlib import Server32
import sys
from ctypes import cast,py_object
import os
from infoVME import infoVME
os.chdir('C:\\Users\cbonline\Documents\CC_TDC-main\interface\\')
from sys import version_info as _swig_python_version_info
# Import the low-level C/C++ module
if __package__ or "." in __name__:
    from . import _pyxxusb
else:
    import _pyxxusb
try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

class MyServer(Server32):
    """Wrapper around a 32-bit C++ library 'my_lib.dll' that has an 'add' and 'version' function."""
    def __init__(self, host, port, **kwargs):
        # Load the 'my_lib' shared-library file using ctypes.CDLL
        #path = Server32.remove_site_packages_64bit()
        super(MyServer, self).__init__('C:\\Users\\cbonline\\Documents\\CC_TDC-main\\interface\\pyxxusb\\_pyxxusb.cp39-win32.pyd', 'cdll', host, port)
        # The Server32 class has a 'lib' property that is a reference to the ctypes.CDLL object
        # Call the version function from the library
        self._messages = []
        self._device = []
        self._hdevice = []
        self._memoryLong = []
        self._memoryShort = []
    
    def new_int_p(self):
        return _pyxxusb.new_int_p()

    def copy_int_p(self,value):
        return _pyxxusb.copy_int_p(value)

    def delete_int_p(self,obj):
        return _pyxxusb.delete_int_p(obj)

    def int_p_assign(self,obj, value):
        return _pyxxusb.int_p_assign(obj, value)

    def int_p_value(self,obj):
        return _pyxxusb.int_p_value(obj)

    def new_long_p(self):
        return _pyxxusb.new_long_p()

    def copy_long_p(self,value):
        return _pyxxusb.copy_long_p(value)

    def delete_long_p(self,obj):
        return _pyxxusb.delete_long_p(obj)

    def long_p_assign(self,obj, value):
        return _pyxxusb.long_p_assign(obj, value)

    def long_p_value(self,obj):
        return _pyxxusb.long_p_value(obj)

    def new_char_p(self):
        return _pyxxusb.new_char_p()

    def copy_char_p(self,value):
        return _pyxxusb.copy_char_p(value)

    def delete_char_p(self,obj):
        return _pyxxusb.delete_char_p(obj)

    def char_p_assign(self,obj, value):
        return _pyxxusb.char_p_assign(obj, value)

    def char_p_value(self,obj):
        return _pyxxusb.char_p_value(obj)

    def new_intArray(self,nelements):
        return _pyxxusb.new_intArray(nelements)

    def delete_intArray(self,ary):
        return _pyxxusb.delete_intArray(ary)

    def intArray_getitem(self,ary, index):
        return _pyxxusb.intArray_getitem(ary, index)

    def intArray_setitem(self,ary, index, value):
        return _pyxxusb.intArray_setitem(ary, index, value)

    def new_longArray(self,nelements):
        self._memoryLong = _pyxxusb.new_longArray(nelements)
        return 

    def delete_longArray(self,ary):
        return _pyxxusb.delete_longArray(ary)

    def longArray_getitem(self,vary, index):
        return _pyxxusb.longArray_getitem(ary, index)

    def longArray_setitem(self,ary, index, value):
        return _pyxxusb.longArray_setitem(ary, index, value)

    def new_shortArray(self,nelements):
        return _pyxxusb.new_shortArray(nelements)

    def delete_shortArray(self,ary):
        return _pyxxusb.delete_shortArray(ary)

    def shortArray_getitem(self,ary, index):
        return _pyxxusb.shortArray_getitem(ary, index)

    def shortArray_setitem(self,ary, index, value):
        return _pyxxusb.shortArray_setitem(ary, index, value)

    def new_charArray(self,nelements):
        return _pyxxusb.new_charArray(nelements)

    def delete_charArray(self,ary):
        return _pyxxusb.delete_charArray(ary)

    def charArray_getitem(self,ary, index):
        return _pyxxusb.charArray_getitem(ary, index)

    def charArray_setitem(self,ary, index, value):
        return _pyxxusb.charArray_setitem(ary, index, value)

    def devices_find(self):
        return _pyxxusb.devices_find()

    def device_open(self):
        return _pyxxusb.device_open()

    def xxusb_bulk_read(self,hDev, DataBuffer, lDataLen, timeout):
        return _pyxxusb.xxusb_bulk_read(hDev, DataBuffer, lDataLen, timeout)

    def xxusb_bulk_write(self,hDev, DataBuffer, lDataLen, timeout):
        return _pyxxusb.xxusb_bulk_write(hDev, DataBuffer, lDataLen, timeout)

    def xxusb_usbfifo_read(self,hDev, DataBuffer, lDataLen, timeout):
        return _pyxxusb.xxusb_usbfifo_read(hDev, DataBuffer, lDataLen, timeout)

    def xxusb_longstack_execute(self,hDev, DataBuffer, lDataLen, timeout):
        return _pyxxusb.xxusb_longstack_execute(hDev, DataBuffer, lDataLen, timeout)

    def xxusb_register_read(self,hDev, RegAddr, RegData):
        return _pyxxusb.xxusb_register_read(hDev, RegAddr, RegData)

    def xxusb_stack_read(self,hDev, StackAddr, StackData):
        return _pyxxusb.xxusb_stack_read(hDev, StackAddr, StackData)

    def xxusb_stack_write(self,hDev, StackAddr, StackData):
        return _pyxxusb.xxusb_stack_write(hDev, StackAddr, StackData)

    def xxusb_stack_execute(self,hDev, StackData):
        return _pyxxusb.xxusb_stack_execute(hDev, StackData)

    def xxusb_register_write(self,hDev, RegAddr, RegData):
        return _pyxxusb.xxusb_register_write(hDev, RegAddr, RegData)

    def xxusb_reset_toggle(self,hDev):
        return _pyxxusb.xxusb_reset_toggle(hDev)

    def xxusb_device_close(self):
        _pyxxusb.xxusb_device_close(self._hdevice)
        return

    def xxusb_flash_program(self,hDev, config, nsect):
        return _pyxxusb.xxusb_flash_program(hDev, config, nsect)

    def xxusb_flashblock_program(self,hDev, config):
        return _pyxxusb.xxusb_flashblock_program(hDev, config)

    def xxusb_serial_open(self,SerialString):
        self._hdevice = _pyxxusb.xxusb_serial_open(SerialString)
        self._device = hex(id(self._hdevice))
        return 

    def VME_register_write(self,hdev, VME_Address, Data):
        return _pyxxusb.VME_register_write(hdev, VME_Address, Data)

    def VME_register_read(self,hdev, VME_Address, Data):
        return _pyxxusb.VME_register_read(hdev, VME_Address, Data)

    def VME_LED_settings(self,hdev, LED, code, invert, latch):
        return _pyxxusb.VME_LED_settings(hdev, LED, code, invert, latch)

    def VME_DGG(self,hdev, channel, trigger, output, delay, gate, invert, latch):
        return _pyxxusb.VME_DGG(hdev, channel, trigger, output, delay, gate, invert, latch)

    def VME_Output_settings(self,hdev, Channel, code, invert, latch):
        return _pyxxusb.VME_Output_settings(hdev, Channel, code, invert, latch)

    def VME_scaler_settings(self,hdev, channel, trigger, enable, reset):
        return _pyxxusb.VME_scaler_settings(hdev, channel, trigger, enable, reset)

    def VME_read_16(self,hdev, Address_Modifier, VME_Address, Data):
        return _pyxxusb.VME_read_16(hdev, Address_Modifier, VME_Address, Data)

    def VME_read_32(self,hdev, Address_Modifier, VME_Address, Data):
        return _pyxxusb.VME_read_32(hdev, Address_Modifier, VME_Address, Data)

    def VME_BLT_read_32(self,hdev, Address_Modifier, count, VME_Address, Data):
        return _pyxxusb.VME_BLT_read_32(hdev, Address_Modifier, count, VME_Address, Data)

    def VME_write_16(self,hdev, Address_Modifier, VME_Address, Data):
        return _pyxxusb.VME_write_16(hdev, Address_Modifier, VME_Address, Data)

    def VME_write_32(self,hdev, Address_Modifier, VME_Address, Data):
        return _pyxxusb.VME_write_32(hdev, Address_Modifier, VME_Address, Data)

    def CAMAC_DGG(self,hdev, channel, trigger, output, delay, gate, invert, latch):
        return _pyxxusb.CAMAC_DGG(hdev, channel, trigger, output, delay, gate, invert, latch)

    def CAMAC_register_read(self,hdev, A, Data):
        return _pyxxusb.CAMAC_register_read(hdev, A, Data)

    def CAMAC_register_write(self,hdev, A, Data):
        return _pyxxusb.CAMAC_register_write(hdev, A, Data)

    def CAMAC_LED_settings(self,hdev, LED, code, invert, latch):
        return _pyxxusb.CAMAC_LED_settings(hdev, LED, code, invert, latch)

    def CAMAC_Output_settings(self,hdev, Channel, code, invert, latch):
        return _pyxxusb.CAMAC_Output_settings(hdev, Channel, code, invert, latch)

    def CAMAC_read_LAM_mask(self,hdev, Data):
        return _pyxxusb.CAMAC_read_LAM_mask(hdev, Data)

    def CAMAC_write_LAM_mask(self,hdev, Data):
        return _pyxxusb.CAMAC_write_LAM_mask(hdev, Data)

    def CAMAC_scaler_settings(self,hdev, channel, trigger, enable, reset):
        return _pyxxusb.CAMAC_scaler_settings(hdev, channel, trigger, enable, reset)

    def CAMAC_write(self,hdev, N, A, F, Data, Q, X):
        return _pyxxusb.CAMAC_write(hdev, N, A, F, Data, Q, X)

    def CAMAC_read(self,hdev, N, A, F, Data, Q, X):
        return _pyxxusb.CAMAC_read(hdev, N, A, F, Data, Q, X)

    def CAMAC_Z(self,hdev):
        return _pyxxusb.CAMAC_Z(hdev)

    def CAMAC_C(self,hdev):
        return _pyxxusb.CAMAC_C(hdev)

    def CAMAC_I(self,hdev, inhibit):
        return _pyxxusb.CAMAC_I(hdev, inhibit)

    def CAMAC_blockread16(self,hdev, N, A, F, loops, Data):
        return _pyxxusb.CAMAC_blockread16(hdev, N, A, F, loops, Data)

