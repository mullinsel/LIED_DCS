import numpy as np
from pyxxusb import pyxxusb
import time

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
            #print(len(tdcmeasured))
            #print((len(tdcmeasured)*2)/len(dataIn))
            channel = self.parse_channel(tdcmeasured)
            measure = self.parse_measure(tdcmeasured)
            self.add_to_hist(measure, channel)

class read_engine:
    def __init__(self,device,readsize):
        self.devID = device
        self.readSize = readsize
        self.readArray = pyxxusb.new_shortArray(int(self.readSize))

    def read_data(self):
        numberread = pyxxusb.xxusb_bulk_read(self.devID, self.readArray, int(self.readSize), 1000)
        readdata = [np.binary_repr(pyxxusb.shortArray_getitem(self.readArray, i), width=16) for i in range(numberread // 2)]
        #print(len(readdata))
        #print(readdata[:50])
        return readdata