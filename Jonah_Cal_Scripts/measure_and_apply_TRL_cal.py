#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 11:55:27 2021

@author: jgollub
"""

import numpy as np
from pathlib import Path
import skrf as rf
from skrf.vi.vna import PNA
from skrf.calibration import OnePort
from cycler import cycler
import matplotlib.pyplot as plt
from datetime import date

import matplotlib.gridspec as gridspec



import matplotlib.pyplot as plt
rf.stylely

# %matplotlib inline
## created calibration class using 

plt.rcParams['axes.prop_cycle'] = cycler(color=['b', 'r', 'g', 'y'])
# plt.rcParams['axes.prop_cycle'] = cycler(color=[.1, , 'r', 'y'])

#%% Measured response from TRL Cal 

cal_folder_name = 'TRL2021-04-23'

measurement_root_folder = Path('/Users/Zaber/Documents/data/scikit_measurements/')
meas_folder = measurement_root_folder / cal_folder_name

THRU_S11 = np.load(meas_folder / 'THRU_S11.ntwk', allow_pickle = True)
THRU_S22 = np.load(meas_folder / 'THRU_S22.ntwk', allow_pickle = True)
THRU_S21 = np.load(meas_folder / 'THRU_S21.ntwk', allow_pickle = True)
THRU_S12 = np.load(meas_folder / 'THRU_S12.ntwk', allow_pickle = True)

REFLECT_S11 = np.load(meas_folder / 'REFLECT_S11.ntwk', allow_pickle = True)
REFLECT_S22 = np.load(meas_folder / 'REFLECT_S22.ntwk', allow_pickle = True)
REFLECT_S21 = np.load(meas_folder / 'REFLECT_S21.ntwk', allow_pickle = True)
REFLECT_S12 = np.load(meas_folder / 'REFLECT_S12.ntwk', allow_pickle = True)

LINE_S11 = np.load(meas_folder / 'LINE_S11.ntwk', allow_pickle = True)
LINE_S22 = np.load(meas_folder / 'LINE_S22.ntwk', allow_pickle = True)
LINE_S21 = np.load(meas_folder / 'LINE_S21.ntwk', allow_pickle = True)
LINE_S12 = np.load(meas_folder / 'LINE_S12.ntwk', allow_pickle = True)

SWITCH_TERMS = np.load(meas_folder / 'SWITCH_TERMS.ntwk', allow_pickle = True)

THRU = rf.two_port_reflect(THRU_S11, THRU_S22)
n_freq = len(THRU.f)
pad_zeros = np.zeros((n_freq, 2, 2)) 

THRU.s[:,0,1] = THRU_S12.s[:,0,0]
THRU.s[:,1,0] = THRU_S21.s[:,0,0]
THRU.z0  = (50+0j)*np.ones((n_freq, 4)) 


REFLECT = rf.two_port_reflect(REFLECT_S11, REFLECT_S22)
REFLECT.s[:,0,1] = REFLECT_S12.s[:,0,0]
REFLECT.s[:,1,0] = REFLECT_S21.s[:,0,0]
REFLECT.z0 = (50+0j)*np.ones((n_freq, 4))

LINE = rf.two_port_reflect(LINE_S11, LINE_S22)
LINE.s[:,0,1] = LINE_S12.s[:,0,0]
LINE.s[:,1,0] = LINE_S21.s[:,0,0]
LINE.z0 = (50+0j)*np.ones((n_freq, 4))

my_ideals = [None, -1, None]

my_measured = [\
               THRU,
               REFLECT,
               LINE,
        ]
    

#%%
    
    
## create a Calibration instance
trl = rf.TRL(\
        measured = my_measured,
        ideals = my_ideals,
        estimate_line = True,
        switch_terms = SWITCH_TERMS,
        )

# run calibration algorithm
trl.run()
# trl_8.run()
# trl=trl_8.coefs_12term()

#%%
# fig, (ax1, ax2)  = plt.subplots(2,1)

#%%

f_start = 8E9
f_stop = 12E9
f_npoints = int(251)

vna = PNA(address ='TCPIP0::10.236.73.132::inst0::INSTR')
vna.reset()
vna.scpi.set_trigger_manual
# vna.scpi.set_delete_all()
# vna.scpi.set_display_on(wnum=1,state=True)


meas_channel = 2


meas_S11 = 'S11'
vna.create_meas(meas_S11,'S11', channel = meas_channel) 
meas_S22 = 'S22'
vna.create_meas(meas_S22,'S22', channel = meas_channel) 
meas_S21 = 'S21'
vna.create_meas(meas_S21,'S21', channel = meas_channel) 
meas_S12 = 'S12'
vna.create_meas(meas_S12,'S12', channel = meas_channel) 

vna.set_frequency_sweep(f_start, 
                        f_stop, 
                        f_npoints, 
                        f_unit = 'Hz',
                        channel = meas_channel, 
                        )



#%%
vna.sweep
# S11
s11 = vna.get_measurement(mname = meas_S11)
print(f'{meas_S11} measured')
filename = meas_folder / ('THRU_' + meas_S11 + '.ntwk')
# rf.write(str(filename), measurement)
# measurement.frequency.units = 'ghz'
# measurement.plot_s_db(ax = ax1, label ='THRU S11')

#S22
s22 = vna.get_measurement(mname = meas_S22)
print(f'{meas_S22} measured')
filename = meas_folder / ('THRU_' + meas_S22 + '.ntwk')
# rf.write(str(filename), measurement)
# measurement.frequency.units = 'ghz'
# measurement.plot_s_db(ax = ax2, label ='THRU S22')

#S21
s21 = vna.get_measurement(mname = meas_S21)
print(f'{meas_S21} measured')
filename = meas_folder / ('THRU_' + meas_S21 + '.ntwk')
# rf.write(str(filename), measurement)
# measurement.frequency.units = 'ghz'
# measurement.plot_s_db(ax = ax1, label ='THRU S21')

#S12
s12 = vna.get_measurement(mname = meas_S12)
print(f'{meas_S12} measured')

filename = meas_folder / ('THRU_' + meas_S12 + '.ntwk')
# rf.write(str(filename), measurement)
# measurement.frequency.units = 'ghz'
# measurement.plot_s_db(ax = ax2, label ='THRU S12')

measurement = rf.two_port_reflect(s11, s22)

measurement.s[:,0,1] = s12.s[:,0,0]
measurement.s[:,1,0] = s21.s[:,0,0]
measurement.z0 = (50+0j)*np.ones((n_freq, 4))

measurement.plot_s_db()

#%%



#%%
# apply it to a dut
dut_raw = measurement
dut_raw.name = 'single element'
dut_corrected = trl.apply_cal(dut_raw)
dut_corrected.name =  dut_raw.name + 'corrected'

# plot results
fig, (ax1,ax2)= plt.subplots(2,1)
dut_corrected.frequency.unit = 'ghz'

dut_corrected.plot_s_deg(ax = ax1)
dut_corrected.plot_s_db(ax = ax2)

# save results
dut_corrected.write_touchstone()
#%%
fig, ax = plt.subplots()
dut_corrected.plot_s_db()
ax.set_ylim(-1,.1)


#%%

RT = rf.RectangularWaveguide(frequency = measurement.frequency, a = 14E-3, b = 0.762E-3, ep_r = 3.45)
left= RT.line(5E-3, 'm',z0 = 50, embed=True)
right = left
 
point_alpha = left.inv ** dut_corrected ** right.inv
alpha = -(1+point_alpha.s[:,0,0]-point_alpha.s[:,1,0])/RT.k0
alpha =alpha/np.amax(np.abs(alpha))

fig = plt.figure(1)
# set up subplot grid
gridspec.GridSpec(2,2)
plt.subplot2grid((2,2), (0,0))
plt.plot(dut_corrected.f, np.abs(alpha))

plt.subplot2grid((2,2), (1,0))
plt.plot(dut_corrected.f, np.angle(alpha))

plt.subplot2grid((2,2), (0,1), colspan = 1, rowspan = 2)
plt.scatter(np.real(alpha), np.imag(alpha))
plt.xlim(-1,1)
plt.ylim(-1,1)