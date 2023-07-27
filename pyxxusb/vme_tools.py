"""This module is to interface with the CC-USB using 
the pyxxusb which is a pyhton wrape to the main C/C++
module made by the manufacture.
"""
try:
    import pyxxusb as pyvme
except Exception as e:
    print(e)
    print("pyxxusb lib works only with python 32bit")
    print("The PC should be connected to the vme-usb")

class VME_USB:

    def __init__(self):
        self.vme_dev = pyvme.xxusb_serial_open('VM0353')
        #self.vme_dev = pyvme.device_open()
        self.dataLocation = pyvme.new_longArray(1)

