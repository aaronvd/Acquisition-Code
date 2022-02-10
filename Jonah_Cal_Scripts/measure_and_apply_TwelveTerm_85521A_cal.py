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
from datetime import date

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
rf.stylely


# %matplotlib inline
## created calibration class using 

n_freq=251
freq_low = 8 # Ghz
freq_high = 12 # GHz

pad_zeros = np.zeros((n_freq, 2, 2)) 

plt.rcParams['axes.prop_cycle'] = cycler(color=['b', 'r', 'g', 'y'])
# plt.rcParams['axes.prop_cycle'] = cycler(color=[.1, , 'r', 'y'])

#%% Define Ideal Cals from Agilent 85521A Mechanical Cal Kit
###########################################################################
##Ideal Thru

freq = rf.Frequency(freq_low, freq_high, n_freq, 'ghz')

base_ntwk = rf.Freespace(freq, z0=50 +0j)

THRU_85521A = base_ntwk.line(115.881,unit ='ps')
THRU_85521A.z0 = (50+0j)*np.ones((n_freq, 4)) 

fig, ax = plt.subplots()
THRU_85521A.plot_s_re(axis =ax, linewidth= 2)
THRU_85521A.plot_s_im(axis =ax, linestyle='--', linewidth= 2)
ax.set_title('Idela THRU')

#%% Ideal Open

OPEN_S11_85521A = base_ntwk.delay_load(1,31.832, unit = 'ps')
OPEN_S22_85521A = OPEN_S11_85521A 

OPEN_85521A = rf.two_port_reflect(OPEN_S11_85521A, OPEN_S22_85521A)
OPEN_85521A.z0 =  (50+0j)*np.ones((n_freq, 4)) 

fig, ax = plt.subplots()
OPEN_85521A.plot_s_re(axis =ax, linewidth= 2)
OPEN_85521A.plot_s_im(axis =ax, linestyle='--', linewidth= 2)

ax.set_title('Ideal OPEN')

#%% Ideal Short

SHORT_S11_85521A = base_ntwk.delay_load(-1, 30.581, unit = 'ps')


SHORT_S22_85521A = SHORT_S11_85521A

SHORT_85521A = rf.two_port_reflect(SHORT_S11_85521A,SHORT_S22_85521A)
SHORT_85521A.z0 =  (50+0j)*np.ones((n_freq, 4)) 

fig, ax = plt.subplots()
SHORT_85521A.plot_s_re(axis =ax, linewidth= 2)
SHORT_85521A.plot_s_im(axis =ax, linestyle='--', linewidth= 2)

ax.set_title('Ideal SHORT')

#%% Ideal Load
LOAD_S11_85521A = base_ntwk.delay_load(0,0)

LOAD_85521A = rf.two_port_reflect(LOAD_S11_85521A)
LOAD_85521A.z0 = (50+0j)*np.ones((n_freq, 4)) 

fig, ax = plt.subplots()
LOAD_85521A.plot_s_re(axis =ax, linewidth= 2)
LOAD_85521A.plot_s_im(axis =ax, linestyle='--', linewidth= 2)

ax.set_title('Ideal LOAD')

#%%


#list of Network types, holding 'ideal' responses ORDER MUST BE SAME AS THOSE ENTERED BELOW IN MEASUREMENTS
my_ideals = [\
        SHORT_85521A,
        OPEN_85521A,
        LOAD_85521A,
        THRU_85521A,
        ]
    
#%% Measured response from Mechanical Cal (85521A)

measurement_root_folder = Path('/Users/Zaber/Documents/data/scikit_measurements/')
cal_folder_name = '2021-04-23_SOLT'

meas_folder = measurement_root_folder / cal_folder_name


SHORT_S11 = np.load(meas_folder / 'SHORT_S11.ntwk', allow_pickle = True)
SHORT_S22 = np.load(meas_folder / 'SHORT_S22.ntwk', allow_pickle = True)
OPEN_S11 = np.load(meas_folder / 'OPEN_S11.ntwk', allow_pickle = True)
OPEN_S22 = np.load( meas_folder / 'OPEN_S22.ntwk', allow_pickle = True)
LOAD_S11 = np.load(meas_folder / 'LOAD_S11.ntwk', allow_pickle = True)
LOAD_S22 = np.load(meas_folder / 'LOAD_S22.ntwk', allow_pickle = True)

THRU_S11 = np.load(meas_folder / 'THRU_S11.ntwk', allow_pickle = True)
THRU_S22 = np.load(meas_folder / 'THRU_S22.ntwk', allow_pickle = True)
THRU_S21 = np.load(meas_folder / 'THRU_S21.ntwk', allow_pickle = True)
THRU_S12 = np.load(meas_folder / 'THRU_S12.ntwk', allow_pickle = True)
 


SHORT = rf.two_port_reflect(SHORT_S11,SHORT_S22)
SHORT.z0  = (50+0j)*np.ones((n_freq, 4))
 

OPEN = rf.two_port_reflect(OPEN_S11,OPEN_S22)
OPEN.z0  = (50+0j)*np.ones((n_freq, 4))
 
LOAD = rf.two_port_reflect(LOAD_S11,LOAD_S22)
LOAD.z0  = (50+0j)*np.ones((n_freq, 4))

THRU = rf.two_port_reflect(THRU_S11, THRU_S22)
THRU.s[:,0,1] = THRU_S12.s[:,0,0]
THRU.s[:,1,0] = THRU_S21.s[:,0,0]

THRU.z0  = (50+0j)*np.ones((n_freq, 4))

# my_measured_ntwk = [\
#         rf.Network(SHORT_S11.as_posix()),
#         rf.Network(SHORT_S22.as_posix()),
#         rf.Network(OPEN_S11.as_posix()),
#         rf.Network(OPEN_S22.as_posix()),
#         rf.Network(LOAD_S11.as_posix()),
#         rf.Network(LOAD_S22.as_posix()),
#         rf.Network(THRU_S21.as_posix()),
#         rf.Network(THRU_S12.as_posix()),
#         ]
    
my_measured = [\
               SHORT,
               OPEN,
               LOAD,
               THRU
        ]
    

## create a Calibration instance
cal_SOLT = rf.TwelveTerm(\
        ideals = my_ideals,
        measured = my_measured,
        )

# run calibration algorithm
cal_SOLT.run()
#%%

f_start = freq_low*1E9
f_stop = freq_high*1E9
f_npoints = n_freq

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

#%% apply it to a dut
dut_raw = measurement
dut_raw.name = 'empty_SIW_test_board'
dut_corrected = cal_SOLT.apply_cal(dut_raw)
dut_corrected.name =  dut_raw.name + '_corrected'

# plot results
fig, (ax1,ax2)= plt.subplots(2,1)
dut_corrected.frequency.unit = 'ghz'

dut_corrected.plot_s_deg(ax = ax1)
dut_corrected.plot_s_db(ax = ax2)
ax2.set_ylim(-10,.1)

# save results
folder = Path('/Users/Zaber/Documents/data/scikit_measurements/SIW_analysis')
dut_corrected.write_touchstone(str(folder),dut_corrected.name)
#%%
fig, ax = plt.subplots()
dut_corrected.plot_s_db()
ax.set_ylim(-1,.1)




#%%
# rf.Network(SHORT_S11.as_posix())
