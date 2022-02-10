# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 12:18:49 2021

@author: lab
"""

import visa
import numpy as np
from struct import unpack
from matplotlib import pyplot as plt
import time

rm = visa.ResourceManager()
rm.list_resources()
scope = rm.open_resource('USB0::0x0699::0x0368::C019640::0::INSTR')
scope_name = scope.query('*IDN?')

scope.write('*RST')
scope.timeout = 25000

def acquire(channel, port):
    try:
        #scope = rm.open_resource(port)
        scope.write('*RST')
        scope.write("DATA:SOURCE " + channel)
        scope.write('DATA:WIDTH 1')
        scope.write('DATA:ENC RPB')
        scope.timeout = 25000
        ymult = float(scope.query('WFMPRE:YMULT?'))
        yzero = float(scope.query('WFMPRE:YZERO?'))
        yoff = float(scope.query('WFMPRE:YOFF?'))
        xincr = float(scope.query('WFMPRE:XINCR?'))
        xdelay = float(scope.query('HORizontal:POSition?'))
        scope.write('CURVE?')
        data = scope.read_raw()
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]
        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))
        Volts = (ADC_wave - yoff) * ymult  + yzero
        Time = np.arange(0, (xincr * len(Volts)), xincr)-((xincr * len(Volts))/2-xdelay)
        return Time,Volts
    except IndexError:
        return 0,0
    
time, volts = acquire('1', 'USB0::0x0699::0x0368::C019640::0::INSTR')

plt.plot(time[:1000], volts[:1000])


scope.close()