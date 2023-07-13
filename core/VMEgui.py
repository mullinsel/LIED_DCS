import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
sys.path.insert(0,'C:\\Users\cbonline\Documents\CC_TDC-main\interface\\')
#from my_client import MyClient
import time
global deviceID
from pyxxusb import pyxxusb
import infoVME

#pyxxusblib = MyClient()
deviceID = ''

def read_buffer():
    global deviceID
    readBufferText.delete("1.0",END)
    bufferRead = pyxxusb.new_longArray(1)
    bytes_written = pyxxusb.xxusb_bulk_read(deviceID,bufferread,8192,100)
    readBufferText.insert(END,str(pyxxusb.long_p_value(bufferRead)))
    if bytes_written <0:
        readBufferText.insert(END,'DAQ mode write failed')
    return

def DAQ_mode():
    global deviceID
    readDAQText.delete("1.0",END)
    bytes_written = pyxxusb.xxusb_register_write(deviceID,1,int(True))
    if bytes_written <0:
        readDAQText.insert(END,'DAQ mode write failed')
    else:
        readDAQText.insert(END,'DAQ mode set')
    return

def readID_func():
    global deviceID
    readText.delete("1.0",END)
    dataread = pyxxusb.new_longArray(1)
    pyxxusb.VME_register_read(deviceID,0,dataread)
    firmwareID = decimalToBinary(pyxxusb.long_p_value(dataread))
    readText.insert(END,str(firmwareID_read(firmwareID)))
    return

def readGlobal_func():
    global deviceID
    readGlobalText.delete("1.0",END)
    datareadglobal = pyxxusb.new_longArray(1)
    pyxxusb.VME_register_read(deviceID,4,datareadglobal)
    globalInfo = decimalToBinary(pyxxusb.long_p_value(datareadglobal))
    readGlobalText.insert(END,str(globalMode_read(globalInfo)))
    return

def connect_func():
    global deviceID
    deviceID = pyxxusb.xxusb_serial_open('VM0353')
    time.sleep(2)
    connectedText.configure(background='green')
    connectedText.update()
    connectedText.delete("1.0",END)
    connectedText.insert(END,'Connected to device')
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

def start_func():
    runningText.configure(background='green')
    runningText.update()
    runningText.delete("1.0",END)
    runningText.insert(END,'DAQ is running')
    return

def stop_func():
    runningText.configure(background='red')
    runningText.update()
    runningText.delete("1.0",END)
    runningText.insert(END,'DAQ is not running')
    return

def decimalToBinary(n):
    return bin(n).replace("0b", "")

def binaryToDecimal(n):
    return int(n,2)

def firmwareID_read(binary_read):
    while len(binary_read)!= 32:
        binary_read = ''.join(('0',binary_read))
    month = binaryToDecimal(binary_read[:4])
    year = binaryToDecimal(binary_read[4:8])
    deviceID = binaryToDecimal(binary_read[8:12])
    betaVersion = binaryToDecimal(binary_read[12:16])
    majorRev = binaryToDecimal(binary_read[16:24])
    minorRev = binaryToDecimal(binary_read[24:])
    return month,year,deviceID,betaVersion,majorRev,minorRev

def globalMode_read(binary_read):
    binary_read = binary_read[:16]
    while len(binary_read)!= 16:
        binary_read = ''.join(('0',binary_read))
    extra = binaryToDecimal(binary_read[15])
    buffOpt = binaryToDecimal(binary_read[0:4])
    mixtBuff = int(binary_read[4])
    FrceSclrDmp = int(binary_read[5])
    align32 = int(binary_read[6])
    HdrOpt = int(binary_read[7])
    DmpOpt = binaryToDecimal(binary_read[8:11])
    BusReq = binaryToDecimal(binary_read[11:14])
    return buffOpt,mixtBuff,FrceSclrDmp,align32,HdrOpt,DmpOpt,BusReq

def DAQsettings_read(binary_read):
    while len(binary_read)!= 32:
        binary_read = ''.join(('0',binary_read))
    scalerReadoutFreq = binaryToDecimal(binary_read[:16])
    scalerReadoutPeriod = binaryToDecimal(binary_read[16:24])
    readoutTriggerDelay = binaryToDecimal(binary_read[24:])
    return scalerReadoutFreq,scalerReadoutPeriod,readoutTriggerDelay

master = Tk()
master.title('VME DAQ')
canva = Canvas(master, width = 1400,height=700)
canva.pack()
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
buttonBufferRead = Button(master,text='Read Buffer', width = 25,command=read_buffer)
buttonBufferRead.place(x=300,y=130)
buttonRead = Button(master,text='Read ID', width = 25,command=readID_func)
buttonRead.place(x=300,y=90)
buttonReadGlobal = Button(master,text='Read Global', width = 25,command=readGlobal_func)
buttonReadGlobal.place(x=300,y=50)
buttonReadGlobal = Button(master,text='DAQ Mode', width = 25,command=DAQ_mode)
buttonReadGlobal.place(x=300,y=10)

#DISPLAY TEXT
#Right side
connectedText = Text(master,height=2,width=30,background='red')
connectedText.place(x=900, y=90)
connectedText.insert(END,'Not Connected to device')
runningText = Text(master,height=2,width=30,background='red')
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
readBufferText = Text(master,height=2,width=30)
readBufferText.place(x=10,y=130)
readBufferText.insert(END,'DAQ mode data')


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

master.mainloop()

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
