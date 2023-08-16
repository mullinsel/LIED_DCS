import numpy as np

class parse_data:
    def __init__(self):
        self.referencehit = 'no reference'
        return

    def parseForData(self,dataToParse,channels):
        tdcmeasured = np.array([])
        for i in range(len(dataToParse)):
            if str(dataToParse[i][:5]) == '00000' and i - 1 > 0:
                if int(dataToParse[i][6:11], 2) in channels:
                    tdcmeasured = np.append(tdcmeasured, dataToParse[i] + dataToParse[i - 1])
        return tdcmeasured

    def parse_channel(self,datain):
        return np.array([int((datain[i][6:11]),2) for i in range(len(datain))])

    def parse_measure(self,datain):
        return np.array([(100)*int(datain[i][13:],2) for i in range(len(datain))])

    def main_parse_data(self,dataToParse):
        difference = np.array([])
        if len(dataToParse) != 0:
            tdcmeasured = self.parseForData(dataToParse,[0,2,5,9])
            channel = self.parse_channel(tdcmeasured)#np.array([int((tdcmeasured[i][6:11]),2) for i in range(len(tdcmeasured))]) #6:11
            measure = self.parse_measure(tdcmeasured)#np.array([(100)*int(tdcmeasured[i][13:],2) for i in range(len(tdcmeasured))]) #11:  data in microseconds # 11 is the index for 25 ps mode (21 bits) 13 is the index for 100ps (19 bits)
            for i in range(len(tdcmeasured)):
                if channel[i] == 0:
                    self.referencehit = measure[i]
                if self.referencehit != 'no reference':
                    difference = np.append(difference,np.abs(self.referencehit-measure[i]))
            return difference
        else:
            return []