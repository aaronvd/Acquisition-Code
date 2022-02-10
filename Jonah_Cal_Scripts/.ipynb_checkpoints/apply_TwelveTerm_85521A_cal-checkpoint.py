#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 11:55:27 2021

@author: jgollub
"""

import numpy as np
from pathlib import Path
import skrf as rf
from skrf.calibration import OnePort
from cycler import cycler


import matplotlib.pyplot as plt
rf.stylely




# %matplotlib inline
## created calibration class using 

n_freq=101
pad_zeros = np.zeros((n_freq, 2, 2)) 

plt.rcParams['axes.prop_cycle'] = cycler(color=['b', 'r', 'g', 'y'])
# plt.rcParams['axes.prop_cycle'] = cycler(color=[.1, , 'r', 'y'])

#%% Define Ideal Cals from Agilent 85521A Mechanical Cal Kit
###########################################################################
##Ideal Thru

freq = rf.Frequency(8,12, n_freq, 'ghz')

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

measurement_root_folder = Path('/Users/Zaber/Documents/data/scikit_measurements/Mike_Metasurface_3/')
cal_folder_name = 'SOLT2021-04-08'

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
cal = rf.TwelveTerm(\
        ideals = my_ideals,
        measured = my_measured,
        )

# run calibration algorithm
cal.run()
#%%
# apply it to a dut
dut = THRU
dut.name = 'test'
dut_caled = cal.apply_cal(dut)
dut_caled.name =  dut.name + 'corrected'

# plot results
dut_caled.frequency.unit = 'ghz'

# %matplotlib qt5
# fig1, ax =plt.subplots()
dut_caled.plot_s_deg()
# save results
dut_caled.write_touchstone()

#%%
# rf.Network(SHORT_S11.as_posix())
