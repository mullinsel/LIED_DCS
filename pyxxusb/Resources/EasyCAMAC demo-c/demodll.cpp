// demodll.cpp : Defines the entry point for the console application.
//


/* CC-USB Demo program Version 1.1
 * 
 * Copyright (C) 2005-2009 JTEC Instruments - Jan Toke (toke@chem.rochester.edu)
 * cc-usb_camac library included, WIENER Plein & Baus - Andreas Ruben (aruben@wiener-us.com)
 *
 *     This program is free software; you can redistribute it and/or
 *     modify it under the terms of the GNU General Public License as
 *     published by the Free Software Foundation, version 2.
 *
 * This program demonstrates the use of libusb to communicate with CC-USB.
 * The prerequisites are:
 * (i) EHCI driver installed - it is part of newer distributions of Linux
 * (ii) libusb package installed - it is installed automatically by newer 
 * distributions (I amd using Mandriva 10.2).
 *
 * The program calls first usb_init(), usb_find_busses(), and usb_find_devices(),
 * passing relevant arguments to structures bus and dev.
 * 
 * compile as:
 * gcc -o demo3 demo3.c -I/usr/local/include -L. -Insl -lm -lc -L/usr/local/lib -lusb
*/
#include <stdio.h>
#include <string.h>
#include "stdafx.h"
#include <time.h>
#include "xxusbdll.h"
#include <windows.h>

BOOLEAN xxusb_reboot(HANDLE*);

int main()
//int APIENTRY WinMain(HINSTANCE instance, HINSTANCE prev_instance,
//                     LPSTR cmd_line, int cmd_show)
{
  struct usb_device *dev;
  xxusb_device_type xxusbDev[32];
  usb_dev_handle *udev;
  
  int i;
  int i1,i2,i3;
  char nafin[20];
  char nafinx[20];
  char OpCode,ch;
  int CamN, CamA, CamF;
  long CamD;
  int WriteMode;
  int DevFound;
    FILE *fptr;
  UCHAR *pconfig;
  UCHAR *p;
  UCHAR tch;
  int chint;
  long ik;
  char cfilename[100];
  unsigned char outbuf[2000];
  int ret,CamQ, CamX;
  short RegNum;
	time_t t1,t2;
  long RegisterData;
  long intbuf[1000];	
	static char device[2][10]=
	{"CC-USB",
	"VM-USB"};
	for (i=0; i<10; i++)
		outbuf[i]=5;
	OpCode='5';
	printf("\n*************************************************************************\n\n");
	printf("          Welcome to the World of CC-USB \n");
	while ((OpCode != 'X') & (OpCode != 'x'))
	{
	printf("\n");
	printf("Select Operation\n");
	printf("1 - Initialize USB Link\n");
	printf("2 - Toggle FPGA Reset (Rotary Switch in P Position) \n");
	printf("3 - Program Flash Memory\n");
	printf("4 - Write to a Register\n");
	printf("5 - Read from a Register\n");
	printf("6 - Do EASY Camac NAF Operation\n");
	printf("7 - EASY CAMAC NAF, Z, C, I demo\n");
	printf("8 - Test Write to Stack\n");
	printf("9 - Test Readback from Stack\n");
	printf("A - Execute Stack\n");
	printf("x - Exit\n\n");
	printf("Enter Operation Code -> ");
	OpCode=getchar();
	ch=getchar();
	switch (OpCode)
	{
	case '1':
	  if ((DevFound=xxusb_devices_find(xxusbDev))>0)
	    {	  
	      printf("\n");
	      for (i=0; i < DevFound; i++)
		{
		dev=xxusbDev[i].usbdev;
		printf("  %i: Product Id = %i, SerialNumber = %s\n",
		       (i+1),dev->descriptor.idProduct, xxusbDev[i].SerialString);
		}
	      udev = xxusb_device_open(dev);
	      if (udev)
		{
			printf("\n****************************************************\n");
			printf("****************************************************\n");
			if (dev->descriptor.idProduct==XXUSB_CCUSB_PRODUCT_ID)
				printf("CC-USB Found with Serial Number %s\n",xxusbDev[0].SerialString);
  			else if (dev->descriptor.idProduct==XXUSB_VMUSB_PRODUCT_ID)
				printf("VM-USB Found with Serial Number %s\n",xxusbDev[0].SerialString);
			printf("****************************************************\n");
			printf("****************************************************\n");
		  }
	    }
	  else if (DevFound==0)
		    printf("No Valid Device Found");
	  else
	       printf(" Cannot Open Handle to a XX-USB Device, Try to Run in Superuser Mode \n\n");
		break;
	case '2':
	  ret = xxusb_reset_toggle(udev);
		break;
	case '3':
		ik=0;
		strcpy(cfilename,"c:\\xilinxconfig\\ccusb\\cc_test_060405.bit");
		if ((fptr=fopen(cfilename,"rb"))==NULL)
			break;
		pconfig = (UCHAR*)malloc(220000);
//		for (i=0; i<1000; i++)
//
		p=pconfig;
//		while ((chint=getc(fptr)) !=255)
//		p++;
		pconfig=p;
		while((chint=getc(fptr)) != EOF)
		{
			*p = (UCHAR)chint;
			p++;
			ik=ik+1;
		}
		printf("\n");
		for (i=0; i < XXUSB_CC_NUMSEC; i++)
		{
			tch=*pconfig;
			if (tch>0) 
				tch=tch+1;
//			ret=xxusb_flashblock_program(udev,pconfig);
			pconfig=pconfig+256;
			t1=clock()+(time_t)(0.03*CLOCKS_PER_SEC);
			while (t1>clock());
			t2=clock();
			printf(".");
			if (i>0)
				if ((i & 63)==63)
				printf("\n");
		}
		break;
	case '4':
		printf("    Register Number, Data (Comma-separated) -> ");
		fflush(stdin);
		scanf("%i,%i",&RegNum,&RegisterData);
		ret=xxusb_register_write(udev, RegNum, RegisterData);
		ch=getchar();
		break;
	case '5':
		printf("    Register Number -> ");
		fflush(stdin);
		scanf("%i",&RegNum);
		ret=xxusb_register_read(udev, RegNum,&RegisterData);
       		if (ret<0)
		  break;
		printf("\n       D = %06xsu\n\n",RegisterData);
		ch=getchar();
		break;
	case '6':
		strcpy(nafin,"5,5,0");
		sscanf(nafin,"%i,%i,%i",&CamN,&CamA,&CamF);
		while (CamN>0)
		{
			printf("    N,A,F (Comma-separated; x for exit; p for NAF=%i,%i,%i) -> ",CamN, CamA, CamF);
			fflush(stdin);
			scanf("%s",&nafinx);
			if (nafinx[0]=='X' || nafinx[0]=='x') 
			{
				break;
			}
			if (strlen(nafinx)>4)
				strcpy(&nafin[0], &nafinx[0]);
			sscanf(nafin,"%i,%i,%i",&CamN,&CamA,&CamF);
			fflush(stdin);
			if (CamF < 8)	
			{
				ret = CAMAC_read(udev, CamN, CamA, CamF, &CamD,&CamQ, &CamX);
				if (ret < 0)
					printf("Read Operation Failed\n");
				else
					printf("\n       X = %i, Q = %i, D = %06x\n\n",CamX, CamQ, CamD);
			}
			if ((CamF > 7) && (CamF < 16))
			{
				ret = CAMAC_read(udev, CamN, CamA, CamF, &CamD,&CamQ, &CamX);
				if (ret < 0)
					printf("Write Operation Failed\n");
				else
					printf("\n       X = %i, Q = %i\n\n",CamX, CamQ);
			}
			if ((CamF > 15) && (CamF < 24))
			{	
				WriteMode=1;
				printf("     D (Use 0x Prefix for Hexadecimal)-> ");
				scanf("%i", &CamD);
				fflush(stdin);
				CAMAC_write(udev, CamN, CamA, CamF, CamD,&CamQ, &CamX);
			}	
		}
		ch=getchar();
		break;
	case '7':
	  printf("EASY CAMAC NAF, Z, C, I demo\n");
  		CAMAC_Z(udev);
		CAMAC_I(udev, true);
		CAMAC_write(udev, 1, 0, 16, 0xaaaaaa,&CamQ, &CamX);
		CAMAC_write(udev, 1, 0, 25, 0x7,&CamQ, &CamX);
		CAMAC_read(udev, 1, 0, 0, &CamD,&CamQ, &CamX);
		CAMAC_C(udev);
		CAMAC_I(udev, false);
		CAMAC_Z(udev);
	    for (ik=0; (ik <= 100000); ik++)
			CAMAC_write(udev, 1, 0, 16, ik,&CamQ, &CamX);
		break;
	case '8':
	  printf("       Starting Number, Last Number (must be less than 256) - ");
	  scanf("%i,%i,%i",&i1, &i2);
	  i3=i2-i1+1;
	  if (i3 > 700)
	    break;
	  for (i=i1; (i <= i2); i++)
	      intbuf[i-i1+1] = i;
	  intbuf[0]=i3;
	  ret=xxusb_stack_write(udev, XXUSB_READOUT_STACK, intbuf);
	  ch=getchar();
	  break;
	case '9':
	  ret=xxusb_stack_read(udev, XXUSB_READOUT_STACK, intbuf);
	  if (ret>0)
	    for (i=0; (i <= (intbuf[0])); i++)
	      printf("%i\n", intbuf[i]);
	  break;
	case 'X':
		break;
	case 'x':
		break;
	}
	}
	if (udev)
	xxusb_device_close(udev);
	return 1;
}

 
