import numpy as np
import re
from pyxxusb import pyxxusb
import time

class DAQSetting:
    def __init__(self,device,configFile):
        self.device = device
        self.configFile = configFile
        pulledSettings = self.open_config_file(str(self.configFile))
        self.baseAddress = hex(int(pulledSettings[0],16))
        self.triggerMode = pulledSettings[1]
        self.offset = int(pulledSettings[2])
        self.window = float(pulledSettings[3])
        self.reject = int(pulledSettings[4])
        self.triggerdelay = int(pulledSettings[5])
        self.channels = np.array([int(i) for i in pulledSettings[6].split(',')])
        self.stack = np.array([hex(int(i,16)) for i in pulledSettings[7].split(',')])#pulledSettings[7]
        self.tdcheaders = pulledSettings[8]
        self.tdcwarnings = pulledSettings[9]
        self.tdcbypass = pulledSettings[10]
        self.ettmode = pulledSettings[11]
        self.triggersubtract = pulledSettings[12]


    def set_tdcheaders(self):
        if self.tdcheaders=='True' or self.tdcheaders=='true':
            headerwritecheck = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x3000)
            time.sleep(1)
        if self.tdcheaders=='False' or self.tdcheaders=='false':
            headerwritecheck= pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x3100)
            time.sleep(1)
        else:
            headerwritecheck = -8 #written to be the -index of the settings array element from the config file so it can be identified
        return headerwritecheck

    def set_tdcwarnings(self):
        if self.tdcwarnings=='True' or self.tdcwarnings=='true':
            warningswritecheck = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x3500)
            time.sleep(1)
        if self.tdcwarnings=='False' or self.tdcwarnings=='false':
            warningswritecheck= pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x3600)
            time.sleep(1)
        else:
            warningswritecheck = -9
        return warningswritecheck

    def set_tdcbypass(self):
        if self.tdcbypass=='True' or self.tdcbypass=='true':
            bypasswritecheck = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x3700)
            time.sleep(1)
        if self.tdcheaders=='False' or self.tdcheaders=='false':
            bypasswritecheck = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x3800)
            time.sleep(1)
        else:
            bypasswritecheck = -10
        return bypasswritecheck

    def set_ettmode(self):
        if self.ettmode=='True' or self.ettmode=='true':
            ettwritecheck = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x3000)
            time.sleep(1)
        if self.ettmode=='False' or self.ettmode=='false':
            ettwritecheck = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x3100)
            time.sleep(1)
        else:
            ettwritecheck = -11
        return ettwritecheck

    def set_offset(self):
        offsetwritecheck1 = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x1100)
        time.sleep(1)
        offsetwritecheck2 = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,self.offset)
        time.sleep(1)
        return offsetwritecheck1,offsetwritecheck2

    def set_window(self):
        windowwritecheck1 = pyxxusb.VME_write_16(self.device, 0x0E, 0x0400102E, 0x1000)
        time.sleep(1)
        windowwritecheck2 = pyxxusb.VME_write_16(self.device, 0x0E, 0x0400102E, self.window)
        time.sleep(1)
        return windowwritecheck1, windowwritecheck2

    def set_extraSearch(self):
        extrasearchwritecheck1 = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x1200)
        time.sleep(1)
        extrasearchwritecheck2 = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,self.extrasearch)
        time.sleep(1)
        return extrasearchwritecheck1,extrasearchwritecheck2

    def set_reject(self):
        rejectwritecheck1 = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x1300)
        time.sleep(1)
        rejectwritecheck2 = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,self.reject)
        time.sleep(1)
        return rejectwritecheck1,rejectwritecheck2

    def set_triggersubtract(self):
        if self.triggersubtract=='True' or self.triggersubtract=='true':
            subtractwritecheck = pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x1400)
            time.sleep(1)
        if self.triggersubtract=='False' or self.triggersubtract=='false':
            subtractwritecheck= pyxxusb.VME_write_16(self.device,0x0E,0x0400102E,0x1500)
            time.sleep(1)
        else:
            subtractwritecheck = -12 #written to be the -index of the settings array element from the config file so it can be identified
        return subtractwritecheck

    def setup_TDC(self):
        windowcheck1,windowcheck2 = self.set_window()  #0x1000 in manual OPCODES
        offsetcheck1,offsetcheck2 = self.set_offset()  #0x1100 in manual OPCODES
        extrasearchcheck1,extrasearchcheck2 = self.set_extraSearch() #0x1200 in manual OPCODES
        rejectcheck1,rejectcheck2 = self.set_reject() #0x1300 in manual OPCODES
        subtractcheck1 = self.set_triggersubtract() #0x1400 and 0x1500 in manual OPCODES

        checkList = np.array([windowcheck1,windowcheck2,offsetcheck1,offsetcheck2,extrasearchcheck1,extrasearchcheck2,rejectcheck1,rejectcheck2,subtractcheck1])
        if np.any(checkList < 0 ):
            return -1
        else:
            return 1

    def setup_VME(self):
        pulledSettings = self.open_config_file(str(self.configFile))
        #print(hex(int(pulledSettings[5])))
        #pyxxusb.VME_register_write(self.device,8,hex(int(pulledSettings[5])))
        return

    def parse_file(self,keyName,textInfo):
        startindex = re.search(keyName, textInfo).end()
        endindex = re.search("\s", textInfo[startindex:]).start()
        parsedinfo = textInfo[startindex:startindex + endindex]
        return parsedinfo

    def open_config_file(self,fileName):
        settingsFile = open(fileName,'r').read()
        tdcaddress = self.parse_file("TDC address = ",settingsFile)
        triggermode = self.parse_file("Trigger mode = ",settingsFile)
        offset = self.parse_file("Offset = ",settingsFile)
        window = self.parse_file("Window = ",settingsFile)
        reject = self.parse_file("Reject margin = ",settingsFile)
        triggerdelay = self.parse_file("Trigger delay read = ",settingsFile)
        channels = self.parse_file("Channels = ",settingsFile)
        stack = self.parse_file("Stack = ",settingsFile)
        tdcheaders = self.parse_file("Enable TDC headers = ",settingsFile)
        tdcwarnings = self.parse_file("Enable TDC warnings = ",settingsFile)
        tdcbypass = self.parse_file("Enable TDC bypass warning = ",settingsFile)
        ettmode = self.parse_file("ETT mode = ",settingsFile)
        triggersubtract = self.parse_file("Trigger subtraction = ",settingsFile)
        return tdcaddress,triggermode,offset,window,reject,triggerdelay,channels,stack,tdcheaders,tdcwarnings,tdcbypass,ettmode,triggersubtract

setup = DAQSetting(pyxxusb.xxusb_serial_open('VM0353'),'configSetup.txt')
setup.setup_TDC()