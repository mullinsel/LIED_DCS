
#include <iostream>
#include "xxusbdll.h"

using namespace std;



int __stdcall devices_find() {
    xxusb_device_type xxusbDev[32];
    return xxusb_devices_find(xxusbDev);
}


usb_dev_handle* __stdcall device_open() {
    xxusb_device_type xxusbDev[32];
    xxusb_devices_find(xxusbDev);
    struct usb_device* dev;
    dev = xxusbDev[0].usbdev;
    return xxusb_device_open(dev);
}



/*
int main() {
    cout << devices_find() << endl;
    CAMAC_C(device_open());
}
*/