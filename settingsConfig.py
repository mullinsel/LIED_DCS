import numpy as np
import re
from pyxxusb import pyxxusb
import time

class DAQSetting:
    def __init__(self,device,configFile):
        self.device = device
        self.AM = 0x0E
        self.waittime = 0.3
        self.configFile = configFile
        self.open_config_file(str(self.configFile))
        #self.baseAddress = hex(int(pulledSettings[0],16))
        #self.triggerMode = bool(pulledSettings[1])
        #self.offset = int(pulledSettings[2])
        #self.window = float(pulledSettings[3])
        #self.reject = float(pulledSettings[4])
        #self.triggerdelay = int(pulledSettings[5])
        #self.channels = np.array([int(i) for i in pulledSettings[6].split(',')])
        #self.stack = np.array([hex(int(i,16)) for i in pulledSettings[7].split(',')])#pulledSettings[7]
        #self.tdcheaders = bool(pulledSettings[8])
        #self.tdcwarnings = bool(pulledSettings[9])
        #self.tdcbypass = bool(pulledSettings[10])
        #self.triggersubtract = bool(pulledSettings[11])
        #self.extrasearch = float(pulledSettings[12])
        #self.resolution = int(pulledSettings[13])

    ######################
    ######################
    ###TDC Functions###

    def reset_TDC(self):
        resetcheck = pyxxusb.VME_write_16(self.device, self.AM, self.baseAddress+int(0x1016), 1)
        return resetcheck

    def set_offset(self): #sets the trigger match offset
        offsetwritecheck1 = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x1100) #the initial send starting the write setting process
        time.sleep(self.waittime)
        offsetval = int(self.offset * 1000 / 25) #converting from microseconds to ns then to cycles. TDC reads the setting in terms of cycles
        offsetwritecheck2 = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),offsetval) #writes the setting
        time.sleep(self.waittime)
        return offsetwritecheck1,offsetwritecheck2 #returns error checks. Negative if fail

    def set_window(self): #sets the trigger match window
        time.sleep(self.waittime)
        windowwritecheck1 = pyxxusb.VME_write_16(self.device, self.AM, self.baseAddress+int(0x102E), 0x1000) #the initial write command
        time.sleep(self.waittime)
        windowval = int(self.window*1000/25) #converts to cycles there are 25 ns in a cycle so convert from microseconds
        windowwritecheck2 = pyxxusb.VME_write_16(self.device, self.AM, self.baseAddress+int(0x102E),windowval) #sends the setting to be set
        time.sleep(self.waittime)
        return windowwritecheck1, windowwritecheck2 #write check. If negative then it failed

    def set_extraSearch(self): #sets the extra search window for trigger match mode
        extrasearchwritecheck1 = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x1200) #starts the write process
        time.sleep(self.waittime)
        extrasearchval = int(self.extrasearch*1000/25) #convert to cycles from microseconds
        extrasearchwritecheck2 = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),extrasearchval) #writing the setting
        time.sleep(self.waittime)
        return extrasearchwritecheck1,extrasearchwritecheck2 #write check. If negative it failed

    def set_reject(self): #sets the reject margin for the trigger match mode
        rejectwritecheck1 = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x1300) #starts the write process
        time.sleep(self.waittime)
        rejectval = int(self.reject*1000/25) #convert the number from microseconds to cycles
        rejectwritecheck2 = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),rejectval) #writes the setting
        time.sleep(self.waittime)
        return rejectwritecheck1,rejectwritecheck2 #write checks. If negative then write failed

    def set_triggersubtract(self): #sets the trigger subtraction on or off on the TDC
        if self.triggersubtract=="True": #if true it writes the register the number to set true
            subtractwritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x1400)
            time.sleep(self.waittime)
        else: #else it writes the number to set false
            subtractwritecheck= pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x1500)
            time.sleep(self.waittime)
        return subtractwritecheck #write check. If negative then it failed to write

    def set_resolution(self): #sets the bin resolution on the TDC
        resolutioncheck1 = pyxxusb.VME_write_16(self.device, self.AM, self.baseAddress+int(0x102E), 0x2400) #starts the write process
        time.sleep(self.waittime)
        resval = 3 #defalt value is 3 when turned on in case input does not match logic statements
        #depending on the input, the value is chosen to be written. These are from the manual (binary)
        if self.resolution == 100:
            resval = 2
        if self.resolution == 200:
            resval = 1
        if self.resolution == 800:
            resval = 0
        if self.resolution == 25:
            resval = 3
        resolutioncheck2 = pyxxusb.VME_write_16(self.device, self.AM, self.baseAddress+int(0x102E), resval) #writes the setting
        time.sleep(self.waittime)
        return resolutioncheck1,resolutioncheck2 #write check. If negative then it failed to write

    def set_mode(self): #sets the TDC in either trigger match mode or cont. mode
        time.sleep(self.waittime)
        if self.triggerMode=="True":
            modewritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x0000) #setting the trigger match mode on
            time.sleep(self.waittime)
        else:
            modewritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x0100) #setting the cont. mode on
            time.sleep(self.waittime)
        return modewritecheck #write check. If negative then failed to write

    def set_headers(self): #setting the TDC to enable or disable headers from the TDC by default they are enabled
        time.sleep(self.waittime)
        if self.tdcheaders=="True":
            headerswritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x3000) #writes the enable number
            time.sleep(self.waittime)
        else:
            headerswritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x3100) #writes the disable number this may defalt to disable since its in the else
            time.sleep(self.waittime)
        return headerswritecheck #If returns negative then write failed

    def set_warnings(self): #setting the TDC to output any warning messages if any. Default is on
        time.sleep(self.waittime)
        if self.tdcwarnings=="True":
            warningswritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x3500) #setting the warning/errors to on
            time.sleep(self.waittime)
        else:
            warningswritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x3600) #setting the warnings/error off. This may default to off now since its in else
            time.sleep(self.waittime)
        return warningswritecheck #if negative is returned then write failed

    def set_bypasswarning(self): #sets the TDC to bypass warnings. Default is false
        time.sleep(self.waittime)
        if self.tdcbypass=="True":
            bypasswritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x3700) #sets the bypass setting to be true
            time.sleep(self.waittime)
        else:
            bypasswritecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x3800) #sets the bypass setting to be false. May default now to false because its in else
            time.sleep(self.waittime)
        return bypasswritecheck #if negative then failed to write the setting

    def set_channels(self): #sets up the TDC channels
        time.sleep(self.waittime)
        disablecheck = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x4300) #disables all channels
        time.sleep(self.waittime)
        enableArray = np.zeros(16,dtype=np.int32) #16 bits to be passed, setting what channels are on
        for i in self.channels:
            enableArray[i] = 1
        enableArray = enableArray[::-1] #flip the array to turn into an int
        enableNumber = enableArray.dot(2**np.arange(enableArray.size)[::-1]) #turn binary into int
        enablecheck1 = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),0x4400) #start the send of new settings
        time.sleep(self.waittime)
        enablecheck2 = pyxxusb.VME_write_16(self.device,self.AM,self.baseAddress+int(0x102E),int(enableNumber)) #send settings
        time.sleep(self.waittime)
        return disablecheck,enablecheck1,enablecheck2 #if negative then the settings failed to write

    def setup_TDC(self): #sets all of the parameters for the TDC calling all the functions to be set and returning any errors they had
        modecheck = self.set_mode() #0x0000 and 0x0100 in manual OPCODES
        rescheck1, rescheck2 = self.set_resolution()  # 0x2400 in the manual OPCODES
        headerscheck = self.set_headers() #0x3000 and 0x3100 in the manual OPCODES
        warningscheck = self.set_warnings() #0x3500 and 0x3600 in the manual OPCODES
        bypasscheck = self.set_bypasswarning() #0x3700 and 0x3800 in the manual OPCODES
        disablecheck,enablecheck1,enablecheck2 = self.set_channels() #0x4300 and 0x4400 in the manual OPCODES
        time.sleep(self.waittime)
        pyxxusb.VME_write_16(self.device,self.AM,0x04001024,250) #number of events for block transfer
        time.sleep(self.waittime)
        pyxxusb.VME_write_16(self.device,self.AM,0x04001000,4129) #control settings #32 works well
        time.sleep(self.waittime)

        if self.triggerMode == "True":
            windowcheck1,windowcheck2 = self.set_window()  #0x1000 in manual OPCODES
            offsetcheck1,offsetcheck2 = self.set_offset()  #0x1100 in manual OPCODES
            extrasearchcheck1,extrasearchcheck2 = self.set_extraSearch() #0x1200 in manual OPCODES
            rejectcheck1,rejectcheck2 = self.set_reject() #0x1300 in manual OPCODES
            subtractcheck1 = self.set_triggersubtract() #0x1400 and 0x1500 in manual OPCODES
            #pyxxusb.VME_write_16(self.device, self.AM, 0x0400102E, 0x3300)  # limits the number of hits
            #time.sleep(self.waittime)
            #pyxxusb.VME_write_16(self.device, self.AM, 0x0400102E, 6)
            #time.sleep(self.waittime)
            checkList = np.array([modecheck, rescheck1, rescheck2, windowcheck1, windowcheck2, offsetcheck1, offsetcheck2,extrasearchcheck1, extrasearchcheck2, rejectcheck1, rejectcheck2, subtractcheck1, headerscheck,warningscheck, bypasscheck, disablecheck, enablecheck1, enablecheck2])

        else:
            #windowcheck1,windowcheck2,offsetcheck1,offsetcheck2,extrasearchcheck1,extrasearchcheck2,rejectcheck1,rejectcheck2,subtractcheck1
            checkList = np.array([modecheck,rescheck1,rescheck2,headerscheck,warningscheck,bypasscheck,disablecheck,enablecheck1,enablecheck2])
        if np.any(checkList < 0 ):
            return -1
        else:
            return 1

    ######################
    ######################
    ###VME Functions###

    def reset_VME(self):
        time.sleep(self.waittime)
        #clearcheck = pyxxusb.VME_register_write(self.device,1,4)
        buffdumpcheck1 = pyxxusb.VME_register_write(self.device,1,64)
        time.sleep(self.waittime)
        buffdumpcheck2 = pyxxusb.VME_register_write(self.device,1,0)
        time.sleep(self.waittime)
        sysrescheck1 = pyxxusb.VME_register_write(self.device,1,8)
        time.sleep(self.waittime)
        sysrescheck2 = pyxxusb.VME_register_write(self.device,1,0)
        time.sleep(self.waittime)
        VMEresetcheckList = np.array([buffdumpcheck1,buffdumpcheck2,sysrescheck1,sysrescheck2])
        if np.any(VMEresetcheckList < 0 ):
            return -1
        else:
            return 1
        return

    def set_VME_dataAcq(self): #writes settings to the data acq register
        readoutval = np.binary_repr(self.triggerdelay,width=8) #turns the number into the 8 bits of the total 32 that will be written
        periodval = np.binary_repr(self.scalerreadperiod,width=8)
        frequencyval = np.binary_repr(self.scalerreadfrequency,width=16)
        dataacqvalue = int(frequencyval+periodval+readoutval,2) #putting them all together
        dataacqwritecheck = pyxxusb.VME_register_write(self.device,8,dataacqvalue) #write to the register
        time.sleep(self.waittime)
        return dataacqwritecheck #if negative then write failed

    def set_VME_globalmode(self): #setting the global mode settings
        #convert everything to binary
        buffopt = np.binary_repr(self.bufferLength,width=3)
        bufferbounds = str(self.bool_to_num(self.bufferBounds))
        mixbuffer = str(self.bool_to_num(self.mixedBuffer))
        forcesclrdmp = str(self.bool_to_num(self.forceSclrDmp))
        align = str(self.bool_to_num(self.align32))
        hdroption = str(self.bool_to_num(self.hdrOpt))
        dmpopt = np.binary_repr(self.dmpOpt,width=3)
        busreq = np.binary_repr(self.busReq,width=3)

        settingNum = int(busreq+dmpopt+hdroption+align+forcesclrdmp+mixbuffer+bufferbounds+buffopt,2) #put them all together and convert to one 16 bit number
        glowritecheck = pyxxusb.VME_register_write(self.device,4,settingNum)
        time.sleep(self.waittime)
        return glowritecheck #if negative write failed

    def set_VME_bulktransfer(self): #settings for the bulk read from the VME
        bulkbuffval = np.binary_repr(self.bulkBuffers,width=8) #convert to binary
        bulktimeoutval = np.binary_repr(self.bulkBufferTimeout,width=3)
        bulkNumber = int(bulktimeoutval+bulkbuffval,2) #put them all together and make decimal val
        bulkwritecheck = pyxxusb.VME_register_write(self.device,60,bulkNumber)
        time.sleep(self.waittime)
        return bulkwritecheck #if negative then write failed

    def set_VME_stack(self): #writes the stack to the VME
        stackdata = pyxxusb.new_longArray(len(self.stack)) #array containing the stack info to be written
        for i in range(len(self.stack)):
            pyxxusb.longArray_setitem(stackdata, i, int(self.stack[i])) #load elements into pointer
        stackwritecheck = pyxxusb.xxusb_stack_write(self.device, 2, stackdata) #write the stack
        time.sleep(self.waittime)
        return stackwritecheck #if negative then failed to write

    def setup_VME(self):
        daqVMEcheck = self.set_VME_dataAcq()
        bulkVMEcheck = self.set_VME_bulktransfer()
        gloVMEcheck = self.set_VME_globalmode() #put this one last as 32 bit mode may be turned on
        stackVMEcheck = self.set_VME_stack()
        time.sleep(self.waittime)
        pyxxusb.VME_register_write(self.device,36,1) #number of events per buffer
        time.sleep(self.waittime)
        VMEcheck = np.array([daqVMEcheck,bulkVMEcheck,gloVMEcheck,stackVMEcheck])
        if np.any(VMEcheck < 0):
            return -1
        else:
            return 1

    def DAQ_mode_on(self):
        bytes_written = pyxxusb.xxusb_register_write(self.device, 1, 257)
        return bytes_written

    def DAQ_mode_off(self):
        bytes_written = pyxxusb.xxusb_register_write(self.device, 1, 0)
        return bytes_written

    ######################
    ######################
    ###Other Functions###

    def bool_to_num(self,s):
        return 1 if s == "True" else 0

    def parse_file(self,keyName,textInfo): #parse the file for the given settings and find the info after to be returned
        startindex = re.search(keyName, textInfo).end()
        endindex = re.search("\s", textInfo[startindex:]).start()
        parsedinfo = textInfo[startindex:startindex + endindex]
        return parsedinfo

    def open_config_file(self,fileName):
        settingsFile = open(fileName,'r').read()
        #TDC settings
        self.baseAddress = int(self.parse_file("TDC address = ",settingsFile))
        self.triggerMode = self.parse_file("Trigger mode = ",settingsFile)
        self.offset = int(self.parse_file("Offset = ",settingsFile))
        self.window = float(self.parse_file("Window = ",settingsFile))
        self.reject = float(self.parse_file("Reject margin = ",settingsFile))
        channels = self.parse_file("Channels = ",settingsFile)
        self.channels = np.array([int(i) for i in channels.split(',')])
        self.tdcheaders = self.parse_file("Enable TDC headers = ",settingsFile)
        self.tdcwarnings = self.parse_file("Enable TDC warnings = ",settingsFile)
        self.tdcbypass = self.parse_file("Enable TDC bypass warning = ",settingsFile)
        self.triggersubtract = self.parse_file("Trigger subtraction = ",settingsFile)
        self.extrasearch = float(self.parse_file("Extra search window = ",settingsFile))
        self.resolution = int(self.parse_file("Resolution = ",settingsFile))

        #VME settings
        self.triggerdelay = int(self.parse_file("Trigger delay read = ",settingsFile))
        stack = self.parse_file("Stack = ", settingsFile)
        self.stack = np.array([int(i) for i in stack.split(',')])
        self.scalerreadfrequency = int(self.parse_file("Scaler readout frequency = ",settingsFile))
        self.scalerreadperiod = int(self.parse_file("Scaler readout period = ",settingsFile))
        self.bufferLength = int(self.parse_file('Buffer size = ',settingsFile))
        self.bufferBounds = self.parse_file('Buffer bounds = ',settingsFile)
        self.mixedBuffer = self.parse_file('Mixed buffer = ',settingsFile)
        self.forceSclrDmp = self.parse_file('Force scaler dump = ',settingsFile)
        self.align32 = self.parse_file('Align32 = ',settingsFile)
        self.hdrOpt = self.parse_file('Header output = ',settingsFile)
        self.dmpOpt = int(self.parse_file('Timed buffer dump = ',settingsFile))
        self.busReq = int(self.parse_file('Bus request option = ',settingsFile))
        self.bulkBuffers = int(self.parse_file('Bulk buffers = ',settingsFile))
        self.bulkBufferTimeout = int(self.parse_file('Bulk buffer timeout = ',settingsFile))
        return

#setup = DAQSetting(pyxxusb.xxusb_serial_open('VM0353'),'configSetup.txt')
#setup.setup_TDC()
#setup.setup_VME()