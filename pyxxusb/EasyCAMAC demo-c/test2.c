//#include <iostream>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "xxusbdll.h"
#include <windows.h>


// Compiles as:
// gcc test.2
BOOLEAN xxusb_reboot(HANDLE*);

int main()
//int APIENTRY WinMain(HINSTANCE instance, HINSTANCE prev_instance,
//                     LPSTR cmd_line, int cmd_show)
{
  struct usb_device *dev;
  xxusb_device_type xxusbDev[32];
  usb_dev_handle *udev;
  int CamN, CamA, CamF;
  long CamD;
  int ret,CamQ, CamX;
  CamN=20;
  CamA=0;
  CamF=0;
  // Test CAMAC functions
  ret = CAMAC_read(udev, CamN, CamA, CamF, &CamD,&CamQ, &CamX);

  //std::cout << ret << "  "  << CamX << "  "  << CamQ << "  "  << CamD;
}