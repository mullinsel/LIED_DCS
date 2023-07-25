import sys
import os
import plotly.express as pltex
import numpy as np
from tkinter import *
import time
from pyxxusb import pyxxusb
import infoVME
import customtkinter

class main_DAQ:
    def __init__(self,master):
        master.title("DAQ GUI")
        master.config(height=700,width=1000,background='grey')
        self.master = master
        self.runningDAQ = False
        self.devID = ''
        self.connectedText = Text(master,height=2,width = 20,background='red')
        self.connectedText.insert(END,'Not Connected to device')
        self.connectedText.place(x=20,y=20)
        self.connectedText.config(state=DISABLED)
        self.runningText = Text(master,height=2,width=20,background='red')
        self.runningText.insert(END,'DAQ Not Running')
        self.runningText.place(x=20,y=60)
        self.runningText.config(state=DISABLED)
        Label(master,text='Save Directory',font=30).place(x=20,y=580)
        self.saveDirectory = Entry(master)
        self.saveDirectory.insert(END,'test.txt')
        self.saveDirectory.place(x=20,y=600)
        self.startButton = Button(master,text='Start',command=self.start_func,height=2,width=10)
        self.startButton.place(x=200,y=60)
        self.stopButton = Button(master,text="Stop",command=self.stop_func,height=2,width=10)
        self.stopButton.place(x=300,y=60)
        self.connectButton=Button(master,text="Connect",command=self.connect_func,height=2,width=10)
        self.connectButton.place(x=200,y=20)
        self.disconnectButton = Button(master,text='Disconnect',command=self.disconnect_func,height=2,width=10)
        self.disconnectButton.place(x=300,y=20)
        Label(master,text='Settings',font=30,background='white').place(x=805,y=20)
        Label(master,text='Trigger Offset').place(x=805,y=180)
        self.triggerOffset = Entry(master)
        self.triggerOffset.insert(END,'0xF800')
        self.triggerOffset.place(x=755,y=200)
        Label(master,text='Window Width').place(x=805,y=230)
        self.windowWidth = Entry(master)
        self.windowWidth.insert(END,'0x0800')
        self.windowWidth.place(x=755,y=250)
        Label(master,text='Reject Window').place(x=805,y=280)
        self.rejectWindow = Entry(master)
        self.rejectWindow.insert(END,'0x01')
        self.rejectWindow.place(x=755,y=300)
        self.writeSettings = Button(master,text="Write Settings",command=self.setup_config,height=2,width=10)
        self.writeSettings.place(x=800,y=400)
        Label(master,text='Errors',font=30).place(x=805,y=500)
        self.errorText = Text(master,width=30,height=10)
        self.errorText.insert(END,"No Errors Yet")
        self.errorText.place(x=705,y=525)
        self.settingsStatus = Text(master,background='red',height=2,width=20)
        self.settingsStatus.insert(END,'Settings Unwritten')
        self.settingsStatus.place(x=750,y=360)
        self.settingsStatus.config(state=DISABLED)
        Label(master,text='Runtime Set',font=30).place(x=20,y=130)
        self.runTime = Entry(master)
        self.runTime.insert(END,'10')
        self.runTime.place(x=20,y=150)
        Label(master,text='Current Time',font=30).place(x=20,y=170)
        self.currentTimeText = Text(master,height=1,width=15)
        self.currentTimeText.insert(END,'0')
        self.currentTimeText.config(state=DISABLED)
        self.currentTimeText.place(x=20,y=200)

    def stack_DAQ(self):
        stackin = [0x0009, 0x0000, 0x0109, 0x0000, 0x0000, 0x0400] #stack to be written
        stackdata = pyxxusb.new_longArray(len(stackin))
        for i in range(len(stackin)):
            pyxxusb.longArray_setitem(stackdata, i, stackin[i])
        writtencheck = pyxxusb.xxusb_stack_write(self.devID, 2, stackdata)
        if writtencheck < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END,'Stack failed to write')
            self.errorText.config(state=DISABLED)
        #time.sleep(1)
        #stackout = pyxxusb.new_longArray(int(writtencheck))
        #readcheck = pyxxusb.xxusb_stack_read(self.devID, 2, stackout)
        #stackoutdata = []
        #for i in range(int(writtencheck)):
        #    stackoutdata.append(pyxxusb.longArray_getitem(stackout, i))
        #extest = pyxxusb.xxusb_stack_execute(deviceID, stackdata)
        #outtest = []
        #for i in range(int(int(extest) / 2)):
        #    outtest.append(hex(pyxxusb.longArray_getitem(stackdata, i)))
        #readSETUPText.insert(END, " " + str(outtest))
        return

    def setup_config(self):
        writecheck = pyxxusb.VME_register_write(self.devID, 0x8, 0x0) #sets the readout trigger delay
        writecheck2 = pyxxusb.VME_register_write(self.devID, 0x4, 0x40A0) #sets global settings
        writecheck = writecheck + writecheck2
        if writecheck < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ Settings failed to set!')
            self.errorText.config(state=DISABLED)
        self.stack_DAQ()  # writes the stack to the memory
        # setting TDC settings
        self.sendCODE(0x0E, 0x0400102E, 0x0000)  # set mode trigger mode
        self.sendCODE(0x0E, 0x0400102E, 0x3000)  # disable/enable headers for testing
        self.sendCODE(0x0E, 0x0400102E, 0x3500)  # disable/enable error markers
        self.sendCODE(0x0E, 0x0400102E, 0x3700)  # enable error bypass
        self.set_offset(0x0E, 0x0400102E)  # sets offset to -2048 cycles or -82 microseconds (set to -10 microseconds right now)
        self.set_window_width(0x0E, 0x0400102E)  # sets window width to 2048 cycles (7 microseconds now)
        self.set_reject(0x0E, 0x0400102E)  # sets reject margin
        #self.set_offset(0x0E, 0x0400102E, 0xF800)  # sets offset to -2048 cycles or -82 microseconds
        #self.set_window_width(0x0E, 0x0400102E, 0x0800)  # sets window width to 2048 cycles
        #self.set_reject(0x0E, 0x0400102E, 0x01)  # sets reject margin
        self.sendCODE(0x0E, 0x0400102E, 0x1400)  # subtract trigger offset
        self.settingsStatus.config(state='normal')
        self.settingsStatus.delete("1.0",END)
        self.settingsStatus.insert(END,"Settings Written")
        self.settingsStatus.config(background='green')
        self.settingsStatus.update()
        self.settingsStatus.config(state=DISABLED)
        return

    def set_window_width(self,AM, location):
        pyxxusb.VME_write_16(self.devID, AM, location, 0x1000)
        pyxxusb.VME_write_16(self.devID, AM, location,0x0190)
        return

    def set_offset(self,AM, location):
        pyxxusb.VME_write_16(self.devID, AM, location, 0x1100)
        pyxxusb.VME_write_16(self.devID, AM, location, 0xFE70)
        return

    def set_reject(self,AM, location):
        pyxxusb.VME_write_16(self.devID, AM, location, 0x1300)
        pyxxusb.VME_write_16(self.devID, AM, location,0x01)
        return

    def sendCODE(self,AM, location, code):  # functin that writes and reads OPCODE for the TDC
        #listen = pyxxusb.new_longArray(32)
        pyxxusb.VME_write_16(self.devID, AM, location, code)
        # pyxxusb.VME_read_16(deviceID,AM,location,listen)
        return  # pyxxusb.longArray_getitem(listen,0)

    def drain_FIFO(self):  # clears the buffer
        shortData = pyxxusb.new_intArray(8192)
        loop = 0
        bytes_rec = 1
        while bytes_rec > 0 and loop < 100:
            bytes_rec = pyxxusb.xxusb_usbfifo_read(self.devID, shortData, 8192, 1000)
            loop += 1

    def read_buffer(self):  # read whats in the buffer and outputs the array
        readArray = pyxxusb.new_shortArray(8192)
        numberread = pyxxusb.xxusb_bulk_read(self.devID, readArray, 8192, 1000)
        readdata = [np.binary_repr(pyxxusb.shortArray_getitem(readArray, i), width=16) for i in range(int(int(numberread) / 2))]
        readdataOut = np.array([readdata[i+1] + readdata[i] for i in np.arange(0, len(readdata), 2)])
        self.drain_FIFO()
        return readdataOut

    def DAQ_mode_on(self):
        bytes_written = pyxxusb.xxusb_register_write(self.devID, 0x1, int(True))
        if bytes_written < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ mode on write failed')
            self.errorText.config(state=DISABLED)
        else:
            self.runningDAQ = True
        return

    def DAQ_mode_off(self):
        bytes_written = pyxxusb.xxusb_register_write(self.devID, 0x1, int(False))
        if bytes_written < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ mode off write failed')
            self.errorText.config(state=DISABLED)
        else:
            self.runningDAQ = False
        return

    def connect_func(self):
        self.devID = pyxxusb.xxusb_serial_open('VM0353')
        time.sleep(1)
        self.connectedText.config(state='normal')
        self.connectedText.configure(background='green')
        self.connectedText.delete("1.0",END)
        self.connectedText.insert(END,str(self.devID))
        self.connectedText.update()
        self.connectedText.config(state=DISABLED)

    def disconnect_func(self):
        #self.force_reset()
        self.stop_func()
        pyxxusb.xxusb_reset_toggle(self.devID)
        pyxxusb.xxusb_device_close(self.devID)
        time.sleep(1)
        self.devID = ''
        self.connectedText.config(state='normal')
        self.connectedText.configure(background='red')
        self.connectedText.delete("1.0", END)
        self.connectedText.insert(END, 'Not Connected to device')
        self.connectedText.update()
        self.connectedText.config(state=DISABLED)
        self.settingsStatus.config(state='normal')
        self.settingsStatus.delete("1.0",END)
        self.settingsStatus.insert(END,'Settings Unwritten')
        self.settingsStatus.config(background='red')
        self.settingsStatus.update()
        self.settingsStatus.config(state=DISABLED)
        self.runningText.config(state='normal')
        self.runningText.config(background='red')
        self.runningText.delete("1.0",END)
        self.runningText.insert(END,'DAQ Not Running')
        self.runningText.update()
        self.runningText.config(state=DISABLED)

    def stop_func(self):  # stop read TDC
        self.drain_FIFO()
        self.DAQ_mode_off()
        self.drain_FIFO()
        self.runningDAQ = False
        self.runningText.config(state='normal')
        self.runningText.configure(background='red')
        self.runningText.update()
        self.runningText.delete("1.0", END)
        self.runningText.insert(END, 'DAQ is not running')
        self.runningText.config(state=DISABLED)

    def TDC_status(self):
        listen=pyxxusb.new_longArray(32)
        pyxxusb.VME_read_16(self.devID,0x0E,0x0400102C,listen)
        return

    def start_func(self):  # start/run read TDC
        self.runningDAQ=True
        self.runningText.config(state='normal')
        self.runningText.configure(background='green')
        self.runningText.delete("1.0", END)
        self.runningText.insert(END,'DAQ is running')
        self.runningText.update()
        self.runningText.config(state=DISABLED)
        self.DAQ_mode_on()
        time.sleep(0.1)
        self.drain_FIFO()
        time.sleep(0.1)
        finalOutData = self.read_buffer()
        self.drain_FIFO()
        time.sleep(0.1)
        finalOutData = np.append(finalOutData,self.read_buffer())
        self.drain_FIFO()
        time.sleep(0.1)
        finalOutData = np.append(finalOutData,self.read_buffer())
        self.loopTime = int(self.runTime.get())
        self.stop_func()
        print(finalOutData[:50])
        #np.savetxt(self.saveDirectory.get(), finalOutData, fmt="%s")
        #splitlocations = np.where(finalOutData=='1010101111001101')[0]
        #print(splitlocations)
        #for i in range(len(splitlocations)-1):
        #    print(finalOutData[splitlocations[i]:splitlocations[i+1]])
        plotdata1 = np.array([])
        plotdata0 = np.array([])
        tdcdata = np.array([])
        headerglobal = np.array([])
        trailerglobal = np.array([])
        gtt = np.array([])
        for i in range(len(finalOutData)):
            if str(finalOutData[i][:2])=='00':
                tdcdata = np.append(tdcdata, finalOutData[i])
            if str(finalOutData[i][:5]) == '01000':
                headerglobal = np.append(headerglobal,finalOutData[i])
            if str(finalOutData[i][:5]) == '10000':
                trailerglobal = np.append(trailerglobal,finalOutData[i])
            if str(finalOutData[i][:5]) == '10001':
                gtt = np.append(gtt, finalOutData[i])
        tdcheader = np.array([])
        tdcmeasured = np.array([])
        tdcerror = np.array([])
        tdctrailer = np.array([])
        for i in range(len(tdcdata)):
            if str(tdcdata[i][:5]) == '00001':
                tdcheader = np.append(tdcheader,tdcdata[i])
            if str(tdcdata[i][:5]) == '00000' and str(tdcdata[i]) != '00000000000000000000000000000011':
                tdcmeasured = np.append(tdcmeasured,tdcdata[i])
            if str(tdcdata[i][:5]) == '00100':
                tdcerror = np.append(tdcerror, tdcdata[i])
            if str(tdcdata[i][:5]) == '00011':
                tdctrailer = np.append(tdctrailer,tdcdata[i])
        headerevent = [int(i[5:27],2) for i in headerglobal]
        headergeo = [int(i[27:],2) for i in headerglobal]
        channel = np.array([int((tdcmeasured[i][6:11]),2) for i in range(len(tdcmeasured))]) #6:11
        measure = np.array([25*int(tdcmeasured[i][11:],2)/1000000 for i in range(len(tdcmeasured))]) #11:
        for i in range(len(tdcmeasured)):
            if channel[i]==0:
                plotdata0 = np.append(plotdata0,measure[i])
            elif channel[i]==1:
                plotdata1 = np.append(plotdata1,measure[i])
        #print(measure[:100])
        #print(channel[:100])
        #print(len(tdcmeasured)/len(finalOutData))
        print('channels')
        print(channel[:100])
        zerolocations = np.where(channel==0)[0]
        print(zerolocations[:50])
        difference=np.array([])
        for i in np.arange(0,len(zerolocations)-1):
            datapoints = np.abs((zerolocations[i+1]-zerolocations[i])-1)
            reference = measure[zerolocations[i]]
            for j in range(datapoints):
                hitdiff = -reference+measure[int(zerolocations[i]+1+j)]
                if hitdiff >=.001 and hitdiff <=5:
                    difference = np.append(difference,hitdiff)
        print(np.count_nonzero((difference>=0.001) & (difference<=1.0)))
        print(np.count_nonzero((difference >= 1.0) & (difference <= 2.0)))
        print(np.count_nonzero((difference >= 2.5) & (difference <= 3.5)))
        fig = pltex.histogram(x=difference,nbins=10000,labels={'x': 'microseconds', 'y': 'counts'},range_x=[0,5])
        fig.show()
        fig2 = pltex.scatter(x=np.arange(0,len(difference)),y=difference)
        fig2.show()
        np.savetxt(self.saveDirectory.get(), finalOutData, fmt="%s")

'''
def setup_config():
    global deviceID
    #DAQsettingsin = [0x0000,0x0101]
    #DAQsettingsarr = pyxxusb.new_longArray(2)
    #pyxxusb.longArray_setitem(DAQsettingsarr,0,0x64)
    #pyxxusb.longArray_setitem(DAQsettingsarr, 1, 0x0101)
    #for i in range(len(DAQsettingsin)):
    #    pyxxusb.longArray_setitem(DAQsettingsarr,0,DAQsettingsin[0])
    #pyxxusb.longArray_setitem(DAQsettingsarr,i,DAQsettingsin[i])
    #writes the DAQ settings (trigger delay)
    writecheck = pyxxusb.VME_register_write(deviceID,8,0x2)
    DAQcheck = pyxxusb.new_longArray(1)
    readcheck = pyxxusb.VME_register_read(deviceID,8,DAQcheck)
    readDAQSETTINGSText.delete("1.0",END)
    #readDAQSETTINGSText.insert(END,str(writecheck))
    #readDAQSETTINGSText.insert(END,str(readcheck))
    if writecheck < 0:
        readDAQSETTINGSText.insert(END,str('DAQ Settings failed to set!'))
    else:
        readDAQSETTINGSText.insert(END, str('DAQ Settings set correctly!'))
        
    stack_DAQ() #writes the stack to the memory

    #setting TDC settings
    sendCODE(0x0E,0x0400102E,0x3100) #disable/enable headers for testing
    sendCODE(0x0E,0x0400102E,0x3600) #disable/enable error markers
    sendCODE(0x0E,0x0400102E,0x0000) #set mode
    #sendCODE(0x0E,0x0400102E,0x0300) #sets keep token
    set_offset(0x0E,0x0400102E,0xF800) #sets offset to -2048 cycles or -82 microseconds
    set_window_width(0x0E,0x0400102E,0x0800) #sets window width to 2048 cycles
    set_reject(0x0E,0x0400102E,0x01) #sets reject margin
    sendCODE(0x0E,0x0400102E,0x1400) #subtract trigger offset
    #pyxxusb.VME_write_16(deviceID, 0x0E, 0x04001000, 0x0028) #enables empty event to be placed in buffer
    return

def stack_DAQ():
    global deviceID
    stackin = [0x0005,0x0000,0x0109,0x0000,0x0000,0x0400]
    stackdata = pyxxusb.new_longArray(len(stackin))
    for i in range(len(stackin)):
        pyxxusb.longArray_setitem(stackdata,i,stackin[i])
    time.sleep(1)
    writtencheck = pyxxusb.xxusb_stack_write(deviceID,2,stackdata)
    time.sleep(1)
    stackout = pyxxusb.new_longArray(int(writtencheck))
    readcheck = pyxxusb.xxusb_stack_read(deviceID,2,stackout)
    stackoutdata = []
    for i in range(int(writtencheck)):
        stackoutdata.append(pyxxusb.longArray_getitem(stackout,i))
    readSETUPText.delete("1.0",END)
    #readSETUPText.insert(END,str(writtencheck)+" ")
    #readSETUPText.insert(END,str(readcheck)+" ")
    #readSETUPText.insert(END,str(stackoutdata[:6]))
    extest = pyxxusb.xxusb_stack_execute(deviceID,stackdata)
    #readSETUPText.insert(END," "+str(extest))
    outtest = []
    for i in range(int(int(extest)/2)):
        outtest.append(hex(pyxxusb.longArray_getitem(stackdata,i)))
    readSETUPText.insert(END," "+str(outtest))
    return

def DAQ_mode_on():
    global deviceID
    global runningDAQ

    readDAQText.delete("1.0",END)
    bytes_written = pyxxusb.xxusb_register_write(deviceID,1,int(True))
    if bytes_written < 0:
        readDAQText.insert(END,'DAQ mode write failed')
    else:
        readDAQText.insert(END,'DAQ mode set to ON')
        runningDAQ=True
    return

def DAQ_mode_off():
    global deviceID
    global runningDAQ
    readDAQText.delete("1.0",END)
    bytes_written = pyxxusb.xxusb_register_write(deviceID,1,int(False))
    if bytes_written < 0:
        readDAQText.insert(END,'DAQ mode write failed')
    else:
        readDAQText.insert(END,'DAQ mode set to OFF')
        runningDAQ = False
    return

def stream_read():
    global deviceID
    bufferRead = pyxxusb.new_longArray(8192)
    bytes_written = pyxxusb.xxusb_usbfifo_read(deviceID,bufferRead,8192,100)
    for i in range(8190):
        readBufferText.insert(END,str(pyxxusb.shortArray_getitem(bufferRead,i)))
    if bytes_written < 0:
        readBufferText.insert(END,'DAQ mode write failed')

def readID_func():
    global deviceID
    readText.delete("1.0",END)
    dataread = pyxxusb.new_longArray(40)
    pyxxusb.VME_register_read(deviceID,0,dataread)
    firmwareID = pyxxusb.long_p_value(dataread)
    readText.insert(END,str(hex(firmwareID)))
    return

def readGlobal_func():
    global deviceID
    readGlobalText.delete("1.0",END)
    datareadglobal = pyxxusb.new_longArray(33)
    pyxxusb.VME_register_read(deviceID,4,datareadglobal)
    globalInfo = pyxxusb.long_p_value(datareadglobal)
    #globalInfo = globalInfo[2:18]
    readGlobalText.insert(END,str(hex(globalInfo)))
    return

def readDAQ_settings():
    global deviceID
    readDAQsettingsText.delete("1.0", END)
    dataDaqSettings = pyxxusb.new_longArray(33)
    pyxxusb.VME_register_read(deviceID,8,dataDaqSettings)
    settingsInfo = pyxxusb.long_p_value(dataDaqSettings)
    readDAQsettingsText.insert(END, str(hex(settingsInfo)))
    return

def connect_func():
    global deviceID
    deviceID = pyxxusb.xxusb_serial_open('VM0353')
    time.sleep(2)
    connectedText.configure(background='green')
    connectedText.update()
    connectedText.delete("1.0",END)
    connectedText.insert(END,str(deviceID))
    return

def disconnect_func():
    global deviceID
    pyxxusb.xxusb_device_close(deviceID)
    time.sleep(2)
    connectedText.configure(background='red')
    connectedText.update()
    deviceID = ''
    connectedText.delete("1.0",END)
    connectedText.insert(END,'Not Connected to device')
    return

def drain_FIFO(): #clears the buffer
    global deviceID
    shortData = pyxxusb.new_intArray(8192)
    loop = 0
    bytes_rec = 1
    while bytes_rec > 0 and loop < 100:
        bytes_rec = pyxxusb.xxusb_usbfifo_read(deviceID,shortData,8192,1000)
        loop += 1

def read_buffer(): #read whats in the buffer and outputs the array
    global deviceID
    testread = pyxxusb.new_shortArray(8192)
    numberread = pyxxusb.xxusb_bulk_read(deviceID, testread, 8192, 1000)
    runningText.insert(END, str(numberread))
    readdata = [np.binary_repr(pyxxusb.shortArray_getitem(testread, i),width=16) for i in range(int(int(numberread) / 2))]
    runningText.insert(END, str(readdata))
    drain_FIFO()
    return readdata

def sendCODE(AM,location,code): #functin that writes and reads OPCODE for the TDC
    global deviceID
    listen = pyxxusb.new_longArray(32)
    pyxxusb.VME_write_16(deviceID,AM,location,code)
    #pyxxusb.VME_read_16(deviceID,AM,location,listen)
    return #pyxxusb.longArray_getitem(listen,0)

def set_window_width(AM,location,width):
    global deviceID
    pyxxusb.VME_write_16(deviceID,AM,location,0x1000)
    pyxxusb.VME_write_16(deviceID,AM,location,width)
    return

def set_offset(AM,location,offset):
    global deviceID
    pyxxusb.VME_write_16(deviceID,AM,location,0x1100)
    pyxxusb.VME_write_16(deviceID,AM,location,offset)
    return

def set_reject(AM,location,reject):
    global deviceID
    pyxxusb.VME_write_16(deviceID,AM,location,0x1300)
    pyxxusb.VME_write_16(deviceID,AM,location,reject)
    return

def start_func(): #start/run read TDC
    global deviceID
    global runningDAQ
    runningText.configure(background='green')
    runningText.update()
    runningText.delete("1.0",END)
    DAQ_mode_on()
    time.sleep(0.1)
    finalOut = []
    for i in [1]:
        final = read_buffer()
        finalOut.append(final)
    #finalOut = flatten(finalOut)
    finalOut = np.array([finalOut[i]+finalOut[i+1] for i in np.arange(0,len(finalOut),2)])
    dataOut = np.array([])
    for i in range(len(finalOut)):
        if finalOut[i][:5]=='00000':
            dataOut = np.append(dataOut,finalOut[i])
    channel = np.array([infoVME.basicFunctions.binaryToDecimal(dataOut[i][6:11]) for i in range(len(dataOut))])
    #count = np.array([infoVME.basicFunctions.binaryToDecimal(finalOut[i][5:27]) for i in range(len(finalOut))])
    measure = np.array([25*infoVME.basicFunctions.binaryToDecimal(dataOut[i][11:]) for i in range(len(dataOut))])
    plotdata0 = np.array([])
    plotdata1 = np.array([])
    for i in range(len(dataOut)):
        if channel[i]==0:
            plotdata0 = np.append(plotdata0,measure[i]/1000000)
        elif channel[i]==1:
            plotdata1 = np.append(plotdata1,measure[i]/1000000)
    fig = pltex.histogram(x=plotdata0,labels={'x':'microseconds','y':'counts'})
    fig.add_histogram(x=plotdata1)
    fig.show()
    #print(channel[:100])
    #print(count[:30])
    #print(measure[:100])
    np.savetxt('dataout.txt',finalOut,fmt="%s")
    #np.savetxt('nothing.txt',nothing,fmt="%s")
    return

def stop_func(): #stop read TDC
    global runningDAQ
    drain_FIFO()
    DAQ_mode_off()
    drain_FIFO()
    drain_FIFO()
    runningText.configure(background='red')
    runningText.update()
    runningText.delete("1.0",END)
    runningText.insert(END,'DAQ is not running')
    return


#BUTTONS
#Right side
buttonStart = Button(master,text='Start', width = 25,command=start_func)
buttonStart.place(x=1200,y=10)
buttonStop = Button(master,text='Stop', width = 25,command=stop_func)
buttonStop.place(x=1200,y=50)
buttonConnect = Button(master,text='Connect', width = 25,command=connect_func)
buttonConnect.place(x=1200,y=90)
buttonDisconnect = Button(master,text='Disconnect',width = 25,command=disconnect_func)
buttonDisconnect.place(x=1200,y=130)
#Left Side
buttonDAQSettings = Button(master,text='Read DAQ Settings', width = 25,command=readDAQ_settings)
buttonDAQSettings.place(x=300,y=130)
buttonRead = Button(master,text='Read ID', width = 25,command=readID_func)
buttonRead.place(x=300,y=90)
buttonReadGlobal = Button(master,text='Read Global', width = 25,command=readGlobal_func)
buttonReadGlobal.place(x=300,y=50)
buttonReadGlobal = Button(master,text='DAQ Mode On', width = 25,command=DAQ_mode_on)
buttonReadGlobal.place(x=300,y=10)
buttonReadGlobal = Button(master,text='DAQ Mode Off', width = 25,command=DAQ_mode_off)
buttonReadGlobal.place(x=600,y=10)
buttonSETUP = Button(master,text='stack',width = 25, command=stack_DAQ)
buttonSETUP.place(x=300,y=210)
buttonSettings = Button(master,text='setup config',width = 25, command=setup_config)
buttonSettings.place(x=300,y=250)
#DISPLAY TEXT
#Right side
connectedText = Text(master,height=2,width=30,background='red')
connectedText.place(x=900, y=90)
connectedText.insert(END,'Not Connected to device')
runningText = Text(master,height=4,width=30,background='red')
runningText.place(x=900,y=10)
runningText.insert(END,'DAQ is not running')
#Left side
readText = Text(master,height=2,width=30)
readText.place(x=10,y=90)
readText.insert(END,'data')
readGlobalText = Text(master,height=2,width=30)
readGlobalText.place(x=10,y=50)
readGlobalText.insert(END,'Global mode data')
readDAQText = Text(master,height=2,width=30)
readDAQText.place(x=10,y=10)
readDAQText.insert(END,'DAQ mode data')
readDAQsettingsText = Text(master,height=2,width=30)
readDAQsettingsText.place(x=10,y=130)
readDAQsettingsText.insert(END,'DAQ settings')
readSETUPText = Text(master,height=2,width=30)
readSETUPText.place(x=10,y=210)
readSETUPText.insert(END,'SETUP DAQ info')
readDAQSETTINGSText = Text(master,height=2,width=30)
readDAQSETTINGSText.place(x=10,y=250)
readDAQSETTINGSText.insert(END,'Settings DAQ info')

#INPUT BOXES
tdcAddress = Entry(master)
tdcAddress.place(x=10,y=400)
saveDirectory = Entry(master)
saveDirectory.place(x=10,y=450)


#LABELS
tdcLabel = Label(master,text = 'tdc Address (0x4000000)')
tdcLabel.place(x=10,y=375)
saveLabel = Label(master,text = 'Save Path')
saveLabel.place(x=10,y=425)
'''

root = Tk()
my_gui = main_DAQ(root)
root.mainloop()

#data = pyxxusb.new_longArray(1)
#globaldata = pyxxusb.new_longArray(1)
#daqsettings = pyxxusb.new_longArray(1)
#time.sleep(3)s
#print(pyxxusb.VME_register_read(crate,0,data))
#firmwareID = decimalToBinary(pyxxusb.long_p_value(data))
#print(firmwareID_read(firmwareID))
#pyxxusb.VME_register_read(crate,4,globaldata)
#globalRegister = decimalToBinary(pyxxusb.long_p_value(globaldata))
#print(globalMode_read(globalRegister))
#pyxxusb.VME_register_read(crate,8,daqsettings)
#print(pyxxusb.long_p_value(daqsettings))
#daqSettings = decimalToBinary(pyxxusb.long_p_value(daqsettings))
#print(DAQsettings_read(str(daqsettings)))
