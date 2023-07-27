import _pyxxusb as pyvme
#import vme_tools as vme
import time

#device = vme.VME_USB()
#data = device.dataLocation
#crate = device.vme_dev
#print(device.vme_dev)
crate = pyvme.xxusb_serial_open('VM0353')
time.sleep(3)
data = pyvme.new_longArray(1)
time.sleep(3)
print(crate)
print(data)

print(pyvme.VME_register_read(crate,0,data))
print(pyvme.long_p_value(data))
#print(device.vme_dev)
print(data)
