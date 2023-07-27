/* CC-USB EASY CAMAC library
 * 
 * Copyright (C) WIENER, Plein & Baus / JTEC 2005-2009 
 * version 1.1, 12/05/05
 *     This program is free software; you can redistribute it and/or
 *     modify it under the terms of the GNU General Public License as
 *     published by the Free Software Foundation, version 2.
 *
 * CC-USB EASY CAMAC calls are direct calls through USB  
 * 
*/
//****************   Pre definition of functions   ************************

#include "xxusbdll.h"


int CAMAC_write(usb_dev_handle *hdev, int N, int A, int F, long Data, int *Q, int *X);
int CAMAC_read(usb_dev_handle *hdev, int N, int A, int F, long *Data, int *Q, int *X);
int CAMAC_Z(usb_dev_handle *hdev);
int CAMAC_C(usb_dev_handle *hdev);
int CAMAC_I(usb_dev_handle *hdev, int inhibit); 

int CAMAC_write(usb_dev_handle *hdev, int N, int A, int F, long Data, int *Q, int *X)
{
    long intbuf[4];  
    int ret;
// CAMAC direct write function
    intbuf[0]=1;
    intbuf[1]=(long)(F+A*32+N*512 + 0x4000);
    if ((F > 15) && (F < 24))
    {	
	intbuf[0]=3;
	intbuf[2]=(Data & 0xffff);
	intbuf[3]=((Data >>16) & 255);
	ret = xxusb_stack_execute(hdev, intbuf);
	*Q = (intbuf[0] & 1);
	*X = ((intbuf[0] >> 1) & 1);
    }	
    return ret;
}

int CAMAC_read(usb_dev_handle *hdev, int N, int A, int F, long *Data, int *Q, int *X)
{
    long intbuf[4];  
    int ret;
    // CAMAC direct read function
    intbuf[0]=1;
    intbuf[1]=(long)(F+A*32+N*512 + 0x4000);
    ret = xxusb_stack_execute(hdev, intbuf);
    if (F < 16)
    {
	*Data=intbuf[0] + (intbuf[1] & 255) * 0x10000;   //24-bit word 
	*Q = ((intbuf[1] >> 8) & 1);
	*X = ((intbuf[1] >> 9) & 1);
    }	
    return ret;
}

int CAMAC_Z(usb_dev_handle *hdev)
{
    long intbuf[4];  
    int  ret;
//  CAMAC Z = N(28) A(8) F(29)
    intbuf[0]=1;
    intbuf[1]=(long)(29+8*32+28*512 + 0x4000);
    ret = xxusb_stack_execute(hdev, intbuf);
    return ret;
}

int CAMAC_C(usb_dev_handle *hdev)
{
    long intbuf[4];  
    int ret;
//  CAMAC C = N(28) A(9) F(29)
    intbuf[0]=1;
    intbuf[1]=(long)(29+9*32+28*512 + 0x4000);
    ret = xxusb_stack_execute(hdev, intbuf);
    return ret;
}

int CAMAC_I(usb_dev_handle *hdev, int inhibit)
{
    long intbuf[4];  
    int  ret;
//	Set Inhibit		= N(29) A(9) F(24)
//	Clear Inhibit	= N(29) A(9) F(26)
    intbuf[0]=1;
    if (inhibit) intbuf[1]=(long)(24+9*32+29*512 + 0x4000);
    else intbuf[1]=(long)(26+9*32+29*512 + 0x4000);
    ret = xxusb_stack_execute(hdev, intbuf);
    return ret;
}
