import sys
import os
import plotly.express as pltex
import numpy as np
from tkinter import *
import time
from pyxxusb import pyxxusb
#import infoVME
import customtkinter

customtkinter.set_default_color_theme("C:\\Users\cbonline\PycharmProjects\LIED_DCS\custom-tktheme.json")
class main_DAQ:
    def __init__(self,master):
        master.title("DAQ GUI") #set window title
        master.config(height=700,width=1000)
        #master.protocol("WM_DELETE_WINDOW",self.close_window)
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
        customtkinter.CTkLabel(master,text='Save Directory',font=('Helvetica',30)).place(x=20,y=550)
        self.saveDirectory = Entry(master)
        self.saveDirectory.insert(END,'test.txt')
        self.saveDirectory.place(x=20,y=600)
        self.startButton = customtkinter.CTkButton(master,text='Start',command=self.start_func,height=40,width=80)
        self.startButton.place(x=200,y=60)
        self.stopButton = customtkinter.CTkButton(master,text="Stop",command=self.stop_func,height=40,width=80)
        self.stopButton.place(x=300,y=60)
        self.connectButton = customtkinter.CTkButton(master,text="Connect",command=self.connect_func,height=40,width=80)
        self.connectButton.place(x=200,y=20)
        self.disconnectButton = customtkinter.CTkButton(master,text='Disconnect',command=self.disconnect_func,height=40,width=80)
        self.disconnectButton.place(x=300,y=20)
        customtkinter.CTkLabel(master,text='Settings',font=('Helvetica',30)).place(x=800,y=20)
        #Label(master,text='Trigger Offset').place(x=805,y=180)
        #self.triggerOffset = Entry(master)
        #self.triggerOffset.insert(END,'0xF800')
        #self.triggerOffset.place(x=755,y=200)
        #Label(master,text='Window Width').place(x=805,y=230)
        #self.windowWidth = Entry(master)
        #self.windowWidth.insert(END,'0x0800')
        #self.windowWidth.place(x=755,y=250)
        #Label(master,text='Reject Window').place(x=805,y=280)
        #self.rejectWindow = Entry(master)
        #self.rejectWindow.insert(END,'0x01')
        #self.rejectWindow.place(x=755,y=300)
        self.writeSettings = customtkinter.CTkButton(master,text="Write Settings",command=self.setup_config,height=40,width=80)
        self.writeSettings.place(x=800,y=400)
        customtkinter.CTkLabel(master,text='Errors',font=('Helvetica',30)).place(x=800,y=480)
        self.errorText = Text(master,width=30,height=10)
        self.errorText.insert(END,"No Errors Yet")
        self.errorText.place(x=705,y=525)
        self.settingsStatus = Text(master,background='red',height=2,width=20)
        self.settingsStatus.insert(END,'Settings Unwritten')
        self.settingsStatus.place(x=750,y=360)
        self.settingsStatus.config(state=DISABLED)
        #Label(master,text='Runtime Set',font=30).place(x=20,y=130)
        #self.runTime = Entry(master)
        #self.runTime.insert(END,'10')
        #self.runTime.place(x=20,y=150)
        #Label(master,text='Current Time',font=30).place(x=20,y=170)
        #self.currentTimeText = Text(master,height=1,width=15)
        #self.currentTimeText.insert(END,'0')
        #self.currentTimeText.config(state=DISABLED)
        #self.currentTimeText.place(x=20,y=200)

    def close_window(self):
        self.stop_func()
        self.disconnect_func()
        self.master.destroy()
        return

    def stack_DAQ(self):
        stackin = [0x0005, 0x0000, 0x0109, 0x0000, 0x0000, 0x0400] #stack to be written
        stackdata = pyxxusb.new_longArray(len(stackin)) #array containing the stack info to be written
        for i in range(len(stackin)):
            pyxxusb.longArray_setitem(stackdata, i, stackin[i])
        writtencheck = pyxxusb.xxusb_stack_write(self.devID, 2, stackdata)
        if writtencheck < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END,'Stack failed to write')
            self.errorText.config(state=DISABLED)
        return

    def setup_config(self):
        self.stack_DAQ()
        #VME settings
        time.sleep(1)
        writecheck = 2 #pyxxusb.VME_register_write(self.devID, 0x8, 0x0) #sets the readout trigger delay
        time.sleep(1)
        writecheck2 = 2#pyxxusb.VME_register_write(self.devID,0x4, 0x01B0)
        time.sleep(1)
        #print(writecheck2)
        bulkset = pyxxusb.VME_register_write(self.devID, 0x3C, 0x0000FFFF)
        #print(bulkset)
        if writecheck < 0 or writecheck2 < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ Settings failed to set!')
            self.errorText.config(state=DISABLED)

        # setting TDC settings
        #self.sendCODE(0x0E, 0x0400102E, 0x3100)  # disable/enable headers for testing
        #self.sendCODE(0x0E, 0x0400102E, 0x3600)  # disable/enable error markers
        #self.sendCODE(0x0E, 0x0400102E, 0x3700)  # enable error bypass
        #pyxxusb.VME_write_16(self.devID,0x0E,0x0400102E,0x1500)
        #self.set_offset(0x0E, 0x0400102E, 0xFE70)  # sets offset to -400 cycles or -10 microseconds
        time.sleep(1)
        pyxxusb.VME_write_16(self.devID,0x0E,0x0400102E,0x1100)
        time.sleep(1)
        pyxxusb.VME_write_16(self.devID,0x0E,0x0400102E,-400)
        time.sleep(1)
        pyxxusb.VME_write_16(self.devID,0x0E,0x0400102E,0x1000)
        time.sleep(1)
        pyxxusb.VME_write_16(self.devID,0x0E,0x0400102E,200)
        time.sleep(1)
        pyxxusb.VME_write_16(self.devID,0x0E,0x0400102E,0x1300)
        time.sleep(1)
        pyxxusb.VME_write_16(self.devID,0x0E,0x0400102E,2)
        time.sleep(1)
        #pyxxusb.VME_write_16(self.devID,0x0E,0x0400102E,0x1400)
        #time.sleep(1)

        #self.set_window_width(0x0E, 0x0400102E,0x015E)  # sets window width to 350 cycles (8.7 microseconds now)
        #self.set_reject(0x0E, 0x0400102E,0x0001)  # sets reject margin
        #self.sendCODE(0x0E, 0x0400102E, 0x1400)  # subtract trigger offset
        #self.sendCODE(0x09,0x0400102E,0x4300) #disable all channels
        #self.sendCODE(0x09,0x0400102E,0x4000) #enable channel 0
        #self.sendCODE(0x09,0x0400102E,0x4001) #enable channel 1
        #self.sendCODE(0x0E,0x0400102E,0x4002) #enable channel 3
        #globset = pyxxusb.xxusb_register_write(self.devID, 0x4, 0x01A0)
        #print(globset)
        self.settingsStatus.config(state='normal')
        self.settingsStatus.delete("1.0",END)
        self.settingsStatus.insert(END,"Settings Written")
        self.settingsStatus.config(background='green')
        self.settingsStatus.update()
        self.settingsStatus.config(state=DISABLED)
        return

    def set_window_width(self,AM, location,width):
        writecheck = pyxxusb.VME_write_16(self.devID, AM, location, 0x1000)
        writecheck2 = pyxxusb.VME_write_16(self.devID, AM, location,width)
        if writecheck < 0 or writecheck2 <0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ Settings failed to set window!')
            self.errorText.config(state=DISABLED)
        return

    def set_offset(self,AM, location,offset):
        writecheck = pyxxusb.VME_write_16(self.devID, AM, location, 0x1100)
        writecheck2 = pyxxusb.VME_write_16(self.devID, AM, location,offset)
        if writecheck < 0 or writecheck2 <0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ Settings failed to set offset!')
            self.errorText.config(state=DISABLED)
        return

    def set_reject(self,AM, location,reject):
        writecheck = pyxxusb.VME_write_16(self.devID, AM, location, 0x1300)
        writecheck2 = pyxxusb.VME_write_16(self.devID, AM, location,reject)
        if writecheck < 0 or writecheck2 <0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ Settings failed to set reject!')
            self.errorText.config(state=DISABLED)
        return

    def sendCODE32(self,AM, location, code):  # function that writes and reads OPCODE for the TDC
        writecheck = pyxxusb.VME_write_32(self.devID, AM, location, code)
        if writecheck < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ Settings failed to set an OPCODE!' + str(code))
            self.errorText.config(state=DISABLED)
        return

    def sendCODE(self,AM, location, code):  # function that writes and reads OPCODE for the TDC
        writecheck = pyxxusb.VME_write_16(self.devID, AM, location, code)
        if writecheck < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ Settings failed to set an OPCODE!' + str(code))
            self.errorText.config(state=DISABLED)
        return

    def drain_FIFO(self):  # clears the buffer
        shortData = pyxxusb.new_intArray(8192)
        loop = 0
        bytes_rec = 1
        while bytes_rec > 0 and loop < 100:
            bytes_rec = pyxxusb.xxusb_usbfifo_read(self.devID, shortData, 8192, 1000)
            loop += 1

    def read_FIFO(self):
        readArray = pyxxusb.new_intArray(8192)  # array must be long if reading 32 or short if reading 16
        numberread = pyxxusb.xxusb_usbfifo_read(self.devID, readArray, 8192, 1000)
        readdata = [np.binary_repr(pyxxusb.intArray_getitem(readArray, i), width=16) for i in range(numberread//2)]
        #data = np.array([])
        #for i in range(len(readdata)):
        #    if pyxxusb.intArray_getitem(readArray,i) != 0xc0c0:
        #        data = np.append(data,np.binary_repr(pyxxusb.intArray_getitem(readArray,i),width=16))
        readdataOut = np.array([str(readdata[i+1]) + str(readdata[i]) for i in np.arange(0, len(readdata)-1, 2)]) #was i+1 and i
        #hexinfo = [hex(pyxxusb.intArray_getitem(readArray, i)) for i in range(numberread // 2)]
        #print(readdata[:20])
        return readdataOut

    def read_buffer(self):  # read what is in the buffer and outputs the array
        readArray = pyxxusb.new_shortArray(8192) #array must be long if reading 32 or short if reading 16
        numberread = pyxxusb.xxusb_bulk_read(self.devID, readArray, 8192, 1000)
        readdata = [np.binary_repr(pyxxusb.shortArray_getitem(readArray, i),width=16) for i in range(numberread//2)]
        #hexinfo = [hex(pyxxusb.longArray_getitem(readArray,i)) for i in range(numberread//2)]
        #print(hexinfo[:100])
        #print(readdata[:100])
        readdataOut = np.array([readdata[i+1] + readdata[i] for i in np.arange(0, len(readdata)-1, 2)]) #was i+1 and i
        #print(readdataOut[:100])
        #self.drain_FIFO()
        return readdataOut

    def DAQ_mode_on(self):
        bytes_written = pyxxusb.xxusb_register_write(self.devID, 1, int(True))
        if bytes_written < 0:
            self.errorText.config(state='normal')
            self.errorText.insert(END, 'DAQ mode on write failed')
            self.errorText.config(state=DISABLED)
        else:
            self.runningDAQ = True
        return

    def DAQ_mode_off(self):
        bytes_written = pyxxusb.xxusb_register_write(self.devID, 1, int(False))
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

    def force_reset(self):
        pyxxusb.VME_register_write(self.devID,1,0x0000)
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
        #time.sleep(3)
        #self.drain_FIFO()
        time.sleep(3)
        finalOutData = self.read_FIFO()
        for i in range(30):
            finalOutData = np.append(finalOutData,self.read_FIFO())
            time.sleep(0.1)
        self.stop_func()
        plotdata1 = np.array([])
        plotdata0 = np.array([])
        plotdata2 = np.array([])
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
        np.savetxt(self.saveDirectory.get(), finalOutData, fmt="%s")
        for i in range(len(tdcdata)):
            if str(tdcdata[i][:5]) == '00001':
                tdcheader = np.append(tdcheader,tdcdata[i])
            if str(tdcdata[i][:6]) == '000000' and str(tdcdata[i]) != '00000000000000000000000000000000':
                if int(tdcdata[i][6:11],2)==0 or int(tdcdata[i][6:11],2)==5:
                    tdcmeasured = np.append(tdcmeasured,tdcdata[i])
            if str(tdcdata[i][:5]) == '00100':
                tdcerror = np.append(tdcerror, tdcdata[i])
            if str(tdcdata[i][:5]) == '00011':
                tdctrailer = np.append(tdctrailer,tdcdata[i])
        #print(tdcheader[:50])
        #print(tdctrailer[:50])
        #print(tdcmeasured[:50])
        headerevent = [int(i[5:27],2) for i in headerglobal]
        headergeo = [int(i[27:],2) for i in headerglobal]
        channel = np.array([int((tdcmeasured[i][6:11]),2) for i in range(len(tdcmeasured))]) #6:11
        measure = np.array([25*int(tdcmeasured[i][11:],2)/1000000 for i in range(len(tdcmeasured))]) #11:
        for i in range(len(tdcmeasured)):
            if channel[i]==0:# and measure[i]>3.2 and measure[i]<3.3:
                plotdata0 = np.append(plotdata0,measure[i])
            if channel[i]==5:# and measure[i]>3.2 and measure[i]<3.3:
                plotdata1 = np.append(plotdata1,measure[i])
            #elif channel[i]==2:
            #    plotdata2 = np.append(plotdata2,measure[i])
        #print(measure[:100])
        #print(channel[:100])
        #print(len(tdcmeasured)/len(finalOutData))
        #print(tdcmeasured[:50])
        #print(plotdata0[:100])
        #print(plotdata1[:100])
        #print('channels')
        #print(channel[:50])
        #print(measure[:50])
        #zerolocations = np.where(channel==0)[0]
        #print(zerolocations[:50])
        #difference=np.array([])
        #for i in np.arange(0,len(zerolocations)-1):
        #    datapoints = np.abs((zerolocations[i+1]-zerolocations[i])-1)
        #    reference = measure[zerolocations[i]]
        #    for j in range(datapoints):
        #        hitdiff = -reference+measure[int(zerolocations[i]+1+j)]
        #        if hitdiff >=.001 and hitdiff <=5:
        #            difference = np.append(difference,hitdiff)
        #print(np.count_nonzero((difference>=0.001) & (difference<=1.0)))
        #print(np.count_nonzero((difference >= 1.0) & (difference <= 2.0)))
        #print(np.count_nonzero((difference >= 2.5) & (difference <= 3.5)))
        print(plotdata0[-50:])
        print(plotdata1[-50:])
        fig = pltex.histogram(x=plotdata0,nbins=10000,labels={'x': 'microseconds', 'y': 'counts'},range_x=[0,10])
        fig.add_histogram(x=plotdata1,nbinsx=10000)
        fig.show()
        fig2 = pltex.scatter(y=channel,x=np.arange(0,len(channel)))
        fig2.show()

#root = Tk()
root = customtkinter.CTk()
my_gui = main_DAQ(root)
root.mainloop()
