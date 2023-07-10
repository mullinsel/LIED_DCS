%module pyxxusb
%{
#define SWIG_FILE_WITH_INIT
#include "pyxxusb.h"
#include "xxusbdll.h"
%}

%include "cpointer.i"
%pointer_functions(int,  int_p);
%pointer_functions(long, long_p);
%pointer_functions(char, char_p);

%include "carrays.i"
%array_functions(int, intArray);
%array_functions(long, longArray);
%array_functions(short, shortArray);
%array_functions(char, charArray);


// from pyxxusb.h
int devices_find();
struct usb_dev_handle;
typedef struct usb_dev_handle usb_dev_handle;
usb_dev_handle* device_open();


// from xxusbdll.h
int  xxusb_bulk_read(usb_dev_handle *hDev, void *DataBuffer, int lDataLen, int timeout);
int  xxusb_bulk_write(usb_dev_handle *hDev, void *DataBuffer, int lDataLen, int timeout);
int  xxusb_usbfifo_read(usb_dev_handle *hDev, int *DataBuffer, int lDataLen, int timeout);
int  xxusb_longstack_execute(usb_dev_handle *hDev, void *DataBuffer, int lDataLen, int timeout);

short  xxusb_register_read(usb_dev_handle *hDev, short RegAddr, long *RegData);
short  xxusb_stack_read(usb_dev_handle *hDev, short StackAddr, long *StackData);
short  xxusb_stack_write(usb_dev_handle *hDev, short StackAddr, long *StackData);
short  xxusb_stack_execute(usb_dev_handle *hDev, long *StackData);
short  xxusb_register_write(usb_dev_handle *hDev, short RegAddr, long RegData);
short  xxusb_reset_toggle(usb_dev_handle *hDev);

//short  xxusb_devices_find(xxusb_device_type *xxusbDev);  //use devices_find instead
short  xxusb_device_close(usb_dev_handle *hDev);
//usb_dev_handle*  xxusb_device_open(struct usb_device *dev);  //use device_open
short  xxusb_flash_program(usb_dev_handle *hDev, char *config, short nsect);
short  xxusb_flashblock_program(usb_dev_handle *hDev, UCHAR *config);
usb_dev_handle*  xxusb_serial_open(char *SerialString);

short  VME_register_write(usb_dev_handle *hdev, long VME_Address, long Data);
short  VME_register_read(usb_dev_handle *hdev, long VME_Address, long *Data);
short  VME_LED_settings(usb_dev_handle *hdev, int LED, int code, int invert, int latch);
short  VME_DGG(usb_dev_handle *hdev, unsigned short channel, unsigned short trigger,unsigned short output, long delay, unsigned short gate, unsigned short invert, unsigned short latch);
short  VME_Output_settings(usb_dev_handle *hdev, int Channel, int code, int invert, int latch);
short  VME_scaler_settings(usb_dev_handle *hdev, short channel, short trigger, int enable, int reset);

short  VME_read_16(usb_dev_handle *hdev,short Address_Modifier, long VME_Address, long *Data);
short  VME_read_32(usb_dev_handle *hdev, short Address_Modifier, long VME_Address, long *Data);
short  VME_BLT_read_32(usb_dev_handle *hdev, short Address_Modifier, int count, long VME_Address, long Data[]);
short  VME_write_16(usb_dev_handle *hdev, short Address_Modifier, long VME_Address, long Data);
short  VME_write_32(usb_dev_handle *hdev, short Address_Modifier, long VME_Address, long Data);

short  CAMAC_DGG(usb_dev_handle *hdev, short channel, short trigger, short output, int delay, int gate, short invert, short latch);
short  CAMAC_register_read(usb_dev_handle *hdev, int A, long *Data);
short  CAMAC_register_write(usb_dev_handle *hdev, int A, long Data);
short  CAMAC_LED_settings(usb_dev_handle *hdev, int LED, int code, int invert, int latch);
short  CAMAC_Output_settings(usb_dev_handle *hdev, int Channel, int code, int invert, int latch);
short  CAMAC_read_LAM_mask(usb_dev_handle *hdev, long *Data);
short  CAMAC_write_LAM_mask(usb_dev_handle *hdev, long Data);
short  CAMAC_scaler_settings(usb_dev_handle *hdev, short channel, short trigger, int enable, int reset);

short  CAMAC_write(usb_dev_handle *hdev, int N, int A, int F, long Data, int *Q, int *X);
short  CAMAC_read(usb_dev_handle *hdev, int N, int A, int F, long *Data, int *Q, int *X);
short  CAMAC_Z(usb_dev_handle *hdev);
short  CAMAC_C(usb_dev_handle *hdev);
short  CAMAC_I(usb_dev_handle *hdev, int inhibit); 
short  CAMAC_blockread16(usb_dev_handle *hdev, int N, int A, int F, int loops, int *Data);

