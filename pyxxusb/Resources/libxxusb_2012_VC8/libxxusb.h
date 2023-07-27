#define EXPORT extern "C" _declspec(dllexport)

#define XXUSB_WIENER_VENDOR_ID	0x16DC   /* Wiener, Plein & Baus */
#define XXUSB_VMUSB_PRODUCT_ID	0x000B	 /* VM-USB */
#define XXUSB_CCUSB_PRODUCT_ID	0x0001	 /* CC-USB */
#define XXUSB_ENDPOINT_OUT	2  /* Endpoint 2 Out*/
#define XXUSB_ENDPOINT_IN    0x86  /* Endpoint 6 In */
#define XXUSB_FIRMWARE_REGISTER 0
#define XXUSB_GLOBAL_REGISTER 1
#define XXUSB_ACTION_REGISTER 10
#define XXUSB_DELAYS_REGISTER 2
#define XXUSB_WATCHDOG_REGISTER 3
#define XXUSB_SELLEDA_REGISTER 6
#define XXUSB_SELNIM_REGISTER 7
#define XXUSB_SELLEDB_REGISTER 4
#define XXUSB_SERIAL_REGISTER 15
#define XXUSB_LAMMASK_REGISTER 8
#define XXUSB_LAM_REGISTER 12
#define XXUSB_READOUT_STACK 2
#define XXUSB_SCALER_STACK 3
#define XXUSB_NAF_DIRECT 12

struct XXUSB_STACK
{
long Data;
short Hit;
short APatt;
short Num;
short HitMask;
};

struct XXUSB_CC_COMMAND_TYPE
{
short Crate;
short F;
short A;
short N;
long Data;
short NoS2;
short LongD;
short HitPatt;
short QStop;
short LAMMode;
short UseHit;
short Repeat;
short AddrScan;
short FastCam;
short NumMod;
short AddrPatt;
long HitMask[4];
long Num;
};

struct xxusb_device_typ
{
  struct usb_device *usbdev;
  char SerialString[7];
};

typedef struct xxusb_device_typ xxusb_device_type;
typedef unsigned char UCHAR;
typedef struct usb_bus usb_busx;

int __stdcall ccusb_longstack_execute(usb_dev_handle *hDev, void *DataBuffer, int lDataLen, int timeout);
int __stdcall xxusb_longstack_execute(usb_dev_handle *hDev, void *DataBuffer, int lDataLen, int timeout);
int __stdcall xxusb_bulk_read(usb_dev_handle *hDev, void *DataBuffer, int lDataLen, int timeout);
int __stdcall xxusb_bulk_write(usb_dev_handle *hDev, void *DataBuffer, int lDataLen, int timeout);
int __stdcall xxusb_usbfifo_read(usb_dev_handle *hDev, int *DataBuffer, int lDataLen, int timeout);

short __stdcall xxusb_register_read(usb_dev_handle *hDev, short RegAddr, long *RegData);
short __stdcall xxusb_stack_read(usb_dev_handle *hDev, short StackAddr, long *StackData);
short __stdcall xxusb_stack_write(usb_dev_handle *hDev, short StackAddr, long *StackData);
short __stdcall xxusb_stack_execute(usb_dev_handle *hDev, long *StackData);
short __stdcall xxusb_register_write(usb_dev_handle *hDev, short RegAddr, long RegData);
short __stdcall xxusb_reset_toggle(usb_dev_handle *hDev);

void __stdcall xxusb_init();
short __stdcall xxusb_devices_find(xxusb_device_type *xxusbDev);
short __stdcall xxusb_device_close(usb_dev_handle *hDev);
usb_dev_handle* __stdcall xxusb_device_open(struct usb_device *dev);
short __stdcall xxusb_flash_program(usb_dev_handle *hDev, char *config, short nsect);
short __stdcall xxusb_flashblock_program(usb_dev_handle *hDev, UCHAR *config);
usb_dev_handle* __stdcall xxusb_serial_open(char *SerialString);

short __stdcall VME_register_write(usb_dev_handle *hdev, long VME_Address, long Data);
short __stdcall VME_register_read(usb_dev_handle *hdev, long VME_Address, long *Data);
short __stdcall VME_LED_settings(usb_dev_handle *hdev, int LED, int code, int invert, int latch);
short __stdcall VME_DGG(usb_dev_handle *hdev, unsigned short channel, unsigned short trigger,unsigned short output, long delay, unsigned short gate, unsigned short invert, unsigned short latch);
short __stdcall VME_scaler_settings(usb_dev_handle *hdev, short channel, short trigger, int enable, int reset);
short __stdcall VME_Output_settings(usb_dev_handle *hdev, int Channel, int code, int invert, int latch);

short __stdcall VME_read_8(usb_dev_handle *hdev,short Address_Modifier, long VME_Address, long *Data);
short __stdcall VME_read_16(usb_dev_handle *hdev,short Address_Modifier, long VME_Address, long *Data);
short __stdcall VME_read_32(usb_dev_handle *hdev, short Address_Modifier, long VME_Address, long *Data);
short __stdcall VME_BLT_read_32(usb_dev_handle *hdev, short Address_Modifier, int count, long VME_Address, long Data[]);
short __stdcall VME_write_16(usb_dev_handle *hdev, short Address_Modifier, long VME_Address, long Data);
short __stdcall VME_write_32(usb_dev_handle *hdev, short Address_Modifier, long VME_Address, long Data);

short __stdcall CAMAC_DGG(usb_dev_handle *hdev, short channel, short trigger, short output, int delay, int gate, short invert, short latch);
short __stdcall CAMAC_register_read(usb_dev_handle *hdev, int A, long *Data);
short __stdcall CAMAC_register_write(usb_dev_handle *hdev, int A, long Data);
short __stdcall CAMAC_LED_settings(usb_dev_handle *hdev, int LED, int code, int invert, int latch);
short __stdcall CAMAC_Output_settings(usb_dev_handle *hdev, int Channel, int code, int invert, int latch);
short __stdcall CAMAC_read_LAM_mask(usb_dev_handle *hdev, long *Data);
short __stdcall CAMAC_write_LAM_mask(usb_dev_handle *hdev, long Data);
short __stdcall CAMAC_scaler_settings(usb_dev_handle *hdev, short channel, short trigger, int enable, int reset);

short __stdcall CAMAC_write(usb_dev_handle *hdev, int N, int A, int F, long Data, int *Q, int *X);
short __stdcall CAMAC_read(usb_dev_handle *hdev, int N, int A, int F, long *Data, int *Q, int *X);
short __stdcall CAMAC_Z(usb_dev_handle *hdev);
short __stdcall CAMAC_C(usb_dev_handle *hdev);
short __stdcall CAMAC_I(usb_dev_handle *hdev, int inhibit); 
short __stdcall CAMAC_blockread16(usb_dev_handle *hdev, int N, int A, int F, int loops, int *Data);

