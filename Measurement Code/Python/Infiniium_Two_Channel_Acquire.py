# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:21:12 2021

@author: smithlab
"""
import sys
sys.path.append('C:/Users/smithlab/Documents/Aaron/Modules/')

import oscope_control as oc
from matplotlib import pyplot as plt
import time

scope = oc.instrument_open("TCPIP0::169.254.221.197::hislip0::INSTR")
time.sleep(5)

oc.scope_initialize(scope, 
            channels=[1,2], 
            N_points=1000, 
            duration=10E-6)
time.sleep(5)

scope.write(':TRIGger:SWEep SINGle')
time.sleep(5)

t1, v1 = oc.scope_read(scope, channel=1)
# time.sleep(5)
t2, v2 = oc.scope_read(scope, channel=2)
fig, ax = plt.subplots(1,1)
ax.plot(t1, v1, t2, v2)
# scope.write(':TRIG:SWE AUTO')
scope.close()






