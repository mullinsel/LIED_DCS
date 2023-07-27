// CC_TDC.cpp : This file contains the 'main' function. Program execution begins and ends there.
#include <iostream>
//#include <string.h>
//#include <time.h>
#include "xxusbdll.h"
//#include <windows.h>


using namespace std;



int CCUSB_Test_DAQ_read_2228(usb_dev_handle* hdev, long loops, long LAM)
{
    long stack[100];
    int i, j, k, k_loops, error_count = 0, events = 0, event_size = 0;
    //      unsigned int IntArray [10000];  //-> produces 32 bit data structure, use only with event alignment!
    short IntArray[10000];  //for FIFOREAD
//      char IntArray [10000];  //for FIFOREAD

//      char * ByteAP;
    long data_lines;
    long CamN, CamDummy;
    int ret, CamQ, CamX;
    //*Change below to a varible N
    int CAM_2228 = 20;                 // station number for 2228 ADC
// prepare stack and load to CC-USB
    CamN = (CAM_2228 << 9);
    //similar to: hex(F + 32*A + 512*N)
    stack[0] = 11;                          // number of lines to follow
    for (i = 0; i < 8; i++) stack[i + 1] = CamN + (i << 5) + 0;       // Read channels F(2) A(i)
    stack[9] = CamN+0x0009;                // CLEAR LAM N()with F(9) A(0) ==> not needed with F(2)A(11)
    stack[10] = 0x0010;                             // add marker
    stack[11] = 0xffff;                             // marker = ffff
// Load stack into CC-USB
    ret = xxusb_stack_write(hdev, 2, stack);
    // Define Trigger LAM=0 -> extern, otherwise LAM
    ret = CAMAC_write(hdev, 25, 9, 16, LAM, &CamQ, &CamX);
    // Define Trigger Delay / LAM time out in Delay Register N(25) A(2) F(16) and enable /disable LAM
    if (LAM == 0)
    {
        //  Define Trigger Delay to 100us for external LAM; bits 0 to 15 in Delay Register N(25) A(2) F(16)
        ret = CAMAC_write(hdev, 25, 2, 16, 0x64, &CamQ, &CamX);
        //  Prepare LeCroy ADC (disable LAM)
        ret = CAMAC_read(hdev, CAM_2228, 0, 24, &CamDummy, &CamQ, &CamX);
        //ret = CAMAC_read(hdev, CAM_2228, 0, 10, &CamDummy, &CamQ, &CamX); //Clear LAM
    }
    else
    {
        //  Define LAM time out to 100us for external LAM; bits 0 to 15 in Delay Register N(25) A(2) F(16)
        ret = CAMAC_write(hdev, 25, 2, 16, 0x640000, &CamQ, &CamX);
        //  Prepare LeCroy ADC (enable LAM)
        ret = CAMAC_read(hdev, CAM_2228, 0, 26, &CamDummy, &CamQ, &CamX); //Enable LAM
        ret = CAMAC_read(hdev, CAM_2228, 0, 10, &CamDummy, &CamQ, &CamX); //Clear LAM
    }
    // Set buffer size to 4k BuffOpt in Global Mode register N(25) A(1) F(16)      
    ret = CAMAC_write(hdev, 25, 1, 16, 0x0, &CamQ, &CamX);

    // Prepare data file
    FILE* data_file;
    data_file = fopen("CCUSB_test_2228.txt", "w");
    //fprintf(data_file, "CC-USB test data file \n");
    // START DAQ
    //      printf("switch to DAQ & Reading data\n");
    //  Clear Data and LAM
    ret = CAMAC_read(hdev, CAM_2228, 0, 9, &CamDummy, &CamQ, &CamX);

    //  Start DAQ mode
    ret = xxusb_register_write(hdev, 1, 0x1); // start acquisition
    k_loops = 0;
    while (k_loops < loops) // number of loops to read
    {
        ret = xxusb_bulk_read(hdev, IntArray, 8192, 100);       // use for 32-bit data
        cout << ret << endl;
        data_lines = ret / 2;
        event_size = (IntArray[1] & 0xffff);
        if (event_size > 0x100) event_size = 0x100; //??
        if (data_file != NULL)
        {
            if (ret > 0)
            {
                events = (IntArray[0] & 0xffff);
                //printf("Events in loop %i : %i\n ",k_loops, events);
                for (j = 0; j <= data_lines; j++) {
                    fprintf(data_file, "%hx,", IntArray[j]);
                    if (j % 10 == 0) fprintf(data_file, "%\t");
                }
            }
            else
            {
                error_count++;
                printf("no read\n");
                continue;
            }
            fprintf(data_file, "\n");
        }
        k_loops++;
    }
    // leave DAQ mode
    xxusb_register_write(hdev, 1, 0x0);
    // drain all data from fifo   
    ret = 1;
    k = 0;
    while (ret > 0)
    {
        ret = xxusb_bulk_read(hdev, IntArray, 8192, 100);
        if (ret > 0)
        {
            //                      printf("drain loops: %i (result %i)\n ",k,ret);
            k++;
            if (k > 100) ret = 0;
        }
    }
    //      in case still DAQ mode -> leave!!!
    //  xxusb_register_write(hdev, 1, 0x0);
    fclose(data_file);
    return 0;
}



int CCUSB_Test_DAQ_read_4208(usb_dev_handle* hdev, long loops, long LAM)
{
    long stack[100];
    int i, j, k, k_loops, error_count = 0, events = 0, event_size = 0;
    //      unsigned int IntArray [10000];  //-> produces 32 bit data structure, use only with event alignment!
    short IntArray[10000];  //for FIFOREAD
//      char IntArray [10000];  //for FIFOREAD

//      char * ByteAP;
    long data_lines;
    long CamN, CamDummy;
    int ret, CamQ, CamX;
    //*Change below to a varible N
    int CAM_4208 = 15;                 // station number for 4208 ADC
// prepare stack and load to CC-USB
    CamN = (CAM_4208 << 9);
    //similar to: hex(F + 32*A + 512*N)
    stack[0] = 11;                          // number of lines to follow
    for (i = 0; i < 8; i++) stack[i + 1] = CamN + (i << 5) + 0;       // Read channels F(2) A(i)
    stack[9] = CamN + 0x0009;                // CLEAR LAM N()with F(9) A(0) ==> not needed with F(2)A(11)
    stack[10] = 0x0010;                             // add marker
    stack[11] = 0xffff;                             // marker = ffff
// Load stack into CC-USB
    ret = xxusb_stack_write(hdev, 2, stack);
    // Define Trigger LAM=0 -> extern, otherwise LAM
    ret = CAMAC_write(hdev, 25, 9, 16, LAM, &CamQ, &CamX);
    // Define Trigger Delay / LAM time out in Delay Register N(25) A(2) F(16) and enable /disable LAM
    if (LAM == 0)
    {
        //  Define Trigger Delay to 100us for external LAM; bits 0 to 15 in Delay Register N(25) A(2) F(16)
        ret = CAMAC_write(hdev, 25, 2, 16, 0x64, &CamQ, &CamX);
        //  Prepare LeCroy ADC (disable LAM)
        ret = CAMAC_read(hdev, CAM_4208, 0, 24, &CamDummy, &CamQ, &CamX);
        //ret = CAMAC_read(hdev, CAM_4208, 0, 10, &CamDummy, &CamQ, &CamX); //Clear LAM
    }
    else
    {
        //  Define LAM time out to 100us for external LAM; bits 0 to 15 in Delay Register N(25) A(2) F(16)
        ret = CAMAC_write(hdev, 25, 2, 16, 0x640000, &CamQ, &CamX);
        //  Prepare LeCroy ADC (enable LAM)
        ret = CAMAC_read(hdev, CAM_4208, 0, 26, &CamDummy, &CamQ, &CamX); //Enable LAM
        ret = CAMAC_read(hdev, CAM_4208, 0, 10, &CamDummy, &CamQ, &CamX); //Clear LAM
    }
    // Set buffer size to 4k BuffOpt in Global Mode register N(25) A(1) F(16)      
    ret = CAMAC_write(hdev, 25, 1, 16, 0x0, &CamQ, &CamX);

    // Prepare data file
    FILE* data_file;
    data_file = fopen("CCUSB_test_4208.txt", "w");
    //fprintf(data_file, "CC-USB test data file \n");
    // START DAQ
    //      printf("switch to DAQ & Reading data\n");
    //  Clear Data and LAM
    ret = CAMAC_read(hdev, CAM_4208, 0, 9, &CamDummy, &CamQ, &CamX);

    //  Start DAQ mode
    ret = xxusb_register_write(hdev, 1, 0x1); // start acquisition
    k_loops = 0;
    while (k_loops < loops) // number of loops to read
    {
        ret = xxusb_bulk_read(hdev, IntArray, 8192, 100);       // use for 32-bit data
        cout << ret << endl;
        data_lines = ret / 2;
        event_size = (IntArray[1] & 0xffff);
        if (event_size > 0x100) event_size = 0x100; //??
        if (data_file != NULL)
        {
            if (ret > 0)
            {
                events = (IntArray[0] & 0xffff);
                //printf("Events in loop %i : %i\n ",k_loops, events);
                for (j = 0; j <= data_lines; j++) {
                    fprintf(data_file, "%hx,", IntArray[j]);
                    if (j % 10 == 0) fprintf(data_file, "%\t");
                }
            }
            else
            {
                error_count++;
                printf("no read\n");
                continue;
            }
            fprintf(data_file, "\n");
        }
        k_loops++;
    }
    // leave DAQ mode
    xxusb_register_write(hdev, 1, 0x0);
    // drain all data from fifo   
    ret = 1;
    k = 0;
    while (ret > 0)
    {
        ret = xxusb_bulk_read(hdev, IntArray, 8192, 100);
        if (ret > 0)
        {
            //                      printf("drain loops: %i (result %i)\n ",k,ret);
            k++;
            if (k > 100) ret = 0;
        }
    }
    //      in case still DAQ mode -> leave!!!
    //  xxusb_register_write(hdev, 1, 0x0);
    fclose(data_file);
    return 0;
}


int main()
{
	struct usb_device* dev;
	xxusb_device_type xxusbDev[32];
	usb_dev_handle* udev;
	int CamN, CamA, CamF;
	long CamD;
	int ret, CamQ, CamX;
	CamN = 1;
	CamA = 0;
	CamF = 0;

    int d = xxusb_devices_find(xxusbDev);
    cout << "Found " << d << " device(s)" <<endl;
    dev = xxusbDev[0].usbdev;
    udev = xxusb_device_open(dev);

    //int CCUSB_Test_DAQ_read_2228(usb_dev_handle* hdev, long loops, long LAM)

    CCUSB_Test_DAQ_read_2228(udev, 20, 0);


    /*
	// Test CAMAC functions
	xxusb_devices_find(xxusbDev);
	dev = xxusbDev[0].usbdev;
	udev = xxusb_device_open(dev);
	ret = CAMAC_read(udev, CamN, CamA, CamF, &CamD, &CamQ, &CamX);
	printf("X = %i, Q = %i, D = %06x\n\n", CamX, CamQ, CamD);
	//std::cout << ret << "  "  << CamX << "  "  << CamQ << "  "  << CamD;
    */
}
