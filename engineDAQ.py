import numpy as np
from pyxxusb import pyxxusb
from pylablib.devices import Thorlabs
import time

class parse_data:
    def __init__(self,numberOfChannels,binRes,windowSize):
        self.referencehit = 'no reference'
        self.numberChan = numberOfChannels
        self.res = binRes
        self.window = windowSize
        self.histArray = np.zeros((np.max(numberOfChannels)+1, int((1000000 / binRes) * windowSize)))
        return

    def parseForData(self,dataToParse,):
        for i in range(len(dataToParse)):
            datahit = dataToParse[i]
            hitchannel = int(datahit[6:11],2)
            hitmeasure = self.res*int(datahit[11:],2)
            if hitchannel == 1:
                self.referencehit = hitmeasure
            if hitchannel != 1 and self.referencehit != 'no reference':
                dataindex = int(round(np.abs(hitmeasure - self.referencehit), -2) // self.res)
                self.histArray[int(hitchannel)][dataindex] += 1
        return

    def parse_channel(self,datain):
        return np.array([int((datain[i][6:11]),2) for i in range(len(datain))])

    def parse_measure(self,datain):
        return np.array([(self.res)*int(datain[i][13:],2) for i in range(len(datain))])

    def add_to_hist(self,parsed_buffer_data,channelData):
        if len(parsed_buffer_data) != 0:
            for i in range(len(parsed_buffer_data)):
                if channelData[i] == 1:
                    self.referencehit = parsed_buffer_data[i]
                if channelData[i] != 1 and self.referencehit != 'no reference':
                    dataindex = int(round(np.abs(parsed_buffer_data[i]-self.referencehit), -2) // self.res)
                    if dataindex < len(self.histArray[int(channelData[i])]):
                        self.histArray[int(channelData[i])][dataindex] += 1
        return

    def main_parse(self,dataIn):
        filtereddata = np.array([])
        if len(dataIn) != 0:
            for i in range(len(dataIn)):
                if dataIn[i] in [160,288,32,64]:
                    chunk = np.binary_repr(dataIn[i],width=16)+np.binary_repr(dataIn[i-1],width=16)
                    filtereddata = np.append(filtereddata,chunk)
            self.parseForData(filtereddata)
            #channel = self.parse_channel(tdcmeasured)
            #measure = self.parse_measure(tdcmeasured)
            #self.add_to_hist(measure, channel)
        return self.histArray

    def multiparse(self,dataToParse):
        histArray =  np.zeros((np.max(9)+1, int((1000000 / 100) * 8)))
        tdcmeasured = np.array([])
        for i in range(len(dataToParse)):
            if str(dataToParse[i][:5]) == '00000' and i - 1 > 0:
                if int(dataToParse[i][6:11], 2) in [1,9]:
                    chunk = dataToParse[i] + dataToParse[i - 1]
                    if (chunk != '11000000000000000000000000000000') and (chunk !='00000000000000000000000100100000'):
                        tdcmeasured = np.append(tdcmeasured, chunk)

        channel = np.array([int((tdcmeasured[i][6:11]), 2) for i in range(len(tdcmeasured))])
        measure = np.array([(100)*int(tdcmeasured[i][13:],2) for i in range(len(tdcmeasured))])

        if len(measure) != 0:
            for i in range(len(measure)):
                dataindex = int(round(measure[i], -2) // 100)
                if dataindex < len(histArray[int(channel[i])]):
                    histArray[int(channel[i])][dataindex] += 1

        return histArray

class read_engine:
    def __init__(self,device,readsize):
        self.devID = device
        self.readSize = readsize
        self.readArray = pyxxusb.new_intArray(int(self.readSize))

    def read_data(self):
        numberread = pyxxusb.xxusb_bulk_read(self.devID, self.readArray, int(self.readSize), 1000)
        readdata = [np.binary_repr(pyxxusb.shortArray_getitem(self.readArray, i), width=16) for i in range(numberread // 2)]
        #print(len(readdata))
        #print(readdata[:50])
        return readdata

    def read_FIFO(self):
        numberread = pyxxusb.xxusb_usbfifo_read(self.devID, self.readArray, int(self.readSize), 1000)
        readdata = [pyxxusb.intArray_getitem(self.readArray, i) for i in range(numberread//2)]
        #binaryrep = [np.binary_repr(i,width=16) for i in readdata]
        #print(readdata[:50])
        #data = np.array([])
        #for i in range(len(readdata)):
        #    if pyxxusb.intArray_getitem(readArray,i) != 0xc0c0:
        #        data = np.append(data,np.binary_repr(pyxxusb.intArray_getitem(readArray,i),width=16))
        #readdataOut = np.array([str(readdata[i+1]) + str(readdata[i]) for i in np.arange(0, len(readdata)-1, 2)]) #was i+1 and i
        #hexinfo = [hex(pyxxusb.intArray_getitem(readArray, i)) for i in range(numberread // 2)]
        return readdata

    def drain_FIFO(self):  # clears the buffer
        shortData = pyxxusb.new_intArray(262144)
        loop = 0
        bytes_rec = 1
        while bytes_rec > 0 and loop < 100:
            bytes_rec = pyxxusb.xxusb_usbfifo_read(self.devID, shortData, 262144, 1000)
            loop += 1


class motor_engine:
    def __init__(self): #motor is in units of meters but only has mm in travel distance
        self.motorID = Thorlabs.list_kinesis_devices()[0][0]
        self.motor = Thorlabs.KinesisMotor(str(self.motorID),scale="stage")
        position = self.motor.get_position()
        return

    def move_motor(self,deg):
        self.motor.move_to(deg)
        time.sleep(1.5)
        position = self.motor.get_position()
        print('End of collection time, moving motor to:')
        print(round(position,6))
        return
