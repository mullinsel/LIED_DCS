import numpy as np
import re
from pyxxusb import pyxxusb

class DAQSetting:
    def __init__(self,device,configFile):
        self.device = device
        self.configFile = configFile

    def setup_TDC(self):
        return


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
        triggerdelay = self.parse_file("Trigger delay = ",settingsFile)
        channels = self.parse_file("Channels = ",settingsFile)
        stack = self.parse_file("Stack = ",settingsFile)
        tdcheaders = self.parse_file("Enable TDC headers = ",settingsFile)
        tdcwarnings = self.parse_file("Enable TDC warnings = ",settingsFile)
        tdcbypass = self.parse_file("Enable TDC bypass warning = ",settingsFile)
        ettmode = self.parse_file("ETT mode = ",settingsFile)
        return tdcaddress,triggermode,offset,window,reject,triggerdelay,channels,stack,tdcheaders,tdcwarnings,tdcbypass,ettmode

setup = DAQSetting('device','configSetup.txt')
setup.setup_VME()