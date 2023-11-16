import plotly.express as pltex
import numpy as np
from tkinter import *
import time
from pyxxusb import pyxxusb
import customtkinter
from settingsConfig import DAQSetting
from engineDAQ import parse_data
from engineDAQ import read_engine
#from engineDAQ import motor_engine
#import multiprocessing
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading
customtkinter.set_default_color_theme("C:\\Users\cbonline\Documents\PycharmProjects\LIED_DCS\custom-tktheme.json")

class main_DAQ:
    def __init__(self,master):
        master.title("DAQ GUI") #set window title
        master.config(height=800,width=1200)
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
        customtkinter.CTkLabel(master,text='Save Directory',font=('Helvetica',30)).place(x=20,y=430)
        self.saveDirectory = Entry(master)
        self.saveDirectory.insert(END,'test.txt')
        self.saveDirectory.place(x=20,y=600)
        customtkinter.CTkLabel(master, text='Config Directory', font=('Helvetica', 20)).place(x=900, y=200)
        self.configDirectory = Entry(master)
        self.configDirectory.insert(END,'configSetup.txt')
        self.configDirectory.place(x=900,y=300)
        self.startButton = customtkinter.CTkButton(master,text='Start',command= lambda: threading.Thread(target=self.start_func).start(),height=40,width=80)
        self.startButton.place(x=200,y=60)
        self.stopButton = customtkinter.CTkButton(master,text="Stop",command=self.stop_func,height=40,width=80)
        self.stopButton.place(x=300,y=60)
        self.connectButton = customtkinter.CTkButton(master,text="Connect",command= lambda: threading.Thread(target=self.connect_func).start(),height=40,width=80)
        self.connectButton.place(x=200,y=20)
        self.disconnectButton = customtkinter.CTkButton(master,text='Disconnect',command=self.disconnect_func,height=40,width=80)
        self.disconnectButton.place(x=300,y=20)
        self.ionModeButton = customtkinter.CTkButton(master,text='Setup Ion Mode',command= lambda: self.setup_config('ionMode.txt'),height=40,width=80)
        self.ionModeButton.place(x=850,y=80)
        self.electronModeButton = customtkinter.CTkButton(master,text='Setup Electron Mode',command= lambda: self.setup_config('electronMode.txt'),height=40,width=80)
        self.electronModeButton.place(x=700,y=80)
        customtkinter.CTkLabel(master,text='Settings',font=('Helvetica',30)).place(x=800,y=20)
        self.writeSettings = customtkinter.CTkButton(master,text="Write settings from config file",command= lambda: self.setup_config(self.configDirectory.get()),height=40,width=80)
        self.writeSettings.place(x=750,y=150)
        customtkinter.CTkLabel(master,text='Errors',font=('Helvetica',30)).place(x=900,y=440)
        self.errorText = Text(master,width=30,height=10)
        self.errorText.insert(END,"No Errors")
        self.errorText.place(x=900,y=625)
        self.settingsStatus = Text(master,background='red',height=2,width=20)
        self.settingsStatus.insert(END,'Settings Unwritten')
        self.settingsStatus.place(x=900,y=330)
        self.settingsStatus.config(state=DISABLED)
        customtkinter.CTkLabel(master, text='Collection runtime(s)', font=('Helvetica', 20)).place(x=20, y=130)
        self.runTime = Entry(master)
        self.runTime.insert(END,'100')
        self.runTime.place(x=20,y=225)
        self.motorStepSize = Entry(master)
        self.motorStepSize.insert(END,'1')
        self.motorStepSize.place(x=20,y=400)
        customtkinter.CTkLabel(master, text='Waveplate step size(deg)', font=('Helvetica', 20)).place(x=20, y=280)
        self.numberOfRuns = Entry(master)
        self.numberOfRuns.insert(END,'1')
        self.numberOfRuns.place(x=20,y=300)
        customtkinter.CTkLabel(master, text='Number of collections(int)', font=('Helvetica', 20)).place(x=20, y=200)
        self.motorStarting = Entry(master)
        self.motorStarting.insert(END,'0')
        self.motorStarting.place(x=20,y=500)
        customtkinter.CTkLabel(master, text='Waveplate Start Position(deg)', font=('Helvetica', 20)).place(x=20, y=360)
        self.readSize = int(4096*255) #524288
        customtkinter.CTkLabel(master,text="Run Time(s)").place(x=400,y=30)
        self.runprogress = customtkinter.CTkProgressBar(self.master,orientation='horizontal')
        self.runprogress.place(x=400,y=50)
        self.runprogress.set(0.0)
        self.fig = Figure(figsize=(4,4),dpi=100)
        self.datay = [i ** 2 for i in range(101)]
        self.plot_function(self.datay)
        self.progress = 0.0

    def plot_function(self,dataToPlot):
        self.fig.clf()
        plot1 = self.fig.add_subplot(111)
        plot1.plot(dataToPlot)
        canvas = FigureCanvasTkAgg(self.fig,master=self.master)
        #toolbar = NavigationToolbar2Tk(canvas, self.master)
        canvas.draw()
        canvas.get_tk_widget().place(x=400,y=200)
        #toolbar = NavigationToolbar2Tk(canvas,self.master)
        #toolbar.update()
        #canvas.get_tk_widget().place(x=10,y=800)

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
        #for i in range(10):
        #    self.plot_function([j*j for j in range(i)])
        #    progress = self.progress + 0.1
        #    self.runprogress.set(progress)
        #    self.progress = progress
        #    self.master.update()
        #    time.sleep(3)
        self.devID = pyxxusb.xxusb_serial_open('VM0403')
        time.sleep(1)
        self.connectedText.config(state='normal')
        self.connectedText.configure(background='green')
        self.connectedText.delete("1.0",END)
        self.connectedText.insert(END,str(self.devID))
        self.connectedText.update()
        self.connectedText.config(state=DISABLED)

    def disconnect_func(self):
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

    def save_data(self,datain):
        #file1 = open("test.txt","a")
        #for i in datain:
        #    file1.write(str(i)+"\n")
        #file1.close()
        with open(self.saveDirectory.get(), 'a') as f:
            if np.any(datain):
                np.savetxt(f,datain)
                f.write("\n")
        f.close()
        return

    def run_sequence(self):
        self.runningDAQ=True
        #rundata = np.zeros((np.max(self.settings.channels)+1, int((1000000 / self.settings.resolution) * self.settings.window)))
        self.totalRunTime = int(self.runTime.get())
        #self.settings.clear_TDC_buffer()
        #self.settings.VME_bufferdump()
        self.settings.DAQ_mode_on()
        self.starttime = time.time()
        while self.runningDAQ:
            if (time.time()-self.starttime) > 4:
                toparse = self.mainengineData.read_FIFO()
                self.save_data(np.array(toparse))
                #self.mainengineParse.main_parse(toparse)
                #self.plot_function(rundata)
                #timepercent = (time.time() - self.starttime - 4) / self.totalRunTime
                #self.runprogress.set(timepercent)
                #multidataout = pool.map(self.mainengineParse.main_parse,np.array_split(toparse,10))
                #for i in range(10): #the number of split chunks to multiprocess
                #    for j in range(10): #number of channels
                #        rundata[j] += multidataout[i][j]
            else:
                dump = self.mainengineData.read_FIFO()
            if (time.time()-self.starttime - 4) > self.totalRunTime:
                self.finaltime = time.time()-self.starttime - 4
                self.runningDAQ = False
                break
        self.stop_func()
        return

    def start_func(self):  # start/run read TDC
        #initialize the engines
        self.mainengineParse = parse_data(self.settings.channels,self.settings.resolution,8)
        self.mainengineData = read_engine(self.devID,self.readSize)
        #self.motor = motor_engine()
        self.runningText.config(state='normal')
        self.runningText.configure(background='green')
        self.runningText.delete("1.0", END)
        self.runningText.insert(END,'DAQ is running')
        self.runningText.update()
        self.runningText.config(state=DISABLED)
        self.motorStepSize.config(state=DISABLED)
        self.numberOfRuns.config(state=DISABLED)
        self.runTime.config(state=DISABLED)
        self.motorStarting.config(state=DISABLED)

        #maindata = np.zeros((np.max(self.settings.channels)+1, int((1000000 / 100) * 8)))
        #waveplateposition = 1#float(self.motorStarting.get())
        #self.motor.move_motor(waveplateposition)
        for i in range(int(self.numberOfRuns.get())):
            #headerArray = np.array(['runNumber',i,'waveplateLocation',waveplateposition,'binRes',self.settings.resolution,'channels',str(self.settings.channels),'windowSize',self.settings.window,'offset',self.settings.offset,'runtime',self.runTime.get()])
            self.run_sequence()
            #time.sleep(0.3)
            #self.save_data(rundata)
            #time.sleep(0.3)
            #waveplateposition += float(self.motorStepSize.get())
            #self.motor.move_motor(waveplateposition)
        #maindata = rundata
        #reprate = 3
        #totalhits = 18
        #totaltime = round(self.finaltime,2)
        #counter9 = np.sum(maindata[9])
        #counter5 = np.sum(maindata[5])
        #counter2 = np.sum(maindata[2])
        #counter = counter9 + counter5 #+ counter2
        #print('percent total data made to computer')
        #print((counter)/(totaltime*reprate*1000*totalhits))
        #print(counter9/(totaltime*reprate*1000*9))
        #print(counter5 / (totaltime * reprate * 1000 * 9))
        #print(counter2 / (totaltime * reprate * 1000 * 8))

        #print('Total time')
        #print(totaltime)
        #print('average speed in MB/s')
        #print(((counter)*4)/(self.finaltime*1000000))
        #print('number of bytes')
        #print((counter)*4)
        #print('expected number of bytes')
        #print((totaltime*reprate*1000*totalhits)*4)
        #fig = pltex.line(y=maindata[9], x=(1/10000)*np.arange(0,len(maindata[9])))
        #fig.add_scatter(y=maindata[5],x=(1/10000)*np.arange(0,len(maindata[5])))
        #fig.add_scatter(y=maindata[2],x=(1/10000)*np.arange(0,len(maindata[2])))
        #fig.show()

if __name__ == '__main__':
    root = customtkinter.CTk()
    my_gui = main_DAQ(root)
    root.mainloop()
