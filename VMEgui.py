import plotly.express as pltex
import numpy as np
from tkinter import *
import time
from pyxxusb import pyxxusb
import customtkinter
from settingsConfig import DAQSetting
from engineDAQ import parse_data
from engineDAQ import read_engine
from engineDAQ import motor_engine
import threading
import multiprocessing

customtkinter.set_default_color_theme("C:\\Users\cbonline\Documents\PycharmProjects\LIED_DCS\custom-tktheme.json")
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
        customtkinter.CTkLabel(master, text='Config Directory', font=('Helvetica', 20)).place(x=750, y=200)
        self.configDirectory = Entry(master)
        self.configDirectory.insert(END,'configSetup.txt')
        self.configDirectory.place(x=750,y=225)
        self.startButton = customtkinter.CTkButton(master,text='Start',command=self.start_func,height=40,width=80)
        self.startButton.place(x=200,y=60)
        self.stopButton = customtkinter.CTkButton(master,text="Stop",command=self.stop_func,height=40,width=80)
        self.stopButton.place(x=300,y=60)
        self.connectButton = customtkinter.CTkButton(master,text="Connect",command=self.connect_func,height=40,width=80)
        self.connectButton.place(x=200,y=20)
        self.disconnectButton = customtkinter.CTkButton(master,text='Disconnect',command=self.disconnect_func,height=40,width=80)
        self.disconnectButton.place(x=300,y=20)
        self.ionModeButton = customtkinter.CTkButton(master,text='Setup Ion Mode',command= lambda: self.setup_config('ionMode.txt'),height=40,width=80)
        self.ionModeButton.place(x=850,y=80)
        self.electronModeButton = customtkinter.CTkButton(master,text='Setup Electron Mode',command= lambda: self.setup_config('electronMode.txt'),height=40,width=80)
        self.electronModeButton.place(x=700,y=80)
        self.resetButton = customtkinter.CTkButton(master,text='Reset and clear',command=self.force_reset,height=40,width=80)
        self.resetButton.place(x=750,y=300)
        customtkinter.CTkLabel(master,text='Settings',font=('Helvetica',30)).place(x=800,y=20)
        self.writeSettings = customtkinter.CTkButton(master,text="Write settings from config file",command= lambda: self.setup_config(self.configDirectory.get()),height=40,width=80)
        self.writeSettings.place(x=750,y=150)
        customtkinter.CTkLabel(master,text='Errors',font=('Helvetica',30)).place(x=800,y=480)
        self.errorText = Text(master,width=30,height=10)
        self.errorText.insert(END,"No Errors")
        self.errorText.place(x=705,y=525)
        self.settingsStatus = Text(master,background='red',height=2,width=20)
        self.settingsStatus.insert(END,'Settings Unwritten')
        self.settingsStatus.place(x=750,y=250)
        self.settingsStatus.config(state=DISABLED)
        customtkinter.CTkLabel(master, text='Runtime(s)', font=('Helvetica', 20)).place(x=20, y=200)
        self.runTime = Entry(master)
        self.runTime.insert(END,'101')
        self.runTime.place(x=20,y=225)
        self.readSize = int(4096*255) #524288

    def close_window(self):
        self.stop_func()
        self.disconnect_func()
        self.master.destroy()
        return

    def write_error(self):
        self.errorText.config(state='normal')
        self.errorText.configure(background='red')
        self.errorText.update()
        self.errorText.delete("1.0", END)
        self.errorText.insert(END, 'Error')
        self.errorText.config(state=DISABLED)
        return

    def setup_config(self,configdirectory):
        self.settings = DAQSetting(self.devID, configdirectory)
        time.sleep(0.3)
        #self.settings.reset_TDC()
        #time.sleep(0.3)
        #self.settings.reset_VME()
        #time.sleep(0.3)
        TDCcheck = self.settings.setup_TDC()
        time.sleep(0.3)
        VMEcheck = self.settings.setup_VME()
        if VMEcheck > 0 and TDCcheck > 0:
            mode = 'From file'
            if configdirectory == 'electronMode.txt':
                mode = 'Electron Mode'
            if configdirectory == 'ionMode.txt':
                mode = 'Ion Mode'
            self.settingsStatus.config(state='normal')
            self.settingsStatus.delete("1.0", END)
            self.settingsStatus.insert(END, "Settings Written for " + mode)
            self.settingsStatus.config(background='green')
            self.settingsStatus.update()
            self.settingsStatus.config(state=DISABLED)
        else:
            self.write_error()
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
        self.force_reset()
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
        #self.settings.clear_TDC_buffer()
        #self.settings.VME_bufferdump()
        time.sleep(0.3)
        dump=self.mainengineData.read_FIFO()
        time.sleep(0.3)
        self.settings.DAQ_mode_off()
        time.sleep(0.3)
        dump = self.mainengineData.read_FIFO()
        time.sleep(0.3)
        dump = self.mainengineData.read_FIFO()
        time.sleep(0.3)
        self.runningDAQ = False
        self.runningText.config(state='normal')
        self.runningText.configure(background='red')
        self.runningText.update()
        self.runningText.delete("1.0", END)
        self.runningText.insert(END, 'DAQ is not running')
        self.runningText.config(state=DISABLED)

    def force_reset(self):
        if self.devID != '':
            resetTDCcheck = self.settings.reset_TDC()
            resetVMEcheck = self.settings.reset_VME()
            if resetVMEcheck < 0 or resetTDCcheck < 0 :
                self.write_error()
            self.settingsStatus.config(state='normal')
            self.settingsStatus.delete(1.0,END)
            self.settingsStatus.insert(END, 'Settings Unwritten')
            self.settingsStatus.configure(background='red')
            self.settingsStatus.config(state=DISABLED)
        return

    def save_data(self,datain):
        file1 = open("test.txt","a")
        for i in datain:
            file1.write(str(i)+"\n")
        file1.close()
        return

    def run_sequence(self):
        self.runningDAQ=True
        rundata = np.zeros((np.max(self.settings.channels)+1, int((1000000 / self.settings.resolution) * self.settings.window)))
        self.totalRunTime = int(self.runTime.get())
        self.settings.clear_TDC_buffer()
        self.settings.DAQ_mode_on()
        self.starttime = time.time()
        pool = multiprocessing.Pool(10)

        while self.runningDAQ:
            toparse = self.mainengineData.read_FIFO()
            multidataout = pool.map(self.mainengineParse.main_parse,np.array_split(toparse,10))
            for i in range(10): #the number of split chunks to multiprocess
                for j in range(10): #number of channels
                    rundata[j] += multidataout[i][j]
            if time.time()-self.starttime > self.totalRunTime:
                self.finaltime = time.time()-self.starttime
                self.runningDAQ = False
                break
        self.stop_func()
        return rundata

    def start_func(self):  # start/run read TDC
        #initialize the engines
        self.mainengineParse = parse_data(self.settings.channels,self.settings.resolution,8)
        self.mainengineData = read_engine(self.devID,self.readSize)
        self.mainengineMotor = motor_engine()
        self.runningText.config(state='normal')
        self.runningText.configure(background='green')
        self.runningText.delete("1.0", END)
        self.runningText.insert(END,'DAQ is running')
        self.runningText.update()
        self.runningText.config(state=DISABLED)
        #maindata = np.zeros((np.max(self.settings.channels)+1, int((1000000 / self.settings.resolution) * self.settings.window)))
        rundata = self.run_sequence()
        maindata = rundata
        reprate = 3
        totalhits = 26
        totaltime = round(self.finaltime,2)
        counter9 = np.sum(maindata[9])
        counter5 = np.sum(maindata[5])
        counter2 = np.sum(maindata[2])
        counter = counter9 + counter5 + counter2
        print('percent total data made to computer')
        print((counter)/(totaltime*reprate*1000*totalhits))
        print(counter9/(totaltime*reprate*1000*9))
        print(counter5 / (totaltime * reprate * 1000 * 9))
        print(counter2 / (totaltime * reprate * 1000 * 8))

        print('Total time')
        print(totaltime)
        print('average speed in MB/s')
        print(((counter)*4)/(self.finaltime*1000000))
        print('number of bytes')
        print((counter)*4)
        print('expected number of bytes')
        print((totaltime*reprate*1000*totalhits)*4)
        fig = pltex.line(y=maindata[9], x=(1/10000)*np.arange(0,len(maindata[9])))
        fig.add_scatter(y=maindata[5],x=(1/10000)*np.arange(0,len(maindata[5])))
        fig.add_scatter(y=maindata[2],x=(1/10000)*np.arange(0,len(maindata[2])))
        fig.show()

if __name__ == '__main__':
    root = customtkinter.CTk()
    my_gui = main_DAQ(root)
    root.mainloop()
