import numpy as np
import os
import sys

#python package for reading VME address info

class infoVME():
    def __init__():
        return

    def decimalToBinary(n):
        return bin(n).replace("0b", "")

    def binaryToDecimal(n):
        return int(n,2)

    def firmwareID_read(binary_read):
        while len(binary_read)!= 32:
            binary_read = ''.join(('0',binary_read))
        month = binaryToDecimal(binary_read[:4])
        year = binaryToDecimal(binary_read[4:8])
        deviceID = binaryToDecimal(binary_read[8:12])
        betaVersion = binaryToDecimal(binary_read[12:16])
        majorRev = binaryToDecimal(binary_read[16:24])
        minorRev = binaryToDecimal(binary_read[24:])
        return month,year,deviceID,betaVersion,majorRev,minorRev

    def globalMode_read(binary_read):
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

    def DAQsettings_read(binary_read):
        while len(binary_read)!= 32:
            binary_read = ''.join(('0',binary_read))
        scalerReadoutFreq = binaryToDecimal(binary_read[:16])
        scalerReadoutPeriod = binaryToDecimal(binary_read[16:24])
        readoutTriggerDelay = binaryToDecimal(binary_read[24:])
        return scalerReadoutFreq,scalerReadoutPeriod,readoutTriggerDelay
