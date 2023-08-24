import numpy as np
from pyxxusb import pyxxusb
import multiprocessing

class parse_data:
    def __init__(self,numberOfChannels,binRes,windowSize):
        self.referencehit = 'no reference'
        self.numberChan = numberOfChannels
        self.res = binRes
        self.window = windowSize
        self.histArray = np.zeros((np.max(numberOfChannels)+1, int((1000000 / binRes) * windowSize)))
        return

    def parseForData(self,dataToParse,channels):
        tdcmeasured = np.array([])
        for i in range(len(dataToParse)):
            if str(dataToParse[i][:5]) == '00000' and i - 1 > 0:
                if int(dataToParse[i][6:11], 2) in channels:
                    if (dataToParse[i] + dataToParse[i - 1] != '11000000000000000000000000000000') and (dataToParse[i] + dataToParse[i - 1] !='00000000000000000000000100100000'):
                        tdcmeasured = np.append(tdcmeasured, dataToParse[i] + dataToParse[i - 1])
        return tdcmeasured

    def parse_channel(self,datain):
        return np.array([int((datain[i][6:11]),2) for i in range(len(datain))])

    def parse_measure(self,datain):
        return np.array([(self.res)*int(datain[i][13:],2) for i in range(len(datain))])

    def add_to_hist(self,parsed_buffer_data,channelData):
        if len(parsed_buffer_data) != 0:
            for i in range(len(parsed_buffer_data)):
                dataindex = int(round(parsed_buffer_data[i], -2) // self.res)
                if dataindex < len(self.histArray[int(channelData[i])]):
                    self.histArray[int(channelData[i])][dataindex] += 1
        return

    def main_parse(self,dataIn):
        if len(dataIn) != 0:
            tdcmeasured = self.parseForData(dataIn,self.numberChan)
            channel = self.parse_channel(tdcmeasured)
            measure = self.parse_measure(tdcmeasured)
            self.add_to_hist(measure, channel)
            return self.histArray
        else:
            return

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
        readdata = [np.binary_repr(pyxxusb.intArray_getitem(self.readArray, i),width=16) for i in range(numberread//2)]
        #print(len(readdata))
        #print(readdata[:50])
        #data = np.array([])
        #for i in range(len(readdata)):
        #    if pyxxusb.intArray_getitem(readArray,i) != 0xc0c0:
        #        data = np.append(data,np.binary_repr(pyxxusb.intArray_getitem(readArray,i),width=16))
        #readdataOut = np.array([str(readdata[i+1]) + str(readdata[i]) for i in np.arange(0, len(readdata)-1, 2)]) #was i+1 and i
        #hexinfo = [hex(pyxxusb.intArray_getitem(readArray, i)) for i in range(numberread // 2)]
        return readdata