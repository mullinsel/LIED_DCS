import numpy as np
from pyxxusb import pyxxusb

class getData:
    def __init__(self,device,nloop):
        self.mainData = []
        self.device = device
        self.map = multiprocessing.Pool().map
        self.njobs = nloop
        return

    @staticmethod
    def read_data(self):
        self.result = self.map(self.multi_buffer,range(self.njobs))
        return self.result

    @staticmethod
    def multi_buffer(self):
        dataArray = pyxxusb.new_shortArray(8192)
        numberread = pyxxusb.xxusb_bulk_read(self.device, dataArray, 8192, 10)
        readdata = [np.binary_repr(pyxxusb.shortArray_getitem(dataArray, i), width=16) for i in range(numberread // 2)]
        return readdata