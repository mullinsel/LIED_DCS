import numpy as np
import os
import sys

#python package for reading VME address info

class infoVME(self):
    def __init__(self):
        return
    
    def decimalToBinary(self,n):
        return bin(n).replace("0b", "")

    def binaryToDecimal(self,n):
        return int(n,2)

    def write_globalMode(self,buffOpt,mixtBuff,FrceSclrDmp,align32,HdrOpt,DmpOpt,BusReq):
        #BuffOpt can be
        # 0 -> 13k (default)
        # 1 -> 8k
        # 2 -> 4k
        # 3 -> 2k
        # 4 -> 1k
        # 5 -> 512
        # 6 -> 256
        # 7 -> 128
        # 8 -> 64
        # 9 -> Event Count

        #DmpOpt
        # 0 -> no auto dump (default)
        # 1 -> 100ms
        # 2 -> 250ms
        # 3 -> 500ms

        #BusReq from 0-4 when VM-USB not operated as slot 1
        
        buffOptBin = self.decimalToBinary(buffOpt)
        BusReqBin = self.decimalToBinary(BusReq)
        DmpOptBin = self.decimalToBinary(DmpOpt)
        binString = ['0',BusReqBin,DmpOptBin,HdrOpt,align32,FrceSclrDmp,mixtBuff,buffOptBin]
        return binString
    
    def read_firmwareID(binary_read):
        while len(binary_read)!= 32:
            binary_read = ''.join(('0',binary_read))
        month = binaryToDecimal(binary_read[:4])
        year = binaryToDecimal(binary_read[4:8])
        deviceID = binaryToDecimal(binary_read[8:12])
        betaVersion = binaryToDecimal(binary_read[12:16])
        majorRev = binaryToDecimal(binary_read[16:24])
        minorRev = binaryToDecimal(binary_read[24:])
        return month,year,deviceID,betaVersion,majorRev,minorRev

    def read_globalMode(binary_read):
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

    def read_DAQsettings(binary_read):
        while len(binary_read)!= 32:
            binary_read = ''.join(('0',binary_read))
        scalerReadoutFreq = binaryToDecimal(binary_read[:16])
        scalerReadoutPeriod = binaryToDecimal(binary_read[16:24])
        readoutTriggerDelay = binaryToDecimal(binary_read[24:])
        return scalerReadoutFreq,scalerReadoutPeriod,readoutTriggerDelay
