import sys
import os
import plotly.express as pltex
import numpy as np
from tkinter import *
import time
global deviceID
deviceID = ''
from pyxxusb import pyxxusb
import infoVME
import customtkinter

master = Tk()
master.title('VME DAQ')
canva = Canvas(master, width = 1400,height=700)
canva.pack()

class main_DAQ:
    def __int__(self,canvas):
        self.canvas = canvas
        self.runningDAQ = False
        self.devID = ''
        self.connectedText = self.canvas.create_text(100,100,anchor='se')
        self.canvas.item_configure(self.connectedText,text='Not Connected')
        self.canvas.bind("<Button-1>",self.connect_func)

    def connect_func(self):
        self.devID = pyxxusb.xxusb_serial_open('VM0353')
        time.sleep(1)
        self.canvas.item_configure(self.connectedText,background='green',text = str(self.devID))
        #connectedText.configure(background='green')
        #connectedText.update()
        #connectedText.delete("1.0", END)
        #connectedText.insert(END, str(deviceID))

    def disconnect_func(self):
        pyxxusb.xxusb_device_close(self.devID)
        time.sleep(1)
        self.devID = ''
        self.canvas.item_configure(self.connectedText, background='red', text='Not Connected')
        #connectedText.configure(background='red')
        #connectedText.delete("1.0", END)
        #connectedText.insert(END, 'Not Connected to device')
        #connectedText.update()

    def stop_func(self):  # stop read TDC
        self.drain_FIFO()
        self.DAQ_mode_off()
        self.drain_FIFO()
        self.canvas.item_configure(self.runningText,background='red',text='DAQ Stopped')
        #runningText.configure(background='red')
        #runningText.update()
        #runningText.delete("1.0", END)
        #runningText.insert(END, 'DAQ is not running')

    def start_func(self):  # start/run read TDC
        self.canvas.item_configure(self.runningText,background='green',text='DAQ is running')
        #runningText.configure(background='green')
        #runningText.update()
        #runningText.delete("1.0", END)
        self.DAQ_mode_on()
        time.sleep(0.1)
        finalOut = []
        for i in [1]:
            final = read_buffer()
            finalOut.append(final)
        finalOut = np.array([finalOut[i] + finalOut[i + 1] for i in np.arange(0, len(finalOut), 2)])
        dataOut = np.array([])
        for i in range(len(finalOut)):
            if finalOut[i][:5] == '00000':
                dataOut = np.append(dataOut, finalOut[i])a
        channel = np.array([infoVME.basicFunctions.binaryToDecimal(dataOut[i][6:11]) for i in range(len(dataOut))])
        measure = np.array([25 * infoVME.basicFunctions.binaryToDecimal(dataOut[i][11:]) for i in range(len(dataOut))])
        plotdata0 = np.array([])
        plotdata1 = np.array([])
        for i in range(len(dataOut)):
            if channel[i] == 0:
                plotdata0 = np.append(plotdata0, measure[i] / 1000000)
            elif channel[i] == 1:
                plotdata1 = np.append(plotdata1, measure[i] / 1000000)
        fig = pltex.histogram(x=plotdata0, labels={'x': 'microseconds', 'y': 'counts'})
        fig.add_histogram(x=plotdata1)
        fig.show()
        np.savetxt('dataout.txt', finalOut, fmt="%s")
    

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

mainfunction = main_DAQ(canva)
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
